// An instrumented, disposable MapKit host. Does not inject into Maps.app.
// Build/run instructions are in ../README.md. Raw data belongs in reports/generated/.
#import <AppKit/AppKit.h>
#import <MapKit/MapKit.h>
#import <Metal/Metal.h>
#import <objc/runtime.h>
#import <mach-o/dyld.h>
#import <mach/mach.h>
#include <mutex>
#include <atomic>
#include <cmath>

static NSString *outputDir;
static NSFileHandle *events;
static std::recursive_mutex lock;
static NSMutableDictionary<NSNumber *, id<MTLBuffer>> *buffers;
static NSMutableSet<NSString *> *seenPipelines;
static NSMutableSet<NSString *> *seenDraws;
static NSMutableSet<NSString *> *seenConstants;
static NSMutableSet<NSString *> *seenBindings;
static NSMutableSet<NSString *> *seenPasses;
static NSMutableDictionary<NSString *,NSNumber *> *pipelineDraws;
static id<MTLDevice> renderingDevice;
static char pipelineKey, encoderKey, bindingKey, constantKey, passKey;
static NSUInteger maxEvents = 12000, eventCount = 0, dumpCount = 0;
static NSUInteger registeredBytes = 0;
static std::atomic<uint64_t> drawCount{0};
static std::atomic<uint64_t> constantSetCount{0};

static void emit(NSString *kind, NSDictionary *fields) {
    std::lock_guard<std::recursive_mutex> guard(lock);
    if (eventCount++ >= maxEvents) return;
    NSMutableDictionary *row = [fields mutableCopy];
    row[@"event"] = kind;
    row[@"uptime"] = @(NSProcessInfo.processInfo.systemUptime);
    NSData *data = [NSJSONSerialization dataWithJSONObject:row options:NSJSONWritingSortedKeys error:nil];
    if (data) { [events writeData:data]; [events writeData:[@"\n" dataUsingEncoding:NSUTF8StringEncoding]]; }
}

static NSString *ptr(id obj) { return [NSString stringWithFormat:@"%p", (__bridge void *)obj]; }

static void remember(id<MTLBuffer> b) {
    if (!b) return;
    std::lock_guard<std::recursive_mutex> guard(lock);
    // Bounded retention deliberately changes resource lifetime; report that limitation.
    // All references are released at process exit. Only this disposable host is affected.
    if (buffers[@(b.gpuAddress)]) return;
    if (buffers.count < 24000 && b.length <= 512*1024*1024 - registeredBytes) {
        buffers[@(b.gpuAddress)] = b;
        registeredBytes += b.length;
    }
}

static NSDictionary *bufferInfo(id<MTLBuffer> b, NSUInteger offset) {
    if (!b) return @{};
    return @{@"object":ptr(b), @"gpu_address":@(b.gpuAddress), @"length":@(b.length),
             @"offset":@(offset), @"storage_mode":@(b.storageMode), @"label":b.label ?: @""};
}

static NSData *readBuffer(id<MTLBuffer> b, NSUInteger offset, NSUInteger length) {
    if (!b || b.storageMode == MTLStorageModePrivate || b.storageMode == MTLStorageModeMemoryless ||
        offset > b.length || length > b.length - offset) return nil;
    void *p = b.contents;
    return p ? [NSData dataWithBytes:(const char *)p + offset length:length] : nil;
}

static NSString *saveData(NSData *data, NSString *stem) {
    if (!data || dumpCount >= 160) return @"";
    NSString *name = [NSString stringWithFormat:@"%04lu-%@.bin", (unsigned long)dumpCount++, stem];
    [data writeToFile:[outputDir stringByAppendingPathComponent:name] atomically:YES];
    return name;
}

static NSDictionary *resolve(uint64_t address) {
    id<MTLBuffer> b = buffers[@(address)];
    if (b) return @{@"buffer":b, @"offset":@0};
    for (NSNumber *base in buffers) {
        uint64_t a = base.unsignedLongLongValue;
        b = buffers[base];
        if (address >= a && address - a < b.length)
            return @{@"buffer":b, @"offset":@(address - a)};
    }
    return nil;
}

