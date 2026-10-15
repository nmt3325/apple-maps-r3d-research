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

final class DownloadLimit: NSObject, URLSessionDownloadDelegate, @unchecked Sendable {
    let limit = 16_000_000
    let tile: String
    let trace: String
    let attempt: Int
    private var lastProgress = 0.0
    init(tile: String, trace: String, attempt: Int) { self.tile = tile; self.trace = trace; self.attempt = attempt }
    func urlSession(_ session: URLSession, task: URLSessionTask, didFinishCollecting metrics: URLSessionTaskMetrics) {
        func ms(_ start: Date?, _ end: Date?) -> Any {
            guard let start, let end else { return NSNull() }; return end.timeIntervalSince(start)*1000
        }
        for (index,m) in metrics.transactionMetrics.enumerated() {
            DiagnosticsLog.shared.event("network.metrics",tile:tile,trace:trace,fields:[
                "attempt":attempt,"transaction":index,"task_ms":metrics.taskInterval.duration*1000,
                "dns_ms":ms(m.domainLookupStartDate,m.domainLookupEndDate),
                "connect_ms":ms(m.connectStartDate,m.connectEndDate),
                "tls_ms":ms(m.secureConnectionStartDate,m.secureConnectionEndDate),
                "request_ms":ms(m.requestStartDate,m.requestEndDate),
                "ttfb_ms":ms(m.requestEndDate,m.responseStartDate),
                "transfer_ms":ms(m.responseStartDate,m.responseEndDate),
                "protocol":m.networkProtocolName ?? "unknown","connection_reused":m.isReusedConnection,
                "proxy":m.isProxyConnection,"fetch_type":m.resourceFetchType.rawValue,
                "response_bytes":m.countOfResponseBodyBytesReceived,"redirects":metrics.redirectCount])
        }
    }
    func urlSession(_ session: URLSession, downloadTask: URLSessionDownloadTask,
                    didWriteData bytesWritten: Int64, totalBytesWritten: Int64, totalBytesExpectedToWrite: Int64) {
        let now = DiagnosticsLog.now
        if now-lastProgress >= 1 || totalBytesWritten == totalBytesExpectedToWrite {
            lastProgress = now
            DiagnosticsLog.shared.event("network.progress",tile:tile,trace:trace,fields:["attempt":attempt,
                "received_bytes":totalBytesWritten,"expected_bytes":totalBytesExpectedToWrite])
        }
        if totalBytesWritten > limit || totalBytesExpectedToWrite > limit {
            DiagnosticsLog.shared.event("network.limit_exceeded",tile:tile,trace:trace,fields:["limit_bytes":limit])
            downloadTask.cancel()
        }
    }
    func urlSession(_ session: URLSession, downloadTask: URLSessionDownloadTask, didFinishDownloadingTo location: URL) {}
    func urlSession(_ session: URLSession, task: URLSessionTask,
                    willPerformHTTPRedirection response: HTTPURLResponse, newRequest request: URLRequest,
                    completionHandler: @escaping (URLRequest?) -> Void) {
        // A signed request must never be forwarded to another origin.
        DiagnosticsLog.shared.event("network.redirect_rejected",tile:tile,trace:trace,fields:["status":response.statusCode])
        completionHandler(nil)
    }
}

