#import <Foundation/Foundation.h>
NS_ASSUME_NONNULL_BEGIN
@interface R3DPythonBridge : NSObject
+ (nullable NSDictionary<NSString *, NSData *> *)invoke:(NSString *)function
    data:(NSData *)data error:(NSError **)error;
+ (nullable NSData *)encrypt:(NSData *)data key:(NSData *)key error:(NSError **)error;
@end
NS_ASSUME_NONNULL_END