static void inspectDraw(id encoder, NSDictionary *draw) {
    ++drawCount;
    std::lock_guard<std::recursive_mutex> guard(lock);
    NSString *pipeline = objc_getAssociatedObject(encoder, &encoderKey) ?: @"unknown";
    NSString *lower = pipeline.lowercaseString;
    BOOL relevant = [lower containsString:@"splat_vertex"] && [lower containsString:@"splat_fragment"];
    pipelineDraws[pipeline]=@([pipelineDraws[pipeline] unsignedLongLongValue]+1);
    NSString *key = [NSString stringWithFormat:@"%@/%@", pipeline, draw];
    if (![seenDraws containsObject:key] && seenDraws.count < 1000) {
        [seenDraws addObject:key];
        emit(@"draw", @{@"pipeline":pipeline, @"arguments":draw});
    }
    if (!relevant) return;
    NSDictionary *pass=objc_getAssociatedObject(encoder,&passKey);
    if(pass){
        NSString *passID=pass.description;
        if(![seenPasses containsObject:passID]){[seenPasses addObject:passID];emit(@"splat_render_pass",pass);}
    }
    NSDictionary *bindings = objc_getAssociatedObject(encoder, &bindingKey);
    for (NSNumber *index in bindings) {
        NSDictionary *binding = bindings[index];
        id<MTLBuffer> arg = binding[@"buffer"];
        NSUInteger argOffset = [binding[@"offset"] unsignedIntegerValue];
        NSData *pointers = readBuffer(arg, argOffset, MIN((NSUInteger)32, arg.length - MIN(argOffset, arg.length)));
        NSString *bindingID=[NSString stringWithFormat:@"%@/%@/%@/%lu",pipeline,index,ptr(arg),(unsigned long)argOffset];
        if(![seenBindings containsObject:bindingID] && seenBindings.count<60){
            [seenBindings addObject:bindingID];
            NSData *head=readBuffer(arg,argOffset,MIN((NSUInteger)256,arg.length-MIN(argOffset,arg.length)));
            emit(@"vertex_binding",@{@"pipeline":pipeline,@"index":index,@"buffer":bufferInfo(arg,argOffset),@"head_file":saveData(head,@"vertex-binding")});
        }
        if (index.unsignedIntegerValue != 0 || pointers.length < 16) continue;
        uint64_t addresses[2]; memcpy(addresses, pointers.bytes, 16);
        // Verified reflection: sharedArgBuffer {constants@0, splatConstants@8}.
        NSDictionary *resolved = resolve(addresses[1]);
        if (!resolved) continue;
        id<MTLBuffer> uniform = resolved[@"buffer"];
        NSUInteger uniformOffset = [resolved[@"offset"] unsignedIntegerValue];
        NSData *data = readBuffer(uniform, uniformOffset, 256);
        if (data.length != 256) continue;
        float c, p; int32_t splatID;
        memcpy(&splatID, (const char *)data.bytes + 192, 4);
        memcpy(&c, (const char *)data.bytes + 196, 4);
        memcpy(&p, (const char *)data.bytes + 200, 4);
        // Do not infer validity from plausibility alone: pipeline + reflection + pointer bounds are required.
        NSString *uniformKey = [NSString stringWithFormat:@"%@/%d/%a/%a", pipeline, splatID, c, p];
        if ([seenConstants containsObject:uniformKey] || seenConstants.count >= 120) continue;
        [seenConstants addObject:uniformKey];
        NSMutableDictionary *fields = [@{@"pipeline":pipeline, @"index":index,
            @"argument_buffer":bufferInfo(arg,argOffset), @"uniform_buffer":bufferInfo(uniform,uniformOffset),
            @"splat_id":@(splatID), @"uniform_file":saveData(data,@"splat-constants"),
            @"finite_alpha_values":@(std::isfinite(c) && std::isfinite(p))} mutableCopy];
        if (std::isfinite(c)) fields[@"alpha_concentration"] = @(c);
        if (std::isfinite(p)) fields[@"alpha_pre_factor"] = @(p);
        emit(@"candidate_splat_constants", fields);
        // Bindless table has three arrays of 16384 eight-byte GPU addresses.
        NSDictionary *tableBinding=bindings[@1];
        id<MTLBuffer> table=tableBinding[@"buffer"];
        NSUInteger tableOffset=[tableBinding[@"offset"] unsignedIntegerValue];
        if(splatID>=0 && splatID<16384){
            NSArray *names=@[@"positions-ushort4",@"properties-12",@"orders-int32"];
            for(NSUInteger array=0;array<3;array++){
                NSData *entry=readBuffer(table,tableOffset+array*131072+(NSUInteger)splatID*8,8);
                if(entry.length!=8)continue;
                uint64_t addr;memcpy(&addr,entry.bytes,8);
                NSDictionary *r=resolve(addr);
                if(!r){emit(@"unresolved_resource",@{@"splat_id":@(splatID),@"kind":names[array],@"gpu_address":@(addr)});continue;}
                id<MTLBuffer> resource=r[@"buffer"];NSUInteger off=[r[@"offset"] unsignedIntegerValue];
                NSUInteger size=MIN((NSUInteger)(512*1024),resource.length-off);
                NSData *bytes=readBuffer(resource,off,size);
                emit(@"splat_resource",@{@"splat_id":@(splatID),@"kind":names[array],@"buffer":bufferInfo(resource,off),
                    @"file":saveData(bytes,names[array]),@"saved_bytes":@(bytes.length),@"complete":@(size==resource.length-off)});
            }
        }
    }
}

