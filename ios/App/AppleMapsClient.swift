import Foundation
import CryptoKit
import Security

struct FetchConfiguration: Codable, Sendable {
    var endpoint: String
    var queryParameters: [[String]]
    var signingParts: [String]
    var headers: [String:String]?
    func validate() throws {
        guard let u = URLComponents(string:endpoint), u.scheme == "https",
              let host = u.host, host.hasSuffix(".apple.com"),
              u.query == nil, u.fragment == nil, u.user == nil, u.password == nil,
              signingParts.count == 2, signingParts.allSatisfy({ !$0.isEmpty }),
              queryParameters.allSatisfy({ $0.count == 2 }) else { throw StreamError.configuration }
        let keys = queryParameters.map { $0[0] }
        guard Set(keys).count == keys.count, !keys.contains("accessKey"),
              Set(["x","y","z","h","style"]).isSubset(of:Set(keys)),
              queryParameters.first(where:{$0[0]=="style"})?[1] == "98" else { throw StreamError.configuration }
    }
    var cacheNamespace: String {
        let encoder = JSONEncoder()
        encoder.outputFormatting = .sortedKeys
        let data = (try? encoder.encode(self)) ?? Data()
        return SHA256.hash(data:data).map{String(format:"%02x",$0)}.joined()
    }
    private static func encode(_ value: String, form: Bool) -> String {
        let safe = Set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.~".utf8)
        return value.utf8.map { c in
            safe.contains(c) ? String(UnicodeScalar(c)) : (c == 32 && form ? "+" : String(format:"%%%02X",c))
        }.joined()
    }
    func signedURL(_ key: TileKey, now: Int = Int(Date().timeIntervalSince1970), nonce supplied: String? = nil) throws -> URL {
        try validate()
        guard (7...22).contains(key.z), (0..<(1 << key.z)).contains(key.x),
              (0..<(1 << key.z)).contains(key.y), key.h >= 0, [98,100].contains(key.style) else { throw StreamError.configuration }
        var components = URLComponents(string:endpoint)!
        let coordinates = ["x":key.x,"y":key.y,"z":key.z,"h":key.h,"style":key.style]
        let query = queryParameters.map { pair in
            Self.encode(pair[0],form:true)+"="+Self.encode(coordinates[pair[0]].map(String.init) ?? pair[1],form:true)
        }.joined(separator:"&")
        let alphabet = Array("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789".utf8)
        var random = [UInt8](repeating:0,count:16)
        guard SecRandomCopyBytes(kSecRandomDefault,random.count,&random) == errSecSuccess else { throw StreamError.authentication }
        let nonce = supplied ?? String(bytes:random.map{alphabet[Int($0)%alphabet.count]},encoding:.utf8)!
        let expiration = now+4200
        let path = components.percentEncodedPath.isEmpty ? "/" : components.percentEncodedPath
        let payload = Data((path+"?"+query+String(expiration)+nonce).utf8)
        let hash = Data(SHA256.hash(data:Data((signingParts.joined()+nonce).utf8)))
        let encrypted = try R3DPythonBridge.encrypt(payload,key:hash)
        let access = "\(expiration)_\(nonce)_"+encrypted.base64EncodedString()
        components.percentEncodedQuery = query+"&accessKey="+Self.encode(access,form:false)
        guard let url = components.url else { throw StreamError.configuration }
        return url
    }
}

