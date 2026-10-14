#import "PythonBridge.h"
#include <Python/Python.h>
#include <CommonCrypto/CommonCryptor.h>

@implementation R3DPythonBridge
+ (BOOL)initializeRuntime:(NSError **)error {
    static dispatch_once_t once;
    static NSString *failure;
    dispatch_once(&once, ^{
        NSString *base = NSBundle.mainBundle.resourcePath;
        PyPreConfig pre;
        PyPreConfig_InitIsolatedConfig(&pre);
        pre.utf8_mode = 1;
        PyStatus status = Py_PreInitialize(&pre);
        PyConfig config;
        PyConfig_InitIsolatedConfig(&config);
        config.buffered_stdio = 0;
        config.write_bytecode = 0;
        config.install_signal_handlers = 0;
        config.module_search_paths_set = 1;
        if (!PyStatus_Exception(status))
            status = PyConfig_SetBytesString(&config, &config.home,
                [[base stringByAppendingPathComponent:@"python"] UTF8String]);
        for (NSString *path in @[@"python/lib/python3.13", @"python/lib/python3.13/lib-dynload", @"app"]) {
            wchar_t *wide = Py_DecodeLocale([[base stringByAppendingPathComponent:path] UTF8String], NULL);
            if (wide && !PyStatus_Exception(status))
                status = PyWideStringList_Append(&config.module_search_paths, wide);
            PyMem_RawFree(wide);
        }
        if (!PyStatus_Exception(status)) status = Py_InitializeFromConfig(&config);
        if (PyStatus_Exception(status)) failure = @"端末内の復号エンジンを起動できませんでした";
        PyConfig_Clear(&config);
        if (!failure) PyEval_SaveThread();
    });
    if (failure && error) *error = [NSError errorWithDomain:@"R3D" code:1
        userInfo:@{NSLocalizedDescriptionKey:failure}];
    return failure == nil;
}
+ (NSDictionary<NSString *, NSData *> *)invoke:(NSString *)function data:(NSData *)data error:(NSError **)error {
    if (![self initializeRuntime:error]) return nil;
    PyGILState_STATE gil = PyGILState_Ensure();
    PyObject *module = PyImport_ImportModule("r3d_mobile");
    PyObject *call = module ? PyObject_GetAttrString(module, function.UTF8String) : NULL;
    PyObject *input = PyBytes_FromStringAndSize(data.bytes, (Py_ssize_t)data.length);
    PyObject *result = call && input ? PyObject_CallOneArg(call, input) : NULL;
    NSMutableDictionary *out = nil;
    if (result && PyDict_Check(result)) {
        out = [NSMutableDictionary dictionary];
        PyObject *key, *value;
        Py_ssize_t at = 0;
        while (PyDict_Next(result, &at, &key, &value)) {
            if (!PyUnicode_Check(key) || !PyBytes_Check(value)) continue;
            const char *name = PyUnicode_AsUTF8(key);
            if (name) out[@(name)] = [NSData dataWithBytes:PyBytes_AS_STRING(value)
                length:(NSUInteger)PyBytes_GET_SIZE(value)];
        }
    } else {
        PyObject *type = NULL, *value = NULL, *trace = NULL;
        PyErr_Fetch(&type, &value, &trace);
        PyErr_NormalizeException(&type, &value, &trace);
        PyObject *message = value ? PyObject_Str(value) : NULL;
        const char *utf8 = message ? PyUnicode_AsUTF8(message) : NULL;
        NSString *detail = utf8 ? @(utf8) : @"Unsupported decoder response";
        if (error) *error = [NSError errorWithDomain:@"R3D" code:2
            userInfo:@{NSLocalizedDescriptionKey:[@"3D データ復号失敗: " stringByAppendingString:detail]}];
        Py_XDECREF(message); Py_XDECREF(type); Py_XDECREF(value); Py_XDECREF(trace);
        PyErr_Clear();
    }
    Py_XDECREF(result); Py_XDECREF(input); Py_XDECREF(call); Py_XDECREF(module);
    PyGILState_Release(gil);
    return out;
}
+ (NSData *)encrypt:(NSData *)data key:(NSData *)key error:(NSError **)error {
    if (key.length != 32) return nil;
    NSMutableData *cipher = [NSMutableData dataWithLength:data.length + kCCBlockSizeAES128];
    unsigned char iv[kCCBlockSizeAES128] = {0};
    size_t written = 0;
    CCCryptorStatus status = CCCrypt(kCCEncrypt, kCCAlgorithmAES, kCCOptionPKCS7Padding,
        key.bytes, key.length, iv, data.bytes, data.length, cipher.mutableBytes, cipher.length, &written);
    if (status != kCCSuccess) {
        if (error) *error = [NSError errorWithDomain:@"R3D" code:3
            userInfo:@{NSLocalizedDescriptionKey:@"取得署名を作成できませんでした"}];
        return nil;
    }
    cipher.length = written;
    return cipher;
}
@end
