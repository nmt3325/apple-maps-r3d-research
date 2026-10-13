import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.program.model.listing.Function;
import ghidra.program.model.address.Address;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.charset.StandardCharsets;

public class DecompileHuff extends GhidraScript {
    @Override
    protected void run() throws Exception {
        String[] names={"huff8_decompress","huff16_decompress","huff816_decompress"};
        String[] addresses={"0x1b709c7b4","0x1b709cbf4","0x1b709d024"};
        Path folder=Path.of("/opt/flyover-viewer/ghidra-lab/output");
        Files.createDirectories(folder);
        for(int i=0;i<addresses.length;i++){
            Address entry=toAddr(addresses[i]);
            boolean ok=disassemble(entry);
            Function function=getFunctionAt(entry);
            if(function==null){function=createFunction(entry,names[i]);}
            println("FUNCTION "+names[i]+" @"+entry+" disassembled="+ok+
                    " existing="+(function!=null));
        }
        DecompInterface decompiler=new DecompInterface();
        decompiler.setSimplificationStyle("decompile");
        decompiler.openProgram(currentProgram);
        for(int i=0;i<addresses.length;i++){
            Address entry=toAddr(addresses[i]);
            Function f=getFunctionAt(entry);
            if(f==null){println("MISSING "+names[i]);continue;}
            DecompileResults result=decompiler.decompileFunction(f,160,monitor);
            String contents="";
            if(result.decompileCompleted() && result.getDecompiledFunction()!=null){
                contents=result.getDecompiledFunction().getC();
            }else{
                contents="FAILED: "+result.getErrorMessage();
            }
            Files.writeString(folder.resolve(names[i]+".c"),contents,StandardCharsets.UTF_8);
            println("WROTE "+names[i]+" chars="+contents.length());
        }
        decompiler.dispose();
    }
}
