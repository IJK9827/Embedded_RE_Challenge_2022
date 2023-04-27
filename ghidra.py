import os
os.environ["GHIDRA_INSTALL_DIR"] = "/media/ijk98/EEFF-DBBA/empty_folder/downloads/ghidra_10.2.3_PUBLIC"


import pyhidra
pyhidra.start()

decompInterface = ghidra.app.decompiler.DecompInterface()
decompInterface.openProgram(currentProgram)
decompileResults = decompInterface.decompileFunction(currentFunction, 30, monitor)
if decompileResults.decompileCompleted():
    decompiledFunction = decompileResults.getDecompiledFunction()
    decompiledFunction.getC()
