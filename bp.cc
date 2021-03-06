/**
Author: Anurag Gautam (10133)
A simple implementation of Bimodal Branch Prediction
*/
#include <iostream>
#include <fstream>
#include "time.h"
#include "pin.H"
#include "instlib.H"
using namespace INSTLIB;

//Define the limit here
const long LIMIT = 1000000000;
const UINT16 LRU_LIMIT = 2048;

//Table Parameters
const int BHR_SIZE = 10; // 10-bit BHR
const int PHT_SIZE = 1024; //PHT SIZE 2**10
const unsigned int BHRT_SIZE = 1024; // requires 4 bits of LSB of the IARG_INS_PTR
const int BTB_SET_SIZE = 256;
const int BTB_K_SIZE = 4;

//UINT64 _references = 0, _predicts = 0;
UINT64 _condInstCount = 0; //Conditional instructions count
UINT64 _indirectBranchCount = 0; // Indirect branch count
UINT64 _parInsCount = 0; //Rest instructions count

//Misprediction counters for various predictors
UINT64 _mispredicitionBimodalCount = 0;
UINT64 _mispredicitionSAgCount = 0;
UINT64 _mispredicitionGAgCount = 0;
UINT64 _mispredicitionGshareCount = 0;
UINT64 _mispredicitionHybridCount = 0;
UINT64 _mispredicitionBTBT1Count = 0;
UINT64 _mispredicitionBTBT2Count = 0;

//BHT, PHT for Bimodal
INT8 patternHistoryTableBimodal[PHT_SIZE+1];

//BHT, PHT for SAg
UINT16 branchHistoryTableSAg[BHRT_SIZE+1];
INT8 patternHistoryTableSAg[PHT_SIZE+1];

//Global branch history for GAg, GShare
UINT16 globalBranchHistory = 0;

//BHT, PHT for GAg
INT8 patternHistoryTableGAg[PHT_SIZE+1];

//BHT, PHT for Gshare
INT8 patternHistoryTableGshare[PHT_SIZE+1];

//BHT, PHT for Hybrid
//Hybrid shares Branch History Register table with SAg predictor
INT8 patternHistoryTableHybrid[PHT_SIZE+1];

//BTB
typedef struct _BTB {
	UINT32 tag;
	UINT32 target;
	INT8 valid; //Valid bits
	UINT8 lruBits;
} BTB, *ptrBTB;
BTB BranchTargetBuffer1[BTB_SET_SIZE][BTB_K_SIZE]; //4-way set(256) associative
BTB BranchTargetBuffer2[BTB_SET_SIZE][BTB_K_SIZE]; //4-way set(256) associative

//Some helper declarations
LOCALVAR ofstream *outfile;
clock_t start;

//Functions declarations
VOID CondBranch(ADDRINT,BOOL);
void PrematureExitRoutine(VOID);
VOID IndirectBranch(ADDRINT, BOOL, ADDRINT);

VOID doCount() {
	_parInsCount ++; 
	if((_parInsCount + _condInstCount) > LIMIT) {
		PrematureExitRoutine();
		exit(0);
	}
}

VOID Instruction(INS ins, VOID *v) {
	if(INS_IsIndirectBranchOrCall(ins)) {
		INS_InsertPredicatedCall(ins, IPOINT_BEFORE, 
			(AFUNPTR)IndirectBranch,
			IARG_INST_PTR,
			IARG_BRANCH_TAKEN,
			IARG_BRANCH_TARGET_ADDR, IARG_END);
	} else if(INS_IsBranchOrCall(ins) && INS_HasFallThrough(ins)) {
		INS_InsertPredicatedCall(ins, IPOINT_BEFORE, 
								 (AFUNPTR)CondBranch,
								 IARG_INST_PTR,
								 IARG_BRANCH_TAKEN,
								 IARG_END);
		
	} else {
		INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)doCount, IARG_END);
	}
}

