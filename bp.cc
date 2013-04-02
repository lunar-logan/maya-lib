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

//UINT64 _references = 0, _predicts = 0;
UINT64 _condInstCount = 0;
UINT64 _mispredicitionCount = 0;
UINT64 _parInsCount = 0;

LOCALVAR ofstream *outfile;
clock_t start;

//Functions declarations
VOID CondBranch(BOOL);
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
								 IARG_BRANCH_TAKEN,
								 IARG_END);
		
	} else {
		INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)doCount, IARG_END);
	}
}

VOID CondBranch(BOOL taken) {
	_condInstCount++; //Counts conditional branch instructions
	if((_parInsCount + _condInstCount) > LIMIT) {
		PrematureExitRoutine();
		exit(0);
	}
	if(saturatingCounter >= 2 && !taken) {
		_mispredicitionCount ++;
		saturatingCounter --;
	} else if(saturatingCounter <= 1 && taken) {
		_mispredicitionCount ++;
		saturatingCounter ++;
	}
}
/*
KNOB<string> KnobOutputFile(KNOB_MODE_WRITEONCE, "pintool",
    "o", "inscount.out", "specify output file name");
*/
// This function is called when the application exits
VOID Fini(INT32 code, VOID *v)
{
	*outfile << endl;
	*outfile << "No. of Branch Instructions # " << _condInstCount << endl;
	*outfile << "No. of Mispredictions # "<< _mispredicitionCount << endl;
	*outfile << "Accuracy # "<<(1.0 - _mispredicitionCount/double(_condInstCount))*100.0 << "%" << endl;
	clock_t end = clock();
	*outfile << "Output genrated in # " << double(end-start)/1000.0 <<" seconds " << endl;
}
void PrematureExitRoutine() {
	*outfile << endl;
	*outfile << "Premature Exit Routine "<<endl;
	*outfile << "No. of Branch Instructions # " << _condInstCount << endl;
	*outfile << "No. of Mispredictions # "<< _mispredicitionCount << endl;
	*outfile << "Accuracy # "<<(1.0 - _mispredicitionCount/double(_condInstCount))*100.0 << "%" << endl;
	clock_t end = clock();
	*outfile << "Output genrated in # " << double(end-start)/1000.0 <<" seconds " << endl;
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

	outfile = new ofstream("Bimodal.out");
    // Register Fini to be called when the application exits
    PIN_AddFiniFunction(Fini, 0);
    
    // Start the program, never returns
    PIN_StartProgram();
}