static void recordBinding(id obj,id<MTLBuffer> buffer,NSUInteger offset,NSUInteger index) {
    remember(buffer);
    std::lock_guard<std::recursive_mutex> guard(lock);
    NSMutableDictionary *b=objc_getAssociatedObject(obj,&bindingKey);
    if(!b){b=[NSMutableDictionary dictionary];objc_setAssociatedObject(obj,&bindingKey,b,OBJC_ASSOCIATION_RETAIN_NONATOMIC);}
    if(buffer) b[@(index)]=@{@"buffer":buffer,@"offset":@(offset)};else [b removeObjectForKey:@(index)];
}

static void replace(Class cls, SEL sel, id block) {
    Method method = class_getInstanceMethod(cls, sel);
    if (!method) { emit(@"missing_method", @{@"class":NSStringFromClass(cls),@"selector":NSStringFromSelector(sel)}); return; }
    const char *types = method_getTypeEncoding(method);
    IMP impl = imp_implementationWithBlock(block);
    if (!class_addMethod(cls, sel, impl, types)) class_replaceMethod(cls, sel, impl, types);
}

static NSString *pipelineName(MTLRenderPipelineDescriptor *d) {
    return [NSString stringWithFormat:@"%@ | %@ | %@", d.label ?: @"", d.vertexFunction.name ?: @"", d.fragmentFunction.name ?: @""];
}

static NSUInteger constantSize(MTLDataType type) {
    switch(type){case MTLDataTypeBool:return 1;case MTLDataTypeInt:case MTLDataTypeUInt:case MTLDataTypeFloat:return 4;default:return 0;}
}

static void rememberConstant(id obj,const void *value,MTLDataType type,NSString *key) {
    NSUInteger length=constantSize(type);if(!length || !value)return;
    ++constantSetCount;
    std::lock_guard<std::recursive_mutex> guard(lock);
    NSMutableDictionary *values=objc_getAssociatedObject(obj,&constantKey);
    if(!values){values=[NSMutableDictionary dictionary];objc_setAssociatedObject(obj,&constantKey,values,OBJC_ASSOCIATION_RETAIN_NONATOMIC);}
    values[key]=@{@"metal_type":@(type),@"hex":[[NSData dataWithBytes:value length:length] description]};
}