VOID CondBranch(ADDRINT ip, BOOL taken) {
	_condInstCount++; //Counts conditional branch instructions
	if((_parInsCount + _condInstCount) > LIMIT) {
		PrematureExitRoutine();
		exit(0);
	}
	//Bimodal prediction
	UINT16 index = (ip & 0x3ff) % PHT_SIZE;
	INT8 history = patternHistoryTableBimodal[index];
	if(history <= 1) {
		//Not taken
		if(taken) {
			//A mispredition
			_mispredicitionBimodalCount ++;
			patternHistoryTableBimodal[index] += 1;
		} 				 
	} else if(history >= 2) {
		//Condition for taken
		if(!taken) {
			_mispredicitionBimodalCount ++;
			patternHistoryTableBimodal[index] -= 1;
		}
	}
	//Bimodal Ends

	//SAg prediction
	//Extracting 10 bits (LSB) of the branch address to index branchHistoryRegister table
	UINT16 branchIndex = (ip & 0x3ff) % BHRT_SIZE;
	//Finding index of the pattern history table
	index = (branchHistoryTableSAg[branchIndex] % PHT_SIZE);// (branchHistory^ip)%PHT_SIZE;
	//get the saturating counter from the pattern history table
	history = patternHistoryTableSAg[index];
	if(history <= 1) {
		//Not taken
		if(taken) {
			//A mispredition
			_mispredicitionSAgCount ++;
			patternHistoryTableSAg[index] += 1;
		} 				 
	} else if(history >= 2) {
		//Condition for taken
		if(!taken) {
			_mispredicitionSAgCount ++;
			patternHistoryTableSAg[index] -= 1;
		}
	}
	///SAg ends

	//GAg
	history = patternHistoryTableGAg[globalBranchHistory];
	if(history <= 1) {
		//Not taken
		if(taken) {
			//A mispredition
			_mispredicitionGAgCount ++;
			patternHistoryTableGAg[globalBranchHistory] += 1;
		} 				 
	} else if(history >= 2) {
		//Condition for taken
		if(!taken) {
			_mispredicitionGAgCount ++;
			patternHistoryTableGAg[globalBranchHistory] -= 1;
		}
	}
	//GAg ends

	//Gshare
	index = (globalBranchHistory^ip)%PHT_SIZE;
	history = patternHistoryTableGshare[index];
	if(history <= 1) {
		//Not taken
		if(taken) {
			//A mispredition
			_mispredicitionGshareCount ++;
			patternHistoryTableGshare[index] += 1;
		} 				 
	} else if(history >= 2) {
		//Condition for taken
		if(!taken) {
			_mispredicitionGshareCount ++;
			patternHistoryTableGshare[index] -= 1;
		}
	}
	//Gshare ends

	//Hybrid
	//Extracting 4 bits (LSB) of the branch address to index branchHistoryRegister table
	branchIndex = (ip & 0x3ff) % BHRT_SIZE;
	//Finding index of the pattern history table
	index = (branchHistoryTableSAg[branchIndex]^ip)%PHT_SIZE;// (branchHistory^ip)%PHT_SIZE;
	//get the saturating counter from the pattern history table
	history = patternHistoryTableHybrid[index];
	if(history <= 1) {
		//Not taken
		if(taken) {
			//A mispredition
			_mispredicitionHybridCount ++;
			patternHistoryTableHybrid[index] += 1;
		} 				 
	} else if(history >= 2) {
		//Condition for taken
		if(!taken) {
			_mispredicitionHybridCount ++;
			patternHistoryTableHybrid[index] -= 1;
		}
	}
	index = ((index<<1)+taken);
	branchHistoryTableSAg[branchIndex] = (index & 0x3ff);
	//Hybrid ends

	globalBranchHistory = (((((globalBranchHistory << 1)|taken)) & 0x3ff) % BHR_SIZE);
}
VOID IndirectBranch(ADDRINT ip, BOOL taken, ADDRINT target) {
	_indirectBranchCount++; //Counts conditional branch instructions
	if((_parInsCount + _indirectBranchCount) > LIMIT) {
		PrematureExitRoutine();
		exit(0);
	}
	UINT8 setIndex = ((ip^globalBranchHistory) & 0xff);//%BTB_SET_SIZE; //LocAL modulo hash routine
	int lru = 0;
	UINT16 lruMin = LRU_LIMIT + 4;
	BOOL found = FALSE;
	for(int assocIndex = 0; assocIndex < 4; assocIndex ++ ){
		if(BranchTargetBuffer2[setIndex][assocIndex].target != 0) {
		//Branch exists
			UINT32 tag = BranchTargetBuffer2[setIndex][assocIndex].tag;
			UINT32 tgt = BranchTargetBuffer2[setIndex][assocIndex].target;
			if( tag == ip && (tgt != target || !taken)) {
				_mispredicitionBTBT2Count ++;
				UINT8 ru = BranchTargetBuffer2[setIndex][assocIndex].lruBits;
				if (ru > LRU_LIMIT) { ru = 0; }
				else { ru += 1; }
				BranchTargetBuffer2[setIndex][assocIndex].lruBits = ru;
				found = TRUE;
				break;
			}
		}
	}
	if(!found) {
		for(int i=0; i<4; i++) {
			UINT8 lruBits = BranchTargetBuffer2[setIndex][i].lruBits;
			if(lruBits < lruMin ) { 
				lruMin = lruBits;
				lru = i;
			}
		}
		BranchTargetBuffer2[setIndex][lru].lruBits = 0;
		BranchTargetBuffer2[setIndex][lru].tag = ip;
		BranchTargetBuffer2[setIndex][lru].target = target;
	}
	//Type 1
	setIndex = ip%BTB_SET_SIZE; //LocAL modulo hash routine
	lru = 0;
	lruMin = LRU_LIMIT + 4;
	found = FALSE;
	for(int assocIndex = 0; assocIndex < 4; assocIndex ++ ){
		if(BranchTargetBuffer1[setIndex][assocIndex].target != 0) {
		//Branch exists
			UINT32 tag = BranchTargetBuffer1[setIndex][assocIndex].tag;
			UINT32 tgt = BranchTargetBuffer1[setIndex][assocIndex].target;
			if( tag == ip && (tgt != target || !taken)) {
				_mispredicitionBTBT1Count ++;
				UINT8 ru = BranchTargetBuffer1[setIndex][assocIndex].lruBits;
				if (ru > LRU_LIMIT) { ru = 0; }
				else { ru += 1; }
				BranchTargetBuffer1[setIndex][assocIndex].lruBits = ru;
				found = TRUE;
				break;
			}
		}
	}
	if(!found) {
		for(int i=0; i<4; i++) {
			UINT8 lruBits = BranchTargetBuffer1[setIndex][i].lruBits;
			if(lruBits < lruMin ) { 
				lruMin = lruBits;
				lru = i;
			}
		}
		BranchTargetBuffer1[setIndex][lru].lruBits = 0;
		BranchTargetBuffer1[setIndex][lru].tag = ip;
		BranchTargetBuffer1[setIndex][lru].target = target;
	}
}

