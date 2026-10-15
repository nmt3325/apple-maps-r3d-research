// Read the identity and code fingerprint of VectorKit loaded in this process.
// Extractors can rewrite Mach-O segment headers: do not infer dyld slide by
// subtracting an extracted segment base from a sample report's image base.
#import <Foundation/Foundation.h>
#import <CommonCrypto/CommonDigest.h>
#include <mach-o/dyld.h>
#include <mach-o/loader.h>
#include <dlfcn.h>
#include <uuid/uuid.h>

static NSString *hexAddress(uint64_t value) {return [NSString stringWithFormat:@"0x%llx",(unsigned long long)value];}

int main() {
    @autoreleasepool {
        void *handle=dlopen("/System/Library/PrivateFrameworks/VectorKit.framework/Versions/A/VectorKit",RTLD_LAZY);
        if(!handle){fprintf(stderr,"%s\n",dlerror());return 1;}
        for(uint32_t i=0;i<_dyld_image_count();i++){
            const char *name=_dyld_get_image_name(i);
            if(!strstr(name,"/VectorKit.framework/") || ![[NSString stringWithUTF8String:name] hasSuffix:@"/VectorKit"])continue;
            const struct mach_header_64 *header=(const struct mach_header_64 *)_dyld_get_image_header(i);
            intptr_t slide=_dyld_get_image_vmaddr_slide(i);
            if(header->magic!=MH_MAGIC_64)return 2;
            NSMutableDictionary *result=[@{@"scope":@"Separate process loading the system VectorKit; not Maps.app attachment",
                @"path":@(name),@"live_header":hexAddress((uintptr_t)header),@"dyld_slide":hexAddress(slide)} mutableCopy];
            const char *cursor=(const char *)(header+1);
            for(uint32_t c=0;c<header->ncmds;c++){
                const struct load_command *command=(const struct load_command *)cursor;
                if(command->cmd==LC_UUID){
                    char value[37];uuid_unparse_upper(((const struct uuid_command *)command)->uuid,value);result[@"uuid"]=@(value);
                }else if(command->cmd==LC_SEGMENT_64){
                    const struct segment_command_64 *segment=(const struct segment_command_64 *)command;
                    if(!strncmp(segment->segname,"__TEXT",16))result[@"original_text_segment_vmaddr"]=hexAddress(segment->vmaddr);
                    const struct section_64 *sections=(const struct section_64 *)(segment+1);
                    for(uint32_t s=0;s<segment->nsects;s++){
                        if(strncmp(sections[s].sectname,"__text",16))continue;
                        result[@"text_section_vmaddr"]=hexAddress(sections[s].addr);
                        size_t length=MIN((uint64_t)4096,sections[s].size);
                        unsigned char hash[CC_SHA256_DIGEST_LENGTH];
                        CC_SHA256((const void *)(sections[s].addr+slide),(CC_LONG)length,hash);
                        NSMutableString *value=[NSMutableString string];
                        for(size_t h=0;h<sizeof(hash);h++)[value appendFormat:@"%02x",hash[h]];
                        result[@"live_text_prefix4096_sha256"]=value;
                    }
                }
                cursor+=command->cmdsize;
            }
            NSData *json=[NSJSONSerialization dataWithJSONObject:result options:NSJSONWritingPrettyPrinted|NSJSONWritingSortedKeys error:nil];
            fwrite(json.bytes,1,json.length,stdout);fputc('\n',stdout);return 0;
        }
        return 3;
    }
}