actor AppleMapsClient {
    let config: FetchConfiguration
    let cache: RawCache
    let preparedCache: RawCache
    let session: URLSession
    var empty: [TileKey:Date] = [:]
    init(_ config: FetchConfiguration) {
        self.config = config; cache = RawCache(namespace:config.cacheNamespace)
        preparedCache = RawCache(namespace:config.cacheNamespace+"-prepared-v1",budget:64*1024*1024)
        let settings = URLSessionConfiguration.ephemeral
        settings.timeoutIntervalForRequest = 25
        settings.timeoutIntervalForResource = 40
        settings.httpMaximumConnectionsPerHost = 2
        settings.urlCache = nil
        session = URLSession(configuration:settings)
    }
    func fetch(_ key: TileKey, trace: String = UUID().uuidString) async throws -> Data? {
        let start = DiagnosticsLog.now
        var outcome = "error"
        DiagnosticsLog.shared.event("fetch.begin",tile:key.name,trace:trace)
        defer { DiagnosticsLog.shared.event("fetch.end",tile:key.name,trace:trace,fields:["outcome":outcome,"total_ms":DiagnosticsLog.milliseconds(since:start)]) }
        do {
            try Task.checkCancellation()
            if let until = empty[key], until > Date() {
                outcome = "negative_cache_hit"; return nil
            }
            let readStart = DiagnosticsLog.now
            let cached = await cache.read(key)
            DiagnosticsLog.shared.event("cache.disk_read",tile:key.name,trace:trace,fields:["hit":cached != nil,
                "bytes":cached?.count ?? 0,"duration_ms":DiagnosticsLog.milliseconds(since:readStart)])
            if let cached { outcome = "disk_cache_hit"; return cached }
            for attempt in 0..<3 {
                try Task.checkCancellation()
                let signingStart = DiagnosticsLog.now
                var request = URLRequest(url:try config.signedURL(key))
                DiagnosticsLog.shared.event("network.begin",tile:key.name,trace:trace,fields:["attempt":attempt+1,
                    "signing_ms":DiagnosticsLog.milliseconds(since:signingStart),"request_timeout_s":25,"resource_timeout_s":40])
                request.cachePolicy = .reloadIgnoringLocalCacheData
                for (name,value) in config.headers ?? [:] where !["host","authorization","cookie"].contains(name.lowercased()) {
                    request.setValue(value,forHTTPHeaderField:name)
                }
                let networkStart = DiagnosticsLog.now
                let (file,response) = try await session.download(for:request,delegate:DownloadLimit(tile:key.name,trace:trace,attempt:attempt+1))
                defer { try? FileManager.default.removeItem(at:file) }
                guard let http = response as? HTTPURLResponse else { throw StreamError.http(0) }
                DiagnosticsLog.shared.event("network.response",tile:key.name,trace:trace,fields:["attempt":attempt+1,
                    "status":http.statusCode,"duration_ms":DiagnosticsLog.milliseconds(since:networkStart),
                    "expected_bytes":response.expectedContentLength])
                if [401,403].contains(http.statusCode) { throw StreamError.authentication }
                if http.statusCode == 429 || http.statusCode >= 500 {
                    if attempt < 2 {
                        let retry = min(20,max(1,Double(http.value(forHTTPHeaderField:"Retry-After") ?? "") ?? pow(2,Double(attempt+1))))
                        DiagnosticsLog.shared.event("network.retry",tile:key.name,trace:trace,fields:["attempt":attempt+1,"status":http.statusCode,"backoff_s":retry])
                        try await Task.sleep(for:.seconds(retry)); continue
                    }
                }
                if http.statusCode == 404 || http.statusCode == 204 {
                    if key.style == 100 { throw StreamError.http(http.statusCode) }
                    rememberEmpty(key); outcome = "empty"; return nil
                }
                guard http.statusCode == 200 else { throw StreamError.http(http.statusCode) }
                let size = try file.resourceValues(forKeys:[.fileSizeKey]).fileSize ?? Int.max
                guard size <= 16_000_000 else { throw StreamError.responseTooLarge }
                let data = try Data(contentsOf:file)
                if data.isEmpty {
                    if key.style == 100 { throw StreamError.invalidIndex }
                    rememberEmpty(key); outcome = "empty"; return nil
                }
                try Task.checkCancellation()
                let writeStart = DiagnosticsLog.now
                let stored = await cache.write(key,data)
                DiagnosticsLog.shared.event("cache.disk_write_complete",tile:key.name,trace:trace,fields:["stored":stored,"bytes":data.count,"duration_ms":DiagnosticsLog.milliseconds(since:writeStart)])
                outcome = "downloaded"
                return data
            }
            throw StreamError.http(429)
        } catch {
            outcome = error is CancellationError || (error as? URLError)?.code == .cancelled ? "cancelled" : "error"
            DiagnosticsLog.shared.event("fetch.error",tile:key.name,trace:trace,fields:DiagnosticsLog.errorFields(error))
            throw error
        }
    }
    private func rememberEmpty(_ key: TileKey) {
        if empty.count >= 4096 { empty = empty.filter{$0.value > Date()} }
        if empty.count >= 4096, let oldest = empty.min(by:{$0.value<$1.value}) { empty.removeValue(forKey:oldest.key) }
        empty[key] = Date().addingTimeInterval(60)
    }
    func rejectCached(_ key: TileKey) async {
        DiagnosticsLog.shared.event("cache.disk_reject",tile:key.name)
        await cache.remove(key.name+".bin")
        await preparedCache.remove(key.name+".bin")
    }
    func clearCache() async { empty.removeAll(); await preparedCache.clear(); await cache.clear() }
}

actor TileDecoder {
    func invoke(_ function: String, data: Data, tile: String? = nil, trace: String? = nil, queuedAt: Double? = nil) throws -> [String:Data] {
        let start = DiagnosticsLog.now
        DiagnosticsLog.shared.event("decode.begin",tile:tile,trace:trace,fields:["function":function,"input_bytes":data.count,
            "actor_wait_ms":queuedAt.map{(start-$0)*1000} ?? 0])
        do {
            try Task.checkCancellation()
            let result = try R3DPythonBridge.invoke(function,data:data)
            try Task.checkCancellation()
            DiagnosticsLog.shared.event("decode.end",tile:tile,trace:trace,fields:["function":function,"duration_ms":DiagnosticsLog.milliseconds(since:start),
                "output_bytes":result.mapValues{$0.count}])
            return result
        } catch {
            var fields = DiagnosticsLog.errorFields(error); fields["duration_ms"] = DiagnosticsLog.milliseconds(since:start)
            DiagnosticsLog.shared.event("decode.error",tile:tile,trace:trace,fields:fields); throw error
        }
    }
}