/*
KNOB<string> KnobOutputFile(KNOB_MODE_WRITEONCE, "pintool",
    "o", "inscount.out", "specify output file name");
*/
// This function is called when the application exits
VOID Fini(INT32 code, VOID *v)
{
	*outfile << "Bimodal Prediction Statistics" << endl;
	*outfile << "No. of Branch Instructions # " << _condInstCount << endl;
	*outfile << "No. of Mispredictions # "<< _mispredicitionBimodalCount << endl;
	*outfile << "Accuracy # "<<(1.0 - _mispredicitionBimodalCount/double(_condInstCount))*100.0 << "%" << endl;

	///SAg
	*outfile << endl << "SAg Prediction statistics" << endl;
	*outfile << "No. of Branch Instructions # " << _condInstCount << endl;
	*outfile << "No. of Mispredictions # "<< _mispredicitionSAgCount << endl;
	*outfile << "Accuracy # "<<(1.0 - _mispredicitionSAgCount/double(_condInstCount))*100.0 << "%" << endl;

	///GAg
	
	*outfile << endl << "GAg Prediction statistics" << endl;
	*outfile << "No. of Branch Instructions # " << _condInstCount << endl;
	*outfile << "No. of Mispredictions # "<< _mispredicitionGAgCount << endl;
	*outfile << "Accuracy # "<<(1.0 - _mispredicitionGAgCount/double(_condInstCount))*100.0 << "%" << endl;

	///Gshare
	*outfile << endl << "Gshare Prediction statistics" << endl;
	*outfile << "No. of Branch Instructions # " << _condInstCount << endl;
	*outfile << "No. of Mispredictions # "<< _mispredicitionGshareCount << endl;
	*outfile << "Accuracy # "<<(1.0 - _mispredicitionGshareCount/double(_condInstCount))*100.0 << "%" << endl;

	///Hybrid
	*outfile << endl << "Hybrid Prediction statistics" << endl;
	*outfile << "No. of Branch Instructions # " << _condInstCount << endl;
	*outfile << "No. of Mispredictions # "<< _mispredicitionHybridCount << endl;
	*outfile << "Accuracy # "<<(1.0 - _mispredicitionHybridCount/double(_condInstCount))*100.0 << "%" << endl;

	//BTB Type 1
	*outfile << endl << "Branch Target Buffer (Type 1) statistics" << endl;
	*outfile << "No. of Indirect Branch Instructions # " << _indirectBranchCount << endl;
	*outfile << "No. of Mispredictions # "<< _mispredicitionBTBT1Count << endl;
	*outfile << "Accuracy # "<<(1.0 - _mispredicitionBTBT2Count/double(_indirectBranchCount))*100.0 << "%" << endl;
	
	//BTB Type 2
	*outfile << endl << "Branch Target Buffer (Type 2) statistics" << endl;
	*outfile << "No. of Indirect Branch Instructions # " << _indirectBranchCount << endl;
	*outfile << "No. of Mispredictions # "<< _mispredicitionBTBT2Count << endl;
	*outfile << "Accuracy # "<<(1.0 - _mispredicitionBTBT2Count/double(_indirectBranchCount))*100.0 << "%" << endl;
	
	clock_t end = clock();
	*outfile << endl << "Analysis stats generated in # " << double(end-start)/1000.0 <<" seconds " << endl;
}
void PrematureExitRoutine() {
	*outfile << "Premature Exit Routine "<< endl;

	*outfile << "Bimodal Prediction Statistics" << endl;
	*outfile << "No. of Branch Instructions # " << _condInstCount << endl;
	*outfile << "No. of Mispredictions # "<< _mispredicitionBimodalCount << endl;
	*outfile << "Accuracy # "<<(1.0 - _mispredicitionBimodalCount/double(_condInstCount))*100.0 << "%" << endl;

	///SAg
	*outfile << endl << "SAg Prediction statistics" << endl;
	*outfile << "No. of Branch Instructions # " << _condInstCount << endl;
	*outfile << "No. of Mispredictions # "<< _mispredicitionSAgCount << endl;
	*outfile << "Accuracy # "<<(1.0 - _mispredicitionSAgCount/double(_condInstCount))*100.0 << "%" << endl;

	///GAg
	*outfile << endl << "GAg Prediction statistics" << endl;
	*outfile << "No. of Branch Instructions # " << _condInstCount << endl;
	*outfile << "No. of Mispredictions # "<< _mispredicitionGAgCount << endl;
	*outfile << "Accuracy # "<<(1.0 - _mispredicitionGAgCount/double(_condInstCount))*100.0 << "%" << endl;

	///Gshare
	*outfile << endl << "Gshare Prediction statistics" << endl;
	*outfile << "No. of Branch Instructions # " << _condInstCount << endl;
	*outfile << "No. of Mispredictions # "<< _mispredicitionGshareCount << endl;
	*outfile << "Accuracy # "<<(1.0 - _mispredicitionGshareCount/double(_condInstCount))*100.0 << "%" << endl;

	///Hybrid
	*outfile << endl << "Hybrid Prediction statistics" << endl;
	*outfile << "No. of Branch Instructions # " << _condInstCount << endl;
	*outfile << "No. of Mispredictions # "<< _mispredicitionHybridCount << endl;
	*outfile << "Accuracy # "<<(1.0 - _mispredicitionHybridCount/double(_condInstCount))*100.0 << "%" << endl;

	//BTB Type 1
	*outfile << endl << "Branch Target Buffer (Type 1) statistics" << endl;
	*outfile << "No. of Indirect Branch Instructions # " << _indirectBranchCount << endl;
	*outfile << "No. of Mispredictions # "<< _mispredicitionBTBT1Count << endl;
	*outfile << "Accuracy # "<<(1.0 - _mispredicitionBTBT2Count/double(_indirectBranchCount))*100.0 << "%" << endl;
	
	//BTB Type 2
	*outfile << endl << "Branch Target Buffer (Type 2) statistics" << endl;
	*outfile << "No. of Indirect Branch Instructions # " << _indirectBranchCount << endl;
	*outfile << "No. of Mispredictions # "<< _mispredicitionBTBT2Count << endl;
	*outfile << "Accuracy # "<<(1.0 - _mispredicitionBTBT2Count/double(_indirectBranchCount))*100.0 << "%" << endl;
	
	clock_t end = clock();
	*outfile << endl << "Analysis stats generated in # " << double(end-start)/1000.0 <<" seconds " << endl;
}

