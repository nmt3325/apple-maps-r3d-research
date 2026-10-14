import Foundation

@main struct DiagnosticsChecks {
    static func records(_ url: URL) throws -> [[String:Any]] {
        let data = try Data(contentsOf:url)
        precondition(data.last == 10, "Export must end at a complete JSONL record")
        return try data.split(separator:10).map {
            try JSONSerialization.jsonObject(with:Data($0)) as! [String:Any]
        }
    }
    static func main() async throws {
        let root = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
        defer { try? FileManager.default.removeItem(at:root) }
        let log = DiagnosticsLog(directory:root,maxQueued:10000)
        DispatchQueue.concurrentPerform(iterations:200) { i in
            log.event("concurrent",tile:"s98_z20_x1_y2_h0",trace:"request-\(i)",fields:["i":i,"text":"日本語\nline"])
        }
        let snapshot = try await log.export()
        let rows = try records(snapshot)
        precondition(rows.filter{$0["event"] as? String == "concurrent"}.count == 200)
        let sequence = rows.compactMap{$0["sequence"] as? Int}
        precondition(sequence == sequence.sorted() && Set(sequence).count == sequence.count)
        precondition(rows.allSatisfy{$0["schema_version"] as? Int == 1})
        let original = try Data(contentsOf:snapshot)
        log.event("after_snapshot")
        let second = try await log.export()
        let unchanged = try Data(contentsOf:snapshot)
        let secondRows = try records(second)
        precondition(unchanged == original, "Shared files must stay immutable")
        precondition(secondRows.contains{$0["event"] as? String == "after_snapshot"})
        let error = NSError(domain:NSURLErrorDomain,code:-1001,userInfo:[NSURLErrorFailingURLStringErrorKey:"https://example.test/?accessKey=SECRET"])
        log.event("error",fields:DiagnosticsLog.errorFields(error))
        let redacted = try await log.export()
        let redactedText = try String(contentsOf:redacted,encoding:.utf8)
        precondition(!redactedText.contains("SECRET"))
        log.event("invalid",fields:["value":Double.nan])
        log.event("oversized",fields:["text":String(repeating:"x",count:70000)])
        let dropped = try records(await log.export())
        precondition((dropped[0]["fields"] as! [String:Any])["dropped_events"] as! Int == 2)
        do {
            _ = try await log.export(to:root.appendingPathComponent("missing/file.jsonl"))
            preconditionFailure("Export failures must reach the UI")
        } catch {}
        let rotatingRoot = root.appendingPathComponent("rotation")
        let rotating = DiagnosticsLog(directory:rotatingRoot,segmentBytes:2048,segmentCount:3,maxQueued:10000)
        for i in 0..<100 { rotating.event("rotate",fields:["i":i]) }
        let rotated = try records(await rotating.export())
        precondition((rotated.last?["fields"] as? [String:Any])?["i"] as? Int == 99)
        precondition(rotated.count < 100)
        let segments = try FileManager.default.contentsOfDirectory(at:rotatingRoot,includingPropertiesForKeys:[.fileSizeKey]).filter{$0.pathExtension == "jsonl"}
        precondition(segments.count <= 3)
        for segment in segments {
            let data = try Data(contentsOf:segment); precondition(data.count <= 2048)
        }
        let crashRoot = root.appendingPathComponent("crash")
        try FileManager.default.createDirectory(at:crashRoot,withIntermediateDirectories:true)
        try Data("{\"event\":\"previous_session\"}\n{\"partial\":".utf8).write(to:crashRoot.appendingPathComponent("stream-0.jsonl"))
        let recovered = DiagnosticsLog(directory:crashRoot)
        let recoveredRows = try records(await recovered.export())
        precondition(recoveredRows.contains{$0["event"] as? String == "previous_session"})
        precondition(recoveredRows.contains{$0["event"] as? String == "session.start"})
        print("PASS: concurrent JSONL ordering, trace fields, immutable export, rotation bounds, partial-write recovery, redacted errors, invalid records and export errors")
    }
}