static void installConstantHooks(id<MTLDevice> device) {
    MTLFunctionConstantValues *v=[MTLFunctionConstantValues new];Class vc=object_getClass(v);
    SEL copy=@selector(copyWithZone:);
    auto origCopy=(id(*)(id,SEL,NSZone*))class_getMethodImplementation(vc,copy);
    replace(vc,copy,^id(id obj,NSZone *zone){
        id result=origCopy(obj,copy,zone);
        std::lock_guard<std::recursive_mutex> guard(lock);
        NSDictionary *values=objc_getAssociatedObject(obj,&constantKey);
        if(values)objc_setAssociatedObject(result,&constantKey,[values mutableCopy],OBJC_ASSOCIATION_RETAIN_NONATOMIC);
        return result;
    });
    SEL reset=@selector(reset);
    auto origReset=(void(*)(id,SEL))class_getMethodImplementation(vc,reset);
    replace(vc,reset,^(id obj){objc_setAssociatedObject(obj,&constantKey,nil,OBJC_ASSOCIATION_RETAIN_NONATOMIC);origReset(obj,reset);});
    SEL one=@selector(setConstantValue:type:atIndex:);
    auto origOne=(void(*)(id,SEL,const void*,MTLDataType,NSUInteger))class_getMethodImplementation(vc,one);
    replace(vc,one,^(id obj,const void *value,MTLDataType type,NSUInteger index){
        rememberConstant(obj,value,type,[NSString stringWithFormat:@"index:%lu",(unsigned long)index]);origOne(obj,one,value,type,index);
    });
    SEL named=@selector(setConstantValue:type:withName:);
    auto origNamed=(void(*)(id,SEL,const void*,MTLDataType,NSString*))class_getMethodImplementation(vc,named);
    replace(vc,named,^(id obj,const void *value,MTLDataType type,NSString *name){
        rememberConstant(obj,value,type,name);origNamed(obj,named,value,type,name);
    });
    SEL many=@selector(setConstantValues:type:withRange:);
    auto origMany=(void(*)(id,SEL,const void*,MTLDataType,NSRange))class_getMethodImplementation(vc,many);
    replace(vc,many,^(id obj,const void *value,MTLDataType type,NSRange range){
        NSUInteger size=constantSize(type);
        if(size)for(NSUInteger i=0;i<range.length;i++)rememberConstant(obj,(const char *)value+i*size,type,[NSString stringWithFormat:@"index:%lu",(unsigned long)(range.location+i)]);
        origMany(obj,many,value,type,range);
    });
    NSError *error=nil;
    NSURL *url=[NSURL fileURLWithPath:@"/System/Library/PrivateFrameworks/VectorKit.framework/Versions/A/Resources/default.metallib"];
    id<MTLLibrary> lib=[device newLibraryWithURL:url error:&error];
    if(!lib){emit(@"library_error",@{@"error":error.localizedDescription ?: @""});return;}
    Class lc=object_getClass(lib);
    SEL function=@selector(newFunctionWithName:constantValues:error:);
    auto origFunction=(id(*)(id,SEL,NSString*,id,NSError**))class_getMethodImplementation(lc,function);
    replace(lc,function,^id(id obj,NSString *name,MTLFunctionConstantValues *values,NSError **err){
        id f=origFunction(obj,function,name,values,err);
        if([name hasPrefix:@"Flyover::"]){
            NSDictionary *record=objc_getAssociatedObject(values,&constantKey) ?: @{};
            emit(@"function_specialized",@{@"name":name,@"constants":record,@"success":@(f!=nil),@"api":@"name"});
        }
        return f;
    });
    SEL descriptor=@selector(newFunctionWithDescriptor:error:);
    auto origDescriptor=(id(*)(id,SEL,MTLFunctionDescriptor*,NSError**))class_getMethodImplementation(lc,descriptor);
    replace(lc,descriptor,^id(id obj,MTLFunctionDescriptor *d,NSError **err){
        id f=origDescriptor(obj,descriptor,d,err);
        if([d.name hasPrefix:@"Flyover::"]){
            NSDictionary *record=objc_getAssociatedObject(d.constantValues,&constantKey) ?: @{};
            emit(@"function_specialized",@{@"name":d.name,@"constants":record,@"success":@(f!=nil),@"api":@"descriptor"});
        }
        return f;
    });
    emit(@"constant_hooks",@{@"values_class":NSStringFromClass(vc),@"library_class":NSStringFromClass(lc)});
}