/* ===================================================================== */
/* Print Help Message                                                    */
/* ===================================================================== */

INT32 Usage()
{
    cerr <<"This pin tool is a various branch predictor. 10 bit BHR and 1024 size PHT \n\n";
    cerr << KNOB_BASE::StringKnobSummary() << endl;
    return -1;
}

/* ===================================================================== */
/* Main                                                                  */
/* ===================================================================== */
/*   argc, argv are the entire command line: pin -t <toolname> -- ...    */
/* ===================================================================== */
void init_TABLES() {
	for(int i=0; i<=PHT_SIZE; i++) {
		patternHistoryTableBimodal[i] = 0;
	}
	for(int i=0; i<=BHRT_SIZE; i++) {
		branchHistoryTableSAg[i] = 0;
	}
	for(int j=0; j <=PHT_SIZE; j++) {
		patternHistoryTableSAg[j]=0;
	}
	for(int j=0; j <=PHT_SIZE; j++) {
		patternHistoryTableGAg[j] = 0;
	}
	
	for(int j=0; j <=PHT_SIZE; j++) {
		patternHistoryTableGshare[j] = 0;
	}
	for(int j=0; j <=PHT_SIZE; j++) {
		patternHistoryTableHybrid[j] = 0;
	}
	for(int i=0; i<BTB_SET_SIZE; i++) {
		for(int j=0; j<BTB_K_SIZE; j++) {
			BranchTargetBuffer1[i][j].target = 0;
			BranchTargetBuffer1[i][j].tag = 0;
			BranchTargetBuffer1[i][j].valid = 0;
			BranchTargetBuffer1[i][j].lruBits = 0;
		}
	}
	for(int i=0; i<BTB_SET_SIZE; i++) {
		for(int j=0; j<BTB_K_SIZE; j++) {
			BranchTargetBuffer2[i][j].target = 0;
			BranchTargetBuffer2[i][j].tag = 0;
			BranchTargetBuffer2[i][j].valid = 0;
			BranchTargetBuffer2[i][j].lruBits = 0;
		}
	}
}
int main(int argc, char * argv[])
{
	start = clock();
    // Initialize pin
    if (PIN_Init(argc, argv)) return Usage();
	//icount.Activate();
	INS_AddInstrumentFunction(Instruction, 0);
	
	outfile = new ofstream("Analysis.out");
	///*outfile << "Abt to Initialized\n";
	init_TABLES();
    // Register Fini to be called when the application exits
    PIN_AddFiniFunction(Fini, 0);
    
    // Start the program, never returns
    PIN_StartProgram();
}
