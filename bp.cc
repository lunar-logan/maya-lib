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

//Table Parameters
const int BHR_SIZE = 10; // 10-bit BHR
const int PHT_SIZE = 1024; //PHT SIZE 2**10
const unsigned int BHRT_SIZE = 1024; // requires 4 bits of LSB of the IARG_INS_PTR

//UINT64 _references = 0, _predicts = 0;
UINT64 _condInstCount = 0; //Conditional instructions count
UINT64 _parInsCount = 0; //Rest instructions count

//Misprediction counters for various predictors
UINT64 _mispredicitionBimodalCount = 0;
UINT64 _mispredicitionSAgCount = 0;
UINT64 _mispredicitionGAgCount = 0;
UINT64 _mispredicitionGshareCount = 0;
UINT64 _mispredicitionHybridCount = 0;

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


LOCALVAR ofstream *outfile;
clock_t start;

//Functions declarations
VOID CondBranch(ADDRINT,BOOL);
void PrematureExitRoutine(VOID);

VOID doCount() {
	_parInsCount ++; 
	if((_parInsCount + _condInstCount) > LIMIT) {
		PrematureExitRoutine();
		exit(0);
	}
}

VOID Instruction(INS ins, VOID *v) {
	if(INS_IsBranchOrCall(ins) && INS_HasFallThrough(ins)) {
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

	clock_t end = clock();
	*outfile << endl << "Analysis stats genrated in # " << double(end-start)/1000.0 <<" seconds " << endl;
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

	clock_t end = clock();
	*outfile << endl << "Analysis stats genrated in # " << double(end-start)/1000.0 <<" seconds " << endl;
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