static void installHooks(id<MTLDevice> device) {
    Class dc = object_getClass(device);
    SEL make = @selector(newBufferWithLength:options:);
    auto origMake = (id(*)(id,SEL,NSUInteger,MTLResourceOptions))class_getMethodImplementation(dc,make);
    replace(dc,make,^id(id obj,NSUInteger length,MTLResourceOptions options){
        id b=origMake(obj,make,length,options); remember(b); return b;
    });
    SEL copy = @selector(newBufferWithBytes:length:options:);
    auto origCopy = (id(*)(id,SEL,const void*,NSUInteger,MTLResourceOptions))class_getMethodImplementation(dc,copy);
    replace(dc,copy,^id(id obj,const void *bytes,NSUInteger length,MTLResourceOptions options){
        id b=origCopy(obj,copy,bytes,length,options); remember(b); return b;
    });
    SEL noCopy=@selector(newBufferWithBytesNoCopy:length:options:deallocator:);
    auto origNoCopy=(id(*)(id,SEL,void*,NSUInteger,MTLResourceOptions,id))class_getMethodImplementation(dc,noCopy);
    replace(dc,noCopy,^id(id obj,void *bytes,NSUInteger length,MTLResourceOptions options,id deallocator){
        id b=origNoCopy(obj,noCopy,bytes,length,options,deallocator);remember(b);return b;
    });
    SEL pipe = @selector(newRenderPipelineStateWithDescriptor:options:reflection:error:);
    auto origPipe = (id(*)(id,SEL,id,MTLPipelineOption,MTLRenderPipelineReflection **,NSError **))class_getMethodImplementation(dc,pipe);
    replace(dc,pipe,^id(id obj,MTLRenderPipelineDescriptor *desc,MTLPipelineOption options,MTLRenderPipelineReflection **reflection,NSError **error){
        id state=origPipe(obj,pipe,desc,options,reflection,error);
        if(state) objc_setAssociatedObject(state,&pipelineKey,pipelineName(desc),OBJC_ASSOCIATION_COPY_NONATOMIC);
        emit(@"pipeline_created",@{@"name":pipelineName(desc),@"success":@(state!=nil)});return state;
    });

    MTLTextureDescriptor *td=[MTLTextureDescriptor texture2DDescriptorWithPixelFormat:MTLPixelFormatBGRA8Unorm width:4 height:4 mipmapped:NO];
    td.usage=MTLTextureUsageRenderTarget;
    id<MTLTexture> tex=[device newTextureWithDescriptor:td];
    MTLRenderPassDescriptor *rp=[MTLRenderPassDescriptor renderPassDescriptor];
    rp.colorAttachments[0].texture=tex;rp.colorAttachments[0].loadAction=MTLLoadActionClear;rp.colorAttachments[0].storeAction=MTLStoreActionDontCare;
    id<MTLCommandQueue> queue=[device newCommandQueue];
    id<MTLCommandBuffer> command=[queue commandBuffer];
    id<MTLRenderCommandEncoder> encoder=[command renderCommandEncoderWithDescriptor:rp];
    Class ec=object_getClass(encoder);
    Class cc=object_getClass(command);
    SEL makeEncoder=@selector(renderCommandEncoderWithDescriptor:);
    auto origMakeEncoder=(id(*)(id,SEL,MTLRenderPassDescriptor*))class_getMethodImplementation(cc,makeEncoder);
    replace(cc,makeEncoder,^id(id obj,MTLRenderPassDescriptor *desc){
        id e=origMakeEncoder(obj,makeEncoder,desc);
        id<MTLTexture> color=desc.colorAttachments[0].texture;
        id<MTLTexture> depth=desc.depthAttachment.texture;
        NSDictionary *info=@{@"imageblock_sample_length":@(desc.imageblockSampleLength),@"tile_width":@(desc.tileWidth),@"tile_height":@(desc.tileHeight),
            @"color_format":@(color.pixelFormat),@"width":@(color.width),@"height":@(color.height),@"sample_count":@(color.sampleCount),
            @"color_storage_mode":@(color.storageMode),@"color_load_action":@(desc.colorAttachments[0].loadAction),
            @"color_store_action":@(desc.colorAttachments[0].storeAction),@"depth_format":@(depth.pixelFormat)};
        if(e)objc_setAssociatedObject(e,&passKey,info,OBJC_ASSOCIATION_RETAIN_NONATOMIC);
        return e;
    });
    emit(@"hooks",@{@"device_class":NSStringFromClass(dc),@"encoder_class":NSStringFromClass(ec)});
    SEL setPipe=@selector(setRenderPipelineState:);
    auto origSetPipe=(void(*)(id,SEL,id))class_getMethodImplementation(ec,setPipe);
    replace(ec,setPipe,^(id obj,id<MTLRenderPipelineState> state){
        NSString *name=objc_getAssociatedObject(state,&pipelineKey) ?: state.label ?: @"unlabelled";
        objc_setAssociatedObject(obj,&encoderKey,name,OBJC_ASSOCIATION_COPY_NONATOMIC);
        { std::lock_guard<std::recursive_mutex> guard(lock);
          if([name containsString:@"Flyover::splat_vertex"])renderingDevice=state.device;
          if(![seenPipelines containsObject:name]){[seenPipelines addObject:name];emit(@"pipeline_bound",@{@"name":name,@"label":state.label ?: @"",@"device":ptr(state.device)});} }
        origSetPipe(obj,setPipe,state);
    });
    SEL bind=@selector(setVertexBuffer:offset:atIndex:);
    auto origBind=(void(*)(id,SEL,id,NSUInteger,NSUInteger))class_getMethodImplementation(ec,bind);
    replace(ec,bind,^(id obj,id<MTLBuffer> buffer,NSUInteger offset,NSUInteger index){
        recordBinding(obj,buffer,offset,index);
        origBind(obj,bind,buffer,offset,index);
    });
    SEL binds=@selector(setVertexBuffers:offsets:withRange:);
    auto origBinds=(void(*)(id,SEL,const id<MTLBuffer>*,const NSUInteger*,NSRange))class_getMethodImplementation(ec,binds);
    replace(ec,binds,^(id obj,const id<MTLBuffer> *values,const NSUInteger *offsets,NSRange range){
        for(NSUInteger i=0;i<range.length;i++)recordBinding(obj,values[i],offsets[i],range.location+i);
        origBinds(obj,binds,values,offsets,range);
    });
    SEL offset=@selector(setVertexBufferOffset:atIndex:);
    auto origOffset=(void(*)(id,SEL,NSUInteger,NSUInteger))class_getMethodImplementation(ec,offset);
    replace(ec,offset,^(id obj,NSUInteger value,NSUInteger index){
        std::lock_guard<std::recursive_mutex> guard(lock);
        NSDictionary *b=objc_getAssociatedObject(obj,&bindingKey);
        id<MTLBuffer> buffer=b[@(index)][@"buffer"];
        if(buffer)recordBinding(obj,buffer,value,index);
        origOffset(obj,offset,value,index);
    });
    SEL resources=@selector(useResources:count:usage:stages:);
    auto origResources=(void(*)(id,SEL,const id<MTLResource>*,NSUInteger,MTLResourceUsage,MTLRenderStages))class_getMethodImplementation(ec,resources);
    replace(ec,resources,^(id obj,const id<MTLResource> *values,NSUInteger count,MTLResourceUsage usage,MTLRenderStages stages){
        for(NSUInteger i=0;i<count;i++)if([values[i] conformsToProtocol:@protocol(MTLBuffer)])remember((id<MTLBuffer>)values[i]);
        origResources(obj,resources,values,count,usage,stages);
    });
    SEL resource=@selector(useResource:usage:stages:);
    auto origResource=(void(*)(id,SEL,id,MTLResourceUsage,MTLRenderStages))class_getMethodImplementation(ec,resource);
    replace(ec,resource,^(id obj,id<MTLResource> value,MTLResourceUsage usage,MTLRenderStages stages){
        if([value conformsToProtocol:@protocol(MTLBuffer)])remember((id<MTLBuffer>)value);
        origResource(obj,resource,value,usage,stages);
    });
    SEL draw=@selector(drawPrimitives:vertexStart:vertexCount:);
    auto origDraw=(void(*)(id,SEL,MTLPrimitiveType,NSUInteger,NSUInteger))class_getMethodImplementation(ec,draw);
    replace(ec,draw,^(id obj,MTLPrimitiveType type,NSUInteger start,NSUInteger count){
        inspectDraw(obj,@{@"kind":@"primitives",@"type":@(type),@"start":@(start),@"count":@(count)});
        origDraw(obj,draw,type,start,count);
    });
    SEL drawI=@selector(drawPrimitives:vertexStart:vertexCount:instanceCount:);
    auto origDrawI=(void(*)(id,SEL,MTLPrimitiveType,NSUInteger,NSUInteger,NSUInteger))class_getMethodImplementation(ec,drawI);
    replace(ec,drawI,^(id obj,MTLPrimitiveType type,NSUInteger start,NSUInteger count,NSUInteger instances){
        inspectDraw(obj,@{@"kind":@"instanced",@"type":@(type),@"start":@(start),@"count":@(count),@"instances":@(instances)});
        origDrawI(obj,drawI,type,start,count,instances);
    });
    SEL drawBase=@selector(drawPrimitives:vertexStart:vertexCount:instanceCount:baseInstance:);
    auto origDrawBase=(void(*)(id,SEL,MTLPrimitiveType,NSUInteger,NSUInteger,NSUInteger,NSUInteger))class_getMethodImplementation(ec,drawBase);
    replace(ec,drawBase,^(id obj,MTLPrimitiveType type,NSUInteger start,NSUInteger count,NSUInteger instances,NSUInteger base){
        inspectDraw(obj,@{@"kind":@"instanced_base",@"type":@(type),@"start":@(start),@"count":@(count),@"instances":@(instances),@"base_instance":@(base)});
        origDrawBase(obj,drawBase,type,start,count,instances,base);
    });
    SEL indexed=@selector(drawIndexedPrimitives:indexCount:indexType:indexBuffer:indexBufferOffset:);
    auto origIndexed=(void(*)(id,SEL,MTLPrimitiveType,NSUInteger,MTLIndexType,id,NSUInteger))class_getMethodImplementation(ec,indexed);
    replace(ec,indexed,^(id obj,MTLPrimitiveType type,NSUInteger count,MTLIndexType indexType,id buffer,NSUInteger offset){
        inspectDraw(obj,@{@"kind":@"indexed",@"type":@(type),@"count":@(count),@"index_type":@(indexType)});
        origIndexed(obj,indexed,type,count,indexType,buffer,offset);
    });
    [encoder endEncoding];[command commit];[command waitUntilCompleted];
}

