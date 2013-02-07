/**
  Solution to Problem B
	@author: Anurag Gautam
*/

#include <iostream>
#include <fstream>
#include "pin.H"

ofstream OutFile; //output file

//Comment it out if instrumenting application that has total instructions < 1000000000 (1 billion)
#define PRODUCTION

// The running count of instructions is kept here
// make it static to help the compiler optimize docount
static UINT64 icount = 0;			//Instruction counter
static UINT64 latency = 0;			//Latency counter

// This function is called before every instruction is executed
#ifdef PRODUCTION
UINT64 fastForwardCount = 1;

ADDRINT insCount(){ 
	icount ++; 
	return (icount >= fastForwardCount + 1000000000);
}
ADDRINT fastForward(void) {
	return (icount >= fastForwardCount);
}
VOID myPredicatedAnalysis(VOID* isLS) {
	// if fast-forward number of instructions have been executed and one billion
	// instructions after fast-forward have not been executed, then do the analysis
	int is = (int)isLS;
	if(is == 0x0) {
		latency += 100;
	} else {
		latency ++;
	}
}

VOID myExitRoutine() {
	OutFile.setf(ios::showbase);
    OutFile << "Total Ins count " << icount << endl;
	OutFile << "CPI: " << latency/(double)icount << endl;
    OutFile.close();
	exit(0);
}
#endif

VOID lsLatencyCount()    { 
	latency += 100; 
#ifndef PRODUCTION
	icount++;
#endif
}
VOID otherLatencyCount() { 
	latency ++; 
#ifndef PRODUCTION
	icount++;
#endif
}

// Pin calls this function every time a new instruction is encountered
VOID Instruction(INS ins, VOID *v)
{
    // Insert a call to docount before every instruction, no arguments are passed
#ifdef PRODUCTION
	INS_InsertIfCall(ins, IPOINT_BEFORE, (AFUNPTR)insCount, IARG_END);
	INS_InsertThenCall(ins, IPOINT_BEFORE, myExitRoutine, IARG_END);	
	// FastForward() is called for every instruction executed
	INS_InsertIfCall(ins, IPOINT_BEFORE, (AFUNPTR)fastForward, IARG_END);	
	INS_InsertThenPredicatedCall(ins, IPOINT_BEFORE, (AFUNPTR)myPredicatedAnalysis, 
		IARG_BOOL, INS_IsMemoryRead(ins) || INS_IsMemoryWrite(ins),
		IARG_END);
#else
	if(INS_IsMemoryRead(ins) || INS_IsMemoryWrite(ins)) {
		INS_InsertCall(ins, IPOINT_BEFORE, lsLatencyCount, IARG_END);
	} else {
		INS_InsertCall(ins, IPOINT_BEFORE, otherLatencyCount, IARG_END);
	}
#endif
}

KNOB<string> KnobOutputFile(KNOB_MODE_WRITEONCE, "pintool",
    "o", "inscount.out", "specify output file name");

// This function is called when the application exits
VOID Fini(INT32 code, VOID *v)
{
    // Write to a file since cout and cerr maybe closed by the application
    OutFile.setf(ios::showbase);
    OutFile << "Total Ins count " << icount << endl;
	OutFile << "CPI: " << latency/(double)icount << endl;
    OutFile.close();
}

/* ===================================================================== */
/* Print Help Message                                                    */
/* ===================================================================== */

INT32 Usage()
{
    cerr << "This tool counts the number of dynamic instructions executed" << endl;
    cerr << endl << KNOB_BASE::StringKnobSummary() << endl;
    return -1;
}

/* ===================================================================== */
/* Main                                                                  */
/* ===================================================================== */
/*   argc, argv are the entire command line: pin -t <toolname> -- ...    */
/* ===================================================================== */

int main(int argc, char * argv[])
{
    // Initialize pin
    if (PIN_Init(argc, argv)) return Usage();

    OutFile.open(KnobOutputFile.Value().c_str());

    // Register Instruction to be called to instrument instructions
    INS_AddInstrumentFunction(Instruction, 0);

    // Register Fini to be called when the application exits
    PIN_AddFiniFunction(Fini, 0);
    
    // Start the program, never returns
    PIN_StartProgram();
    
    return 0;
}
