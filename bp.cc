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

unsigned int saturatingCounter = 0;

//Table Parameters
const int BHR_SIZE = 10; // 10-bit BHR
const int PHT_SIZE = 1024; //PHT SIZE 2**10
const unsigned int BHRT_SIZE = 1024; // requires 4 bits of LSB of the IARG_INS_PTR

//UINT64 _references = 0, _predicts = 0;
UINT64 _condInstCount = 0;
UINT64 _parInsCount = 0;

UINT64 _mispredicitionBimodalCount = 0;
UINT64 _mispredicitionSAgCount = 0;
UINT64 _mispredicitionGAgCount = 0;
UINT64 _mispredicitionGshareCount = 0;
UINT64 _mispredicitionHybridCount = 0;

//BHT, PHT for SAg
UINT16 branchHistoryTableSAg[BHRT_SIZE+1];
INT8 patternHistoryTableSAg[PHT_SIZE+1];

//BHT, PHT for GAg
UINT16 branchHistoryGAg = 0;
INT8 patternHistoryTableGAg[PHT_SIZE+1];

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
	if(saturatingCounter >= 2 && !taken) {
		_mispredicitionBimodalCount ++;
		saturatingCounter --;
	} else if(saturatingCounter <= 1 && taken) {
		_mispredicitionBimodalCount ++;
		saturatingCounter ++;
	}
	//Bimodal Ends

	//SAg prediction
	//Extracting 10 bits (LSB) of the branch address to index branchHistoryRegister table
	UINT8 branchIndex = UINT8(ip & 0x7ff);
	//Finding index of the pattern history table
	UINT8 index = branchHistoryTableSAg[branchIndex];// (branchHistory^ip)%PHT_SIZE;
	//get the saturating counter from the pattern history table
	INT8 history = patternHistoryTableSAg[index];
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
	index = ((index<<1)+taken);
	branchHistoryTableSAg[branchIndex] = index;
	///SAg ends

	//GAg prediction
	history = patternHistoryTableGAg[branchHistoryGAg];
	if(history <= 1) {
		//Not taken
		if(taken) {
			//A mispredition
			_mispredicitionGAgCount ++;
			patternHistoryTableGAg[branchHistoryGAg] += 1;
		} 				 
	} else if(history >= 2) {
		//Condition for taken
		if(!taken) {
			_mispredicitionGAgCount ++;
			patternHistoryTableGAg[branchHistoryGAg] -= 1;
		}
	}
	branchHistoryGAg = ((branchHistoryGAg<<1)+taken);
	branchHistoryGAg &= 0x7ff;//10-bits
	//GAg ends

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

	clock_t end = clock();
	*outfile << endl << "Output genrated in # " << double(end-start)/1000.0 <<" seconds " << endl;
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

	clock_t end = clock();
	*outfile << endl << "Output genrated in # " << double(end-start)/1000.0 <<" seconds " << endl;
}

/* ===================================================================== */
/* Print Help Message                                                    */
/* ===================================================================== */

INT32 Usage()
{
    cerr <<"This pin tool is a GAg branch predictor. 8 bit BHR and 256 size PHT \n\n";
    cerr << KNOB_BASE::StringKnobSummary() << endl;
    return -1;
}

/* ===================================================================== */
/* Main                                                                  */
/* ===================================================================== */
/*   argc, argv are the entire command line: pin -t <toolname> -- ...    */
/* ===================================================================== */

int main(int argc, char * argv[])
{
	start = clock();
    // Initialize pin
    if (PIN_Init(argc, argv)) return Usage();
	//icount.Activate();
	INS_AddInstrumentFunction(Instruction, 0);

	outfile = new ofstream("Analysis.out");
    // Register Fini to be called when the application exits
    PIN_AddFiniFunction(Fini, 0);
    
    // Start the program, never returns
    PIN_StartProgram();
}