@interface ProbeDelegate : NSObject<NSApplicationDelegate,MKMapViewDelegate>
@property NSWindow *window;
@property MKMapView *map;
@property double latitude, longitude, distance, pitch, duration;
@end
@implementation ProbeDelegate
- (void)applicationDidFinishLaunching:(NSNotification *)notification {
    id<MTLDevice> device=MTLCreateSystemDefaultDevice();
    emit(@"start",@{@"pid":@(getpid()),@"device":device.name ?: @"",@"os":NSProcessInfo.processInfo.operatingSystemVersionString,
        @"latitude":@(self.latitude),@"longitude":@(self.longitude),@"distance":@(self.distance),@"pitch":@(self.pitch)});
    installHooks(device);
    installConstantHooks(device);
    // Start before MapKit creates its command buffers. An idle-map capture can
    // otherwise succeed yet contain no commands. Report draw deltas at stop.
    if (getenv("MAPS_PROBE_CAPTURE")) {
        MTLCaptureDescriptor *d=[MTLCaptureDescriptor new];d.captureObject=device;d.destination=MTLCaptureDestinationGPUTraceDocument;
        d.outputURL=[NSURL fileURLWithPath:[outputDir stringByAppendingPathComponent:@"mapkit.gputrace"]];
        NSError *error=nil;BOOL ok=[MTLCaptureManager.sharedCaptureManager startCaptureWithDescriptor:d error:&error];
        emit(@"capture_start",@{@"success":@(ok),@"error":error.localizedDescription ?: @"",@"device":ptr(device),@"draw_calls_at_start":@(drawCount.load())});
    }
    self.window=[[NSWindow alloc] initWithContentRect:NSMakeRect(40,40,960,720) styleMask:NSWindowStyleMaskTitled|NSWindowStyleMaskClosable backing:NSBackingStoreBuffered defer:NO];
    self.window.title=@"MapKit R3D research probe";
    self.map=[[MKMapView alloc] initWithFrame:NSMakeRect(0,0,960,720)];
    self.map.delegate=self;
    self.map.preferredConfiguration=[[MKImageryMapConfiguration alloc] initWithElevationStyle:MKMapElevationStyleRealistic];
    self.map.showsBuildings=YES;self.map.showsUserLocation=NO;
    self.window.contentView=self.map;
    [self.window makeKeyAndOrderFront:nil];
    [NSApp activateIgnoringOtherApps:YES];
    CLLocationCoordinate2D center=CLLocationCoordinate2DMake(self.latitude,self.longitude);
    self.map.camera=[MKMapCamera cameraLookingAtCenterCoordinate:center fromDistance:self.distance pitch:self.pitch heading:0];
    [NSTimer scheduledTimerWithTimeInterval:8 repeats:NO block:^(NSTimer *){
        emit(@"capture_support",@{@"gpu_trace_document":@([MTLCaptureManager.sharedCaptureManager supportsDestination:MTLCaptureDestinationGPUTraceDocument])});
        if (MTLCaptureManager.sharedCaptureManager.isCapturing) {
            [MTLCaptureManager.sharedCaptureManager stopCapture];
            emit(@"capture_stop",@{@"draw_calls_at_stop":@(drawCount.load()),@"rendering_device":renderingDevice ? ptr(renderingDevice) : @"unobserved"});
        }
    }];
    [NSTimer scheduledTimerWithTimeInterval:self.duration repeats:NO block:^(NSTimer *){
        task_vm_info_data_t vm={};mach_msg_type_number_t count=TASK_VM_INFO_COUNT;
        kern_return_t status=task_info(mach_task_self(),TASK_VM_INFO,(task_info_t)&vm,&count);
        {
            std::lock_guard<std::recursive_mutex> guard(lock);
            NSMutableDictionary *summary=[@{@"draw_calls":@(drawCount.load()),@"registered_buffers":@(buffers.count),
                @"registered_buffer_bytes":@(registeredBytes),@"metal_current_allocated_size":@(device.currentAllocatedSize),
                @"pipelines":@(seenPipelines.count),@"candidate_constants":@(seenConstants.count),
                @"constant_set_calls":@(constantSetCount.load()),@"draw_calls_per_pipeline":pipelineDraws} mutableCopy];
            if(status==KERN_SUCCESS){summary[@"physical_footprint_bytes"]=@(vm.phys_footprint);summary[@"resident_size_bytes"]=@(vm.resident_size);}
            emit(@"summary",summary);
        }
        for(uint32_t i=0;i<_dyld_image_count();i++){
            const char *name=_dyld_get_image_name(i);
            if(strstr(name,"VectorKit") || strstr(name,"AGXMetal")) emit(@"image",@{@"path":@(name),@"slide":@(_dyld_get_image_vmaddr_slide(i))});
        }
        [events synchronizeFile];[NSApp terminate:nil];
    }];
}
- (void)mapViewDidFinishRenderingMap:(MKMapView *)mapView fullyRendered:(BOOL)fullyRendered {
    emit(@"map_rendered",@{@"fully_rendered":@(fullyRendered),@"pitch":@(mapView.camera.pitch),@"distance":@(mapView.camera.centerCoordinateDistance)});
}
- (void)mapViewDidFailLoadingMap:(MKMapView *)mapView withError:(NSError *)error {
    emit(@"map_error",@{@"domain":error.domain,@"code":@(error.code),@"description":error.localizedDescription});
}
@end