enum CredentialStore {
    static let service = "dev.nmt3325.r3d-explorer.maps"
    static func save(_ data: Data) throws {
        try JSONDecoder().decode(FetchConfiguration.self,from:data).validate()
        let base: [String:Any] = [kSecClass as String:kSecClassGenericPassword,
            kSecAttrService as String:service,kSecAttrAccount as String:"fetch"]
        SecItemDelete(base as CFDictionary)
        var attributes = base
        attributes[kSecValueData as String] = data
        attributes[kSecAttrAccessible as String] = kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly
        guard SecItemAdd(attributes as CFDictionary,nil) == errSecSuccess else { throw StreamError.configuration }
    }
    static func load() -> FetchConfiguration? {
        var output: CFTypeRef?
        let query: [String:Any] = [kSecClass as String:kSecClassGenericPassword,kSecAttrService as String:service,
            kSecAttrAccount as String:"fetch",kSecReturnData as String:true,kSecMatchLimit as String:kSecMatchLimitOne]
        if SecItemCopyMatching(query as CFDictionary,&output) == errSecSuccess,
           let data = output as? Data, let config = try? JSONDecoder().decode(FetchConfiguration.self,from:data),
           (try? config.validate()) != nil { return config }
        if let path = Bundle.main.url(forResource:"maps.credentials",withExtension:"json"),
           let data = try? Data(contentsOf:path),
           let config = try? JSONDecoder().decode(FetchConfiguration.self,from:data),
           (try? config.validate()) != nil {
            // Unsigned simulator builds may not have a Keychain access group.
            // A valid local bootstrap configuration remains usable in that case.
            try? save(data)
            return config
        }
        // The researched service uses shared, published signing constants.
        // Assemble defaults on the device; no external JSON or CI secret is needed.
        let standard = FetchConfiguration.standard
        guard (try? standard.validate()) != nil else { return nil }
        return standard
    }
    static func restoreStandard() {
        let query: [String:Any] = [kSecClass as String:kSecClassGenericPassword,
            kSecAttrService as String:service,kSecAttrAccount as String:"fetch"]
        SecItemDelete(query as CFDictionary)
    }
}

actor RawCache {
    struct Entry { var size: Int; var touched: Date }
    let directory: URL
    var entries: [String:Entry] = [:]
    var bytes = 0
    let budget: Int
    init(namespace: String, budget: Int = 384*1024*1024) {
        self.budget = budget
        directory = FileManager.default.urls(for:.cachesDirectory,in:.userDomainMask)[0]
            .appendingPathComponent("R3D/"+namespace,isDirectory:true)
        try? FileManager.default.createDirectory(at:directory,withIntermediateDirectories:true)
        let files = (try? FileManager.default.contentsOfDirectory(at:directory,includingPropertiesForKeys:[.fileSizeKey,.contentModificationDateKey])) ?? []
        for file in files where file.pathExtension == "bin" {
            if let info = try? file.resourceValues(forKeys:[.fileSizeKey,.contentModificationDateKey]), let size = info.fileSize {
                entries[file.lastPathComponent] = Entry(size:size,touched:info.contentModificationDate ?? .distantPast)
                bytes += size
            }
        }
    }
    func read(_ key: TileKey) -> Data? {
        let name = key.name+".bin"
        guard var entry = entries[name], Date().timeIntervalSince(entry.touched) < 3600,
              let data = try? Data(contentsOf:directory.appendingPathComponent(name)), data.count == entry.size else {
            remove(name); return nil
        }
        entry.touched = Date(); entries[name] = entry
        return data
    }
    func remove(_ name: String) {
        if let entry = entries.removeValue(forKey:name) { bytes -= entry.size }
        try? FileManager.default.removeItem(at:directory.appendingPathComponent(name))
    }
    func write(_ key: TileKey, _ data: Data) {
        guard data.count <= budget else { return }
        let name = key.name+".bin"
        remove(name)
        while bytes+data.count > budget, let oldest = entries.min(by:{$0.value.touched<$1.value.touched}) { remove(oldest.key) }
        do {
            try data.write(to:directory.appendingPathComponent(name),options:.atomic)
            entries[name] = Entry(size:data.count,touched:Date()); bytes += data.count
        } catch { /* A cache write failure does not prevent live rendering. */ }
    }
    func clear() { for name in Array(entries.keys) { remove(name) } }
}

