#import <UIKit/UIKit.h>
#import <Foundation/Foundation.h>
#import <MapKit/MapKit.h>
#include <dlfcn.h>
#include <mach-o/dyld.h>
#include <mach-o/loader.h>
#include <mach-o/getsect.h>
#include <inttypes.h>
#include <sys/stat.h>
#include <string.h>

@interface DecoderDelegate : UIResponder <UIApplicationDelegate>
@property (nonatomic,strong) UIWindow *window;
@end
@implementation DecoderDelegate
- (BOOL)application:(UIApplication *)application didFinishLaunchingWithOptions:(NSDictionary *)options {
 return YES;
}
- (void)runDecode {
 NSMutableDictionary *result=[NSMutableDictionary dictionary];
 result[@"stage"]=@"init";
 char const *path="/System/Library/PrivateFrameworks/VectorKit.framework/VectorKit";
 void *handle=dlopen(path,RTLD_LAZY|RTLD_GLOBAL);
 const char *dlerr=dlerror(); result[@"dlopen"]=handle?@"success":[NSString stringWithUTF8String:dlerr?dlerr:"failed"];
 const struct mach_header_64 *mh=nullptr;intptr_t slide=0;
 for(uint32_t i=0;i<_dyld_image_count();i++){
  const char *name=_dyld_get_image_name(i);
  if(name&&strstr(name,"/VectorKit.framework/")){
   mh=(const struct mach_header_64*)_dyld_get_image_header(i);
   slide=_dyld_get_image_vmaddr_slide(i);
   result[@"loadedImage"]=[NSString stringWithUTF8String:name];break;
  }
 }
 if(!mh){result[@"error"]=@"VectorKit not loaded";[self save:result];return;}
 uintptr_t textVm=0;uintptr_t dataPtr=0;uint64_t textSize=0;
 const uint8_t *cur=(const uint8_t*)(mh+1);
 for(uint32_t i=0;i<mh->ncmds;i++){
  const struct load_command *cmd=(const struct load_command*)cur;
  if(cmd->cmd==LC_SEGMENT_64){
   const struct segment_command_64 *seg=(const struct segment_command_64*)cmd;
   if(strncmp(seg->segname,"__TEXT",16)==0){
    textVm=(uintptr_t)seg->vmaddr;
    for(uint32_t j=0;j<seg->nsects;j++){
     const struct section_64 *sec=(const struct section_64*)(seg+1)+j;
     if(strncmp(sec->sectname,"__text",16)==0){dataPtr=sec->addr+(uintptr_t)slide;textSize=sec->size;}
    }
   }
  }
  cur+=cmd->cmdsize;
 }
 result[@"textVMBase"]=[NSString stringWithFormat:@"0x%llx",(unsigned long long)textVm];
 result[@"textSize"]=@(textSize);
 unsigned hits=0;uintptr_t hitAddr=0; NSMutableArray *magicSites=[NSMutableArray array];
 if(dataPtr&&textSize>=1024){
  for(size_t j=0;j+16<textSize;j+=4){
   uint32_t w0=*(const uint32_t*)(dataPtr+j),w1=*(const uint32_t*)(dataPtr+j+4);
   bool a=(w0&0x7f800000)==0x52800000 && ((w0>>5)&0xffff)==0x963d;
   bool b=(w1&0x7f800000)==0x72800000 && ((w1>>5)&0xffff)==0x2e59 && ((w1>>21)&3)==1;
   if(a&&b&&(w0&31)==(w1&31)){hits++;hitAddr=dataPtr+j; [magicSites addObject:@(j)];}
  }
 }
 NSMutableArray *createSplatsSites=[NSMutableArray array];
 if(dataPtr && textSize > 256) {
  for(size_t j=0;j+64<textSize;j+=4){
   const uint32_t *w=(const uint32_t*)(dataPtr+j);
   if(w[0]==0xd503237f && w[1]==0xd103c3ff && w[2]==0x6d0823e9 && w[10]==0xb9800816){
    [createSplatsSites addObject:@(j)];
   }
  }
 }
 result[@"createSplatsPatternMatches"]=createSplatsSites;
 result[@"createSplatsPotentialOffsets"]=[createSplatsSites valueForKey:@"description"];
 result[@"magicCheckSites"]=@(hits);
 result[@"magicSiteOffsets"]=magicSites;
 NSString *dumpDir=[NSHomeDirectory() stringByAppendingPathComponent:@"Documents"];
 [[NSFileManager defaultManager] createDirectoryAtPath:dumpDir withIntermediateDirectories:YES attributes:nil error:nil];
 for(NSUInteger k=0;k<magicSites.count;k++){
  NSUInteger site=(NSUInteger)[magicSites[k] unsignedLongLongValue];
  if(site>8192 && site+2048<textSize){
   NSData *dump=[NSData dataWithBytes:(const void*)(dataPtr+site-8192) length:10240];
   [dump writeToFile:[dumpDir stringByAppendingPathComponent:[NSString stringWithFormat:@"vector-magic-%lu.bin",(unsigned long)k]] atomically:YES];
  }
 }
 result[@"magicCheckOffset"]=hitAddr?[NSString stringWithFormat:@"0x%llx",(unsigned long long)(hitAddr-((uintptr_t)textVm+(uintptr_t)slide))]:@"";
 uintptr_t entry=0;
 NSString *fn=[NSBundle.mainBundle pathForResource:@"r3d_offset" ofType:@"txt"];
 if(fn){
  NSString *offstr=[NSString stringWithContentsOfFile:fn encoding:NSUTF8StringEncoding error:nil];
  if(offstr.length){unsigned long long off=strtoull(offstr.UTF8String,nullptr,0);entry=textVm+(uintptr_t)slide+(uintptr_t)off;result[@"entryMethod"]=@"computed-from-simulator-symbol-offset";}
 }
 if(!entry){void *ptr=dlsym(handle,"r3d_world_read_mem");if(!ptr)ptr=dlsym(handle,"_r3d_world_read_mem");if(ptr){entry=(uintptr_t)ptr;result[@"entryMethod"]=@"dlsym";}}
 if(!entry&&hitAddr){entry=hitAddr-0xf0;result[@"entryMethod"]=@"provisional-firmware-signature";}
 if(entry && dataPtr){
  NSString *out=[NSHomeDirectory() stringByAppendingPathComponent:@"Documents/R3D-disassembly-region.bin"];
  NSData *region=[NSData dataWithBytes:(const void*)(entry+0x3000) length:0x1e000];
  [region writeToFile:out atomically:YES];
  result[@"relativeDisasmRegion"]=@"reader+0x3000, length 0x1e000";
 }
 result[@"functionAvailable"]=@(entry!=0);
 result[@"functionOffset"]=entry?[NSString stringWithFormat:@"0x%llx",(unsigned long long)(entry-textVm-(uintptr_t)slide)]:@"";
 NSString *tile=[NSBundle.mainBundle pathForResource:@"test-tile" ofType:@"r3d"];
 NSData *bytes=[NSData dataWithContentsOfFile:tile];
 result[@"bytesRead"]=@(bytes.length);
 if(!entry||!bytes.length){result[@"stage"]=@"no decoder or tile";[self save:result];return;}
 // Only execute a function whose *exact* simulator offset was obtained offline,
 // or whose symbol is explicitly exported. Signature-based guessing is not executed.
 if([result[@"entryMethod"] isEqualToString:@"provisional-firmware-signature"]){
  result[@"stage"]=@"found-magic-but-not-safely-located-function";[self save:result];return;
 }
 typedef int (*R3dReadFunc)(const unsigned char*,size_t,void*);
 R3dReadFunc read=(R3dReadFunc)entry;
 void *world=calloc(1,0x2000);
 int status=read((const unsigned char*)bytes.bytes,(size_t)bytes.length,world);
 result[@"nativeReturn"]=@(status);
 if(status==0) {
   uint64_t images=*(uint64_t*)((char*)world+0x338);
   uintptr_t textureRecordPtr=*(uintptr_t*)((char*)world+0x340);
   result[@"nativeTextureRecordCount"]=@(images);
   NSString *docs=[NSHomeDirectory() stringByAppendingPathComponent:@"Documents"];
   NSMutableArray *found=[NSMutableArray array];
   if(images>0 && images<=8 && textureRecordPtr>0x100000000ull){
    for(uint64_t k=0;k<images;k++){
      char *entry=(char*)textureRecordPtr+k*0x9888;
      [[NSData dataWithBytes:entry length:0x9888] writeToFile:[docs stringByAppendingPathComponent:[NSString stringWithFormat:@"texture-record-%llu.bin",k]] atomically:YES];
      for(uint64_t slot=0;slot<64;slot++){
       uintptr_t pixels=*(uintptr_t*)(entry+0x608+8*slot);
       uint64_t count=*(uint64_t*)(entry+0x808+8*slot);
       if(pixels>0x100000000ull && count>32 && count<10000000){
         NSString *file=[NSString stringWithFormat:@"native-image-%llu-%llu.bin",k,slot];
         [[NSData dataWithBytes:(const void*)pixels length:(NSUInteger)count] writeToFile:[docs stringByAppendingPathComponent:file] atomically:YES];
         [found addObject:@{ @"record":@(k),@"slot":@(slot),@"bytes":@(count) }];
       }
      }
    }
   }
   result[@"nativeTextureImageSlots"]=found;
 }

 if(status==0){
   NSString *dir=[NSHomeDirectory() stringByAppendingPathComponent:@"Documents"];
   const int offsets[]={0x2b0,0x2c8,0x2e0,0x2f8,0x310,0x328};
   const int stride[]={12,8,12,4,4,4};
   for(int q=0;q<6;q++){
      int off=offsets[q];
      uint64_t count=*(uint64_t*)((char*)world+off+8);
      void *src=*(void**)((char*)world+off);
      if(src && count>0 && count<500000 && count*stride[q]<30000000){
         NSString *file=[dir stringByAppendingPathComponent:[NSString stringWithFormat:@"c3m-%03x.bin",off]];
         [[NSData dataWithBytes:src length:(NSUInteger)count*stride[q]] writeToFile:file atomically:YES];
      }
   }
 }


 if(status==0) {
  NSString *dd=[NSHomeDirectory() stringByAppendingPathComponent:@"Documents"];
  [[NSData dataWithBytes:world length:0x650] writeToFile:[dd stringByAppendingPathComponent:@"mesh-world-raw.bin"] atomically:YES];
  NSArray<NSNumber*> *offsets=@[@688,@712,@736,@760,@784,@808,@832,@856];
  for(NSNumber *nn in offsets) {
   NSUInteger off=nn.unsignedIntegerValue;
   uintptr_t addr=*(uintptr_t*)((char*)world+off);
   uint64_t count=*(uint64_t*)((char*)world+off+8);
   if(addr>0x100000000ull && count>0 && count<2000000){
    NSUInteger len=(NSUInteger)MIN(count*4,262144);
    NSData *chunk=[NSData dataWithBytes:(const void*)addr length:len];
    [chunk writeToFile:[dd stringByAppendingPathComponent:[NSString stringWithFormat:@"mesh-field-%03lx.bin",(unsigned long)off]] atomically:YES];
   }
  }
 }

 uint64_t mc=*(uint64_t*)((char*)world+0x350);
 result[@"meshCountCandidate"]=@(mc);
 if(mc>0 && mc<32){const void *mp=*(void**)((char*)world+0x358); NSString *fp=[NSHomeDirectory() stringByAppendingPathComponent:@"Documents/r3d-mesh-array.bin"];[[NSData dataWithBytes:mp length:(NSUInteger)mc*32] writeToFile:fp atomically:YES];}


 result[@"worldHexPrefix"]=[[NSData dataWithBytes:world length:96] description];
 NSMutableArray *ptrs=[NSMutableArray array];
 for(size_t j=0;j<0x4c0;j+=8){
  uint64_t val=*(uint64_t*)((char*)world+j);
  if(val){[ptrs addObject:@{@"byteOffset":@(j),@"valueHex":[NSString stringWithFormat:@"0x%llx",(unsigned long long)val]}];}
 }
 result[@"nonzeroFields"]=ptrs;
 NSMutableArray *descriptorSamples=[NSMutableArray array];
 uint32_t descriptors=(uint32_t)*(uint64_t*)((char*)world+0x20);
 uintptr_t descriptorPtr=(uintptr_t)*(void**)((char*)world+0x28);
 if(descriptors>0&&descriptors<100 && descriptorPtr>0x100000000ull){
  for(uint32_t i=0;i<descriptors;i++){
    uint32_t *r=(uint32_t*)(descriptorPtr+i*12);
    [descriptorSamples addObject:@{@"id":@(i),@"kind":@(r[0]),@"x":@(r[1]),@"y":@(r[2])}];
  }
 }
 result[@"descriptors"]=descriptorSamples;
 NSMutableDictionary *pointers=[NSMutableDictionary dictionary];
 int offsets[]={0,16,40,688,712,736,760,784,808,832,856};
 for(int i=0;i<11;i++){
  int off=offsets[i];
  uintptr_t ptr=(uintptr_t)*(void**)((char*)world+off);
  if(ptr>0x100000000ull){
   NSData *chunk=[NSData dataWithBytes:(const void*)ptr length:128];
   pointers[[NSString stringWithFormat:@"%d",off]]=[chunk description];
  }
 }
 result[@"nativePointerSamples128"]=pointers;

 int32_t nativeCount=*(int32_t*)((char*)world+8);
 uintptr_t positions=(uintptr_t)*(void**)world;
 result[@"splatCountOffset8"]=@(nativeCount);
 result[@"positionPointer"]=positions?@"nonzero":@"zero";
 if(nativeCount>0 && nativeCount<500000 && positions>0x100000000ull){
  NSString *dir=[NSHomeDirectory() stringByAppendingPathComponent:@"Documents"];
  [[NSFileManager defaultManager] createDirectoryAtPath:dir withIntermediateDirectories:YES attributes:nil error:nil];
  NSData *xyz=[NSData dataWithBytes:(const void*)positions length:(size_t)nativeCount*12];
  [xyz writeToFile:[dir stringByAppendingPathComponent:@"native-positions-f32le.bin"] atomically:YES];
  float *vf=(float*)positions;
  result[@"samplePositions"]=@[@(vf[0]),@(vf[1]),@(vf[2])];
 }
 if(nativeCount>0 && nativeCount<500000){
  NSUInteger channels=(NSUInteger)*(uint64_t*)((char*)world+0x18);
  void *attr=*(void**)((char*)world+0x10);
  result[@"nativeAttributeChannels"]=@(channels);
  if(channels==8 && attr){
   NSString *dir=[NSHomeDirectory() stringByAppendingPathComponent:@"Documents"];
   NSData *attributes=[NSData dataWithBytes:attr length:(size_t)nativeCount*channels*sizeof(float)];
   [attributes writeToFile:[dir stringByAppendingPathComponent:@"native-attributes-f32le.bin"] atomically:YES];
   float *row=(float*)attr;
   NSMutableArray *sample=[NSMutableArray array];
   for(int i=0;i<8;i++)[sample addObject:@(row[i])];
   result[@"firstAttributeRow"]=sample;
  }
 }
 // Verified exact Simulator createSplats instruction sequence:
 // sub sp,#0xf0; stp d9,d8; ...; ldrsw x22,[x0,#8].
 uintptr_t createPtr=entry+0xdcc8;
 const uint32_t *code=(const uint32_t*)createPtr;
 if(status==0 && code[0]==0xd103c3ff && code[1]==0x6d0823e9 && code[9]==0xb9800816){
  typedef int (*CreateSplats)(const void*,void*);
  CreateSplats create=(CreateSplats)createPtr;
  void *splats=calloc(1,0x4000);
  int ok=create(world,splats);
  result[@"createSplatsStatus"]=@(ok);
  NSMutableArray *vecs=[NSMutableArray array];
  NSString *dir=[NSHomeDirectory() stringByAppendingPathComponent:@"Documents"];
  for(int off=0x38;off<0x180;off+=8){
   uintptr_t first=*(uintptr_t*)((char*)splats+off);
   uintptr_t last=*(uintptr_t*)((char*)splats+off+8);
   if(first>0x100000000ull && last>=first && last-first<16000000){
    NSMutableDictionary *v=[NSMutableDictionary dictionaryWithDictionary:@{
      @"offset":@(off),@"bytes":@(last-first)}];
    if(last>first && last-first<=3000000){
     NSString *file=[NSString stringWithFormat:@"createSplats-vector-%03x.bin",off];
     NSData *out=[NSData dataWithBytes:(const void*)first length:(size_t)(last-first)];
     [out writeToFile:[dir stringByAppendingPathComponent:file] atomically:YES];
     v[@"file"]=file;
    }
    [vecs addObject:v];
   }
  }
  result[@"nativeSplatVectors"]=vecs;
  result[@"splatsStructHex"]=[[NSData dataWithBytes:splats length:240] description];
  // output vector-owned memory is intentionally left for this short-lived experiment
 }else{
  result[@"createSplatsStatus"]=@"exact function prologue not matched";
 }
 result[@"stage"]=@"decoder-invoked";
 // r3d_world_free is a local function: avoid unsafe manual free; the process is short-lived.
 [self save:result];
 [self batchDecodeR3DAtEntry:entry maxTiles:223];
}
- (void)batchDecodeR3DAtEntry:(uintptr_t)entry maxTiles:(int)limit {
 typedef int (*R3dReadFunc)(const unsigned char*,size_t,void*);
 typedef void (*R3dFreeFunc)(void*);
 R3dReadFunc read=(R3dReadFunc)entry;
 // Validated adjacent function boundary in the installed iOS 27.0 Simulator's VectorKit.
 R3dFreeFunc cleanup=(R3dFreeFunc)(entry-0xa0);
 NSString *docs=[NSHomeDirectory() stringByAppendingPathComponent:@"Documents"];
 NSString *input=[docs stringByAppendingPathComponent:@"NativeTiles"];
 NSString *output=[docs stringByAppendingPathComponent:@"NativeDecoded"];
 [[NSFileManager defaultManager] createDirectoryAtPath:output withIntermediateDirectories:YES attributes:nil error:nil];
 NSArray<NSString*> *names=[[[NSFileManager defaultManager] contentsOfDirectoryAtPath:input error:nil] sortedArrayUsingSelector:@selector(compare:)];
 NSMutableArray *results=[NSMutableArray array];
 NSInteger tried=0,ok=0;
 for(NSString *name in names){
  if(![name.pathExtension isEqualToString:@"r3d"])continue;
  if(tried>=limit)break;
  tried++;
  @autoreleasepool {
   NSData *src=[NSData dataWithContentsOfFile:[input stringByAppendingPathComponent:name]];
   NSMutableDictionary *meta=[NSMutableDictionary dictionaryWithDictionary:@{@"file":name,@"rawBytes":@(src.length)}];
   if(src.length<100){meta[@"error"]=@"too-small";[results addObject:meta];continue;}
   void *world=calloc(1,0x2000);
   int status=read((const unsigned char*)src.bytes,(size_t)src.length,world);
   meta[@"nativeStatus"]=@(status);
   uint32_t count=(uint32_t)*(uint64_t*)((char*)world+0x8);
   uint64_t channels=*(uint64_t*)((char*)world+0x18);
   meta[@"vertices"]=@(count);meta[@"channels"]=@(channels);
   NSUInteger ndesc=(NSUInteger)*(uint64_t*)((char*)world+0x20);
   void *dp=*(void**)((char*)world+0x28);
   NSMutableArray *desc=[NSMutableArray array];
   if(ndesc>0&&ndesc<50 && dp){
    for(NSUInteger k=0;k<ndesc;k++){
     const uint32_t *x=(uint32_t*)((char*)dp+12*k);
     [desc addObject:@[@(x[0]),@(x[1]),@(x[2])]];
    }
   }
   meta[@"attributes"]=desc;
   void *xyz=*(void**)world, *attr=*(void**)((char*)world+0x10);
   if(status==0&&count>0&&count<300000&&channels>0&&channels<=32&&xyz&&attr){
    uint64_t outputBytes=(uint64_t)count*(12+4*channels);
    if(outputBytes<12000000){
     NSMutableData *data=[NSMutableData dataWithCapacity:16+outputBytes];
     uint32_t header[4]={0x31443352,count,(uint32_t)channels,0};
     [data appendBytes:header length:16];
     [data appendBytes:xyz length:(size_t)count*12];
     [data appendBytes:attr length:(size_t)count*(size_t)channels*4];
     NSString *dest=[output stringByAppendingPathComponent:[name stringByAppendingString:@".decoded"]];
     BOOL saved=[data writeToFile:dest atomically:YES];
     meta[@"saved"]=@(saved);
     if(saved)ok++;
    }
   }else{
    meta[@"error"]=@"read-or-array-validation-failed";
   }
   // Native createSplats produces exactly three true triangle vertices + 20-byte
   // packed color/normal/material properties per R3D record.
   uintptr_t cv=(uintptr_t)entry+0xdcc8;
   const uint32_t *ci=(const uint32_t*)cv;
   if(status==0 && count>0 && count<300000 && ci[0]==0xd103c3ff && ci[1]==0x6d0823e9 && ci[9]==0xb9800816) {
    typedef int (*SplatsCreator)(const void*,void*);
    void *surface=calloc(1,0x4000);
    int code=((SplatsCreator)cv)(world,surface);
    meta[@"createSplatsStatus"]=@(code);
    uintptr_t vstart=*(uintptr_t*)((char*)surface+0x38);
    uintptr_t vend=*(uintptr_t*)((char*)surface+0x40);
    uintptr_t mstart=*(uintptr_t*)((char*)surface+0x50);
    uintptr_t mend=*(uintptr_t*)((char*)surface+0x58);
    uint64_t vbytes=vend>=vstart?(uint64_t)(vend-vstart):0;
    uint64_t mbytes=mend>=mstart?(uint64_t)(mend-mstart):0;
    meta[@"nativeTriangleBytes"]=@(vbytes);
    meta[@"nativeMaterialBytes"]=@(mbytes);
    if(code==1 && vstart>0x100000000ull && mstart>0x100000000ull &&
        vbytes==(uint64_t)count*36 && mbytes==(uint64_t)count*20) {
     NSString *vertexName=[name stringByAppendingString:@".native-triangle-f32"];
     NSString *propsName=[name stringByAppendingString:@".native-material20"];
     NSData *vertices=[NSData dataWithBytes:(const void*)vstart length:(NSUInteger)vbytes];
     NSData *materials=[NSData dataWithBytes:(const void*)mstart length:(NSUInteger)mbytes];
     BOOL ok1=[vertices writeToFile:[output stringByAppendingPathComponent:vertexName] atomically:YES];
     BOOL ok2=[materials writeToFile:[output stringByAppendingPathComponent:propsName] atomically:YES];
     meta[@"nativeTriangleSaved"]=@(ok1&&ok2);
    }else{meta[@"nativeTriangleSaved"]=@NO;}
    // Deliberately retain native vector-owned allocations until this isolated probe exits.
   }
   // Native R3D polygon source arrays, independent position/UV/normal indices.
   // Identified by xrefs in createC3mModel and validated sample.
   const int mo[]={0x2b0,0x2c8,0x2e0,0x2f8,0x310,0x328};
   const size_t stride[]={12,8,12,4,4,4};
   NSMutableArray *meshCounts=[NSMutableArray array];
   BOOL meshSaved=(status==0);
   for(int k=0;k<6;k++){
     uint64_t elementCount=*(uint64_t*)((char*)world+mo[k]+8);
     void *array=*(void**)((char*)world+mo[k]);
     [meshCounts addObject:@(elementCount)];
     if(elementCount>0 && elementCount<1000000 && array && elementCount*stride[k]<40000000){
       NSString *file=[name stringByAppendingFormat:@".c3m-%03x.bin",mo[k]];
       NSData *out=[NSData dataWithBytes:array length:(size_t)elementCount*stride[k]];
       if(![out writeToFile:[output stringByAppendingPathComponent:file] atomically:YES])meshSaved=NO;
     }else{meshSaved=NO;}
   }
   meta[@"meshArrayCounts"]=meshCounts;
   meta[@"meshSaved"]=@(meshSaved);
   meta[@"meshGroupCountCandidate"]=@(*(uint64_t*)((char*)world+0x350));
   // R3D image atlases are HEIC in the native texture-resource table.
   // md::R3dResourceDecoder::decode copies texture image bytes from +0x608
   // with length at +0x808 for each material slot.
   uint64_t textureCount=*(uint64_t*)((char*)world+0x338);
   uintptr_t textureRecords=*(uintptr_t*)((char*)world+0x340);
   NSMutableArray *textureFiles=[NSMutableArray array];
   if(status==0 && textureCount>0 && textureCount<=16 && textureRecords>0x100000000ull){
    for(uint64_t tex=0;tex<textureCount;tex++){
     const char *record=(const char*)textureRecords+tex*0x9888;
     for(uint64_t slot=0;slot<64;slot++){
      const unsigned char *src=*(const unsigned char**)(record+0x608+slot*8);
      uint64_t len=*(uint64_t*)(record+0x808+slot*8);
      if(src && (uintptr_t)src>0x100000000ull && len>=24 && len<10000000){
       BOOL heic=(memcmp(src+4,"ftyp",4)==0);
       NSString *file=[name stringByAppendingFormat:@".texture-%llu-%llu.%@",tex,slot,heic?@"heic":@"bin"];
       if([[NSData dataWithBytes:src length:(NSUInteger)len] writeToFile:[output stringByAppendingPathComponent:file] atomically:YES]){
        [textureFiles addObject:@{@"name":file,@"record":@(tex),@"slot":@(slot),@"bytes":@(len),@"heic":@(heic)}];
       }
      }
     }
    }
   }
   meta[@"nativeTextureImages"]=textureFiles;
   cleanup(world);
   free(world);
   [results addObject:meta];
  }
  if(tried%10==0){
   NSDictionary *partial=@{@"complete":@(tried),@"success":@(ok),@"files":results};
   NSData *json=[NSJSONSerialization dataWithJSONObject:partial options:NSJSONWritingPrettyPrinted error:nil];
   [json writeToFile:[output stringByAppendingPathComponent:@"batch.json"] atomically:YES];
  }
 }
 NSDictionary *report=@{@"complete":@(tried),@"success":@(ok),@"files":results};
 NSData *json=[NSJSONSerialization dataWithJSONObject:report options:NSJSONWritingPrettyPrinted error:nil];
 [json writeToFile:[output stringByAppendingPathComponent:@"batch.json"] atomically:YES];
 NSLog(@"R3D BATCH COMPLETE %ld tiles; %ld with decoded arrays",(long)tried,(long)ok);
}
- (void)save:(NSDictionary*)report {
 NSString *dir=[NSHomeDirectory() stringByAppendingPathComponent:@"Documents"];
 [[NSFileManager defaultManager] createDirectoryAtPath:dir withIntermediateDirectories:YES attributes:nil error:nil];
 NSData *json=[NSJSONSerialization dataWithJSONObject:report options:NSJSONWritingPrettyPrinted error:nil];
 [json writeToFile:[dir stringByAppendingPathComponent:@"decoder-result.json"] atomically:YES];
 NSLog(@"R3D TEST RESULT %@",report);
}
@end
@interface R3dSceneDelegate : UIResponder <UIWindowSceneDelegate>
@property (strong,nonatomic) UIWindow *window;
@end
@implementation R3dSceneDelegate
- (void)scene:(UIScene *)scene willConnectToSession:(UISceneSession *)session options:(UISceneConnectionOptions *)options {
 if (![scene isKindOfClass:[UIWindowScene class]]) return;
 self.window=[[UIWindow alloc] initWithWindowScene:(UIWindowScene*)scene];
 UIViewController *vc=[UIViewController new];
 vc.view.backgroundColor=[UIColor systemBackgroundColor];
 UILabel *label=[[UILabel alloc] initWithFrame:CGRectMake(0,100,400,140)];
 label.text=@"Running iOS27 Native R3D Decoder";
 [vc.view addSubview:label];self.window.rootViewController=vc;[self.window makeKeyAndVisible];
 DecoderDelegate *app=(DecoderDelegate*)UIApplication.sharedApplication.delegate;
 [app performSelector:@selector(runDecode) withObject:nil afterDelay:2.0];
}
@end
int main(int argc,char**argv){@autoreleasepool{return UIApplicationMain(argc,argv,nil,NSStringFromClass([DecoderDelegate class]));}}