int main(int argc,const char *argv[]) {
    @autoreleasepool {
        if(argc<2){fprintf(stderr,"usage: mapkit_probe OUTPUT_DIR [duration_s [lat lon distance pitch]]\n");return 2;}
        outputDir=@(argv[1]);
        [NSFileManager.defaultManager createDirectoryAtPath:outputDir withIntermediateDirectories:YES attributes:nil error:nil];
        NSString *log=[outputDir stringByAppendingPathComponent:@"events.jsonl"];
        if([NSFileManager.defaultManager fileExistsAtPath:log]){fprintf(stderr,"refusing to overwrite events.jsonl\n");return 2;}
        [NSFileManager.defaultManager createFileAtPath:log contents:nil attributes:nil];
        events=[NSFileHandle fileHandleForWritingAtPath:log];
        buffers=[NSMutableDictionary dictionary];seenPipelines=[NSMutableSet set];seenDraws=[NSMutableSet set];seenConstants=[NSMutableSet set];seenBindings=[NSMutableSet set];seenPasses=[NSMutableSet set];pipelineDraws=[NSMutableDictionary dictionary];
        NSApplication *app=NSApplication.sharedApplication;[app setActivationPolicy:NSApplicationActivationPolicyRegular];
        ProbeDelegate *delegate=[ProbeDelegate new];delegate.duration=argc>2?atof(argv[2]):24;
        delegate.latitude=argc>3?atof(argv[3]):35.6586;delegate.longitude=argc>4?atof(argv[4]):139.7454;
        delegate.distance=argc>5?atof(argv[5]):900;delegate.pitch=argc>6?atof(argv[6]):65;
        app.delegate=delegate;[app run];
    }
}
