import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.program.model.listing.Function;
import ghidra.program.model.address.Address;
import java.nio.file.Files;
import java.nio.file.Path;

// Static analysis only. Never executes captured instructions.
public class DecompileCodec extends GhidraScript {
    public void run() throws Exception {
        String[] names={"trico_mesh", "trico_soup", "huff8", "huff16", "huff816",
            "byet", "key16", "bytes", "quantf", "createSplats", "reorder_faces"};
        String[] addresses={"1b7097500", "1b709c238", "1b709c7b4", "1b709cbf4",
            "1b709d024", "1b709decc", "1b709f14c", "1b709f3d0", "1b70afc4c",
            "1b70ae89c", "1b70ade60"};
        Path out=Path.of(getScriptArgs()[0]);
        Files.createDirectories(out);
        for(int i=0;i<addresses.length;i++) {
            Address at=toAddr(addresses[i]);
            disassemble(at);
            Function f=getFunctionAt(at);
            if(f==null) f=createFunction(at,names[i]);
            if(f!=null) f.setName(names[i],ghidra.program.model.symbol.SourceType.USER_DEFINED);
        }
        DecompInterface d=new DecompInterface();
        d.openProgram(currentProgram);
        for(int i=0;i<addresses.length;i++) {
            Function f=getFunctionAt(toAddr(addresses[i]));
            if(f==null) {println("MISSING "+names[i]);continue;}
            DecompileResults r=d.decompileFunction(f,180,monitor);
            String text=r.decompileCompleted() && r.getDecompiledFunction()!=null
                ? r.getDecompiledFunction().getC() : "FAILED: "+r.getErrorMessage();
            Files.writeString(out.resolve(names[i]+".c"),text);
            println("WROTE "+names[i]+" chars="+text.length());
        }
        d.dispose();
    }
}