final class DownloadLimit: NSObject, URLSessionDownloadDelegate, @unchecked Sendable {
    let limit = 16_000_000
    func urlSession(_ session: URLSession, downloadTask: URLSessionDownloadTask,
                    didWriteData bytesWritten: Int64, totalBytesWritten: Int64, totalBytesExpectedToWrite: Int64) {
        if totalBytesWritten > limit || totalBytesExpectedToWrite > limit { downloadTask.cancel() }
    }
    func urlSession(_ session: URLSession, downloadTask: URLSessionDownloadTask, didFinishDownloadingTo location: URL) {}
    func urlSession(_ session: URLSession, task: URLSessionTask,
                    willPerformHTTPRedirection response: HTTPURLResponse, newRequest request: URLRequest,
                    completionHandler: @escaping (URLRequest?) -> Void) {
        // A signed request must never be forwarded to another origin.
        completionHandler(nil)
    }
}

actor AppleMapsClient {
    let config: FetchConfiguration
    let cache: RawCache
    let session: URLSession
    var empty: [TileKey:Date] = [:]
    init(_ config: FetchConfiguration) {
        self.config = config; cache = RawCache(namespace:config.cacheNamespace)
        let settings = URLSessionConfiguration.ephemeral
        settings.timeoutIntervalForRequest = 25
        settings.timeoutIntervalForResource = 40
        settings.httpMaximumConnectionsPerHost = 2
        settings.urlCache = nil
        session = URLSession(configuration:settings)
    }
    func fetch(_ key: TileKey) async throws -> Data? {
        try Task.checkCancellation()
        if let until = empty[key], until > Date() { return nil }
        if let cached = await cache.read(key) { return cached }
        for attempt in 0..<3 {
            try Task.checkCancellation()
            var request = URLRequest(url:try config.signedURL(key))
            request.cachePolicy = .reloadIgnoringLocalCacheData
            for (name,value) in config.headers ?? [:] where !["host","authorization","cookie"].contains(name.lowercased()) {
                request.setValue(value,forHTTPHeaderField:name)
            }
            let (file,response) = try await session.download(for:request,delegate:DownloadLimit())
            defer { try? FileManager.default.removeItem(at:file) }
            guard let http = response as? HTTPURLResponse else { throw StreamError.http(0) }
            if [401,403].contains(http.statusCode) { throw StreamError.authentication }
            if http.statusCode == 429 || http.statusCode >= 500 {
                if attempt < 2 {
                    let retry = min(20,max(1,Double(http.value(forHTTPHeaderField:"Retry-After") ?? "") ?? pow(2,Double(attempt+1))))
                    try await Task.sleep(for:.seconds(retry)); continue
                }
            }
            if http.statusCode == 404 || http.statusCode == 204 {
                if key.style == 100 { throw StreamError.http(http.statusCode) }
                rememberEmpty(key); return nil
            }
            guard http.statusCode == 200 else { throw StreamError.http(http.statusCode) }
            let size = try file.resourceValues(forKeys:[.fileSizeKey]).fileSize ?? Int.max
            guard size <= 16_000_000 else { throw StreamError.responseTooLarge }
            let data = try Data(contentsOf:file)
            if data.isEmpty {
                if key.style == 100 { throw StreamError.invalidIndex }
                rememberEmpty(key); return nil
            }
            try Task.checkCancellation()
            await cache.write(key,data)
            return data
        }
        throw StreamError.http(429)
    }
    private func rememberEmpty(_ key: TileKey) {
        if empty.count >= 4096 { empty = empty.filter{$0.value > Date()} }
        if empty.count >= 4096, let oldest = empty.min(by:{$0.value<$1.value}) { empty.removeValue(forKey:oldest.key) }
        empty[key] = Date().addingTimeInterval(60)
    }
    func rejectCached(_ key: TileKey) async { await cache.remove(key.name+".bin") }
    func clearCache() async { empty.removeAll(); await cache.clear() }
}

actor TileDecoder {
    func invoke(_ function: String, data: Data) throws -> [String:Data] {
        try Task.checkCancellation()
        let result = try R3DPythonBridge.invoke(function,data:data)
        try Task.checkCancellation()
        return result
    }
}
