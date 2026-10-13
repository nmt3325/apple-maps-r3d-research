import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.program.model.listing.Function;
import ghidra.program.model.address.Address;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.charset.StandardCharsets;

public class DecompileBytes extends GhidraScript {
    @Override
    protected void run() throws Exception {
        Address entry=toAddr("0x1b709f3d0");
        println("ENTRY="+entry+" bytes="+currentProgram.getMemory().getBlock(entry));
        boolean ok=disassemble(entry);
        Function f=getFunctionAt(entry);
        if(f==null) f=createFunction(entry,"bytes_decompress");
        println("DISASSEMBLED="+ok+" function="+f);
        DecompInterface decompiler=new DecompInterface();
        decompiler.setSimplificationStyle("decompile");
        decompiler.openProgram(currentProgram);
        DecompileResults result=decompiler.decompileFunction(f,180,monitor);
        String contents=(result.decompileCompleted() && result.getDecompiledFunction()!=null)
            ? result.getDecompiledFunction().getC()
            : "FAILED: "+result.getErrorMessage();
        Path path=Path.of("/opt/flyover-viewer/nativefree-lab-20261013/bytes_decompress.c");
        Files.writeString(path,contents,StandardCharsets.UTF_8);
        println("OUTPUT="+path+" chars="+contents.length()+" body="+f.getBody());
        decompiler.dispose();
    }
}
