import Foundation

// Persistent, bounded JSONL. Encoding happens at the call site; all filesystem work
// is serialized off the render thread. No request URLs, headers or NSError userInfo.
final class DiagnosticsLog: @unchecked Sendable {
    static let shared = DiagnosticsLog()
    static var now: Double { ProcessInfo.processInfo.systemUptime }
    static func milliseconds(since start: Double) -> Double { (now-start)*1000 }
    static func errorFields(_ error: Error) -> [String:Any] {
        let ns = error as NSError
        return ["error_domain":ns.domain,"error_code":ns.code,
                "cancelled":error is CancellationError || (ns.domain == NSURLErrorDomain && ns.code == NSURLErrorCancelled)]
    }
    let sessionID = UUID().uuidString
    private let directory: URL
    private let segmentBytes: Int
    private let segmentCount: Int
    private let queue = DispatchQueue(label:"dev.nmt3325.r3d.diagnostics",qos:.utility)
    private let lock = NSLock()
    private var queued = 0
    private var sequence = 0
    private var dropped = 0
    private var handle: FileHandle?
    private var fileBytes = 0
    private var writeFailures = 0
    private let maxQueued: Int

    init(directory: URL? = nil, segmentBytes: Int = 4*1024*1024, segmentCount: Int = 6, maxQueued: Int = 1024) {
        self.directory = directory ?? FileManager.default.urls(for:.applicationSupportDirectory,in:.userDomainMask)[0]
            .appendingPathComponent("Diagnostics",isDirectory:true)
        self.segmentBytes = max(1024,segmentBytes); self.segmentCount = max(2,segmentCount)
        self.maxQueued = maxQueued
        event("session.start",fields:["os":ProcessInfo.processInfo.operatingSystemVersionString,
            "app_version":Bundle.main.object(forInfoDictionaryKey:"CFBundleShortVersionString") as? String ?? "unknown",
            "app_build":Bundle.main.object(forInfoDictionaryKey:"CFBundleVersion") as? String ?? "unknown",
            "physical_memory_bytes":ProcessInfo.processInfo.physicalMemory,
            "processors":ProcessInfo.processInfo.processorCount,
            "segment_bytes":self.segmentBytes,"segment_count":self.segmentCount,
            "wall_time_unit":"unix_seconds_utc","duration_unit":"milliseconds"])
    }
    deinit { try? handle?.close() }

    func event(_ name: String, tile: String? = nil, trace: String? = nil, fields: [String:Any] = [:]) {
        lock.lock()
        guard queued < maxQueued else { dropped += 1; lock.unlock(); return }
        sequence += 1
        var record: [String:Any] = ["schema_version":1,"session_id":sessionID,"sequence":sequence,
            "unix_time":Date().timeIntervalSince1970,"uptime_s":Self.now,"event":name,"fields":fields]
        if let tile { record["tile"] = tile }
        if let trace { record["trace_id"] = trace }
        // Invalid or oversized payloads cannot corrupt the line stream.
        guard let data = try? JSONSerialization.data(withJSONObject:record,options:[.sortedKeys]), data.count <= min(65536,segmentBytes-1) else {
            dropped += 1; lock.unlock(); return
        }
        queued += 1
        // Enqueue while locked to keep sequence numbers and file order identical.
        queue.async { [self] in
            do { try append(data) } catch { writeFailures += 1 }
            lock.lock(); queued -= 1; lock.unlock()
        }
        lock.unlock()
    }
    private func file(_ index: Int) -> URL { directory.appendingPathComponent("stream-\(index).jsonl") }
    private func open() throws {
        guard handle == nil else { return }
        try FileManager.default.createDirectory(at:directory,withIntermediateDirectories:true)
        let url = file(0)
        if !FileManager.default.fileExists(atPath:url.path) { FileManager.default.createFile(atPath:url.path,contents:nil) }
        let writer = try FileHandle(forUpdating:url)
        let end = try writer.seekToEnd()
        // A killed process can leave a partial last line. Recover just that tail.
        if end > 0 {
            let offset = end > 65538 ? end-65538 : 0
            try writer.seek(toOffset:offset)
            let tail = try writer.readToEnd() ?? Data()
            let validEnd = tail.lastIndex(of:10).map { offset+UInt64($0+1) } ?? 0
            if validEnd < end { try writer.truncate(atOffset:validEnd) }
        }
        fileBytes = Int(try writer.seekToEnd()); handle = writer
    }
    private func append(_ data: Data) throws {
        try open()
        if fileBytes > 0 && fileBytes+data.count+1 > segmentBytes {
            try handle?.close(); handle = nil
            let fm = FileManager.default
            if fm.fileExists(atPath:file(segmentCount-1).path) { try fm.removeItem(at:file(segmentCount-1)) }
            for i in stride(from:segmentCount-2,through:0,by:-1) where fm.fileExists(atPath:file(i).path) {
                try fm.moveItem(at:file(i),to:file(i+1))
            }
            try open()
        }
        try handle?.write(contentsOf:data+Data([10])); fileBytes += data.count+1
    }
    // A stable snapshot: includes all records accepted before this call; subsequent
    // live writes cannot mutate the exported file. Streaming copy bounds memory.
    func export(to destination: URL? = nil) async throws -> URL {
        try await withCheckedThrowingContinuation { continuation in
            lock.lock()
            let lost = dropped
            queue.async { [self] in
                do {
                    try open(); try handle?.synchronize()
                    let exports = directory.appendingPathComponent("Exports",isDirectory:true)
                    try FileManager.default.createDirectory(at:exports,withIntermediateDirectories:true)
                    let output = destination ?? exports.appendingPathComponent("R3D-diagnostics-\(UUID().uuidString).jsonl")
                    // Retain recent share snapshots across launches, bounded independently.
                    if destination == nil {
                        let old = try FileManager.default.contentsOfDirectory(at:exports,includingPropertiesForKeys:[.creationDateKey])
                            .sorted { ((try? $0.resourceValues(forKeys:[.creationDateKey]).creationDate) ?? .distantPast) <
                                      ((try? $1.resourceValues(forKeys:[.creationDateKey]).creationDate) ?? .distantPast) }
                        for url in old.prefix(max(0,old.count-2)) { try? FileManager.default.removeItem(at:url) }
                    }
                    guard FileManager.default.createFile(atPath:output.path,contents:nil) else {
                        throw CocoaError(.fileWriteUnknown)
                    }
                    do {
                        let writer = try FileHandle(forWritingTo:output)
                        defer { try? writer.close() }
                        let metadata: [String:Any] = ["schema_version":1,"event":"export.snapshot",
                            "session_id":sessionID,"unix_time":Date().timeIntervalSince1970,
                            "fields":["dropped_events":lost,"write_failures":writeFailures,
                                "retention_bytes":segmentBytes*segmentCount,"contains_location":true]]
                        try writer.write(contentsOf:JSONSerialization.data(withJSONObject:metadata,options:[.sortedKeys])+Data([10]))
                        for i in stride(from:segmentCount-1,through:0,by:-1) where FileManager.default.fileExists(atPath:file(i).path) {
                            let reader = try FileHandle(forReadingFrom:file(i))
                            defer { try? reader.close() }
                            while let chunk = try reader.read(upToCount:1024*1024), !chunk.isEmpty { try writer.write(contentsOf:chunk) }
                        }
                        try writer.synchronize()
                    } catch { try? FileManager.default.removeItem(at:output); throw error }
                    continuation.resume(returning:output)
                } catch { continuation.resume(throwing:error) }
            }
            lock.unlock()
        }
    }
}
