import Foundation

actor RawCache {
    struct Entry { var size: Int; var touched: Date }
    let directory: URL
    var entries: [String:Entry] = [:]
    var bytes = 0
    private(set) var revision = 0
    let budget: Int
    init(namespace: String, budget: Int = 384*1024*1024, root: URL? = nil) {
        self.budget = budget
        directory = (root ?? FileManager.default.urls(for:.cachesDirectory,in:.userDomainMask)[0])
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
        let name = key.name+".bin", file = directory.appendingPathComponent(name)
        guard var entry = entries[name], entry.size <= budget,
              Date().timeIntervalSince(entry.touched) < 3600,
              let size = try? file.resourceValues(forKeys:[.fileSizeKey]).fileSize, size == entry.size,
              let data = try? Data(contentsOf:file), data.count == entry.size else {
            remove(name); return nil
        }
        entry.touched = Date(); entries[name] = entry
        return data
    }
    func remove(_ name: String) {
        if let entry = entries.removeValue(forKey:name) { bytes -= entry.size }
        try? FileManager.default.removeItem(at:directory.appendingPathComponent(name))
    }
    func write(_ key: TileKey, _ data: Data) -> Bool {
        guard data.count <= budget else { return false }
        let name = key.name+".bin"
        remove(name)
        while bytes+data.count > budget, let oldest = entries.min(by:{$0.value.touched<$1.value.touched}) { remove(oldest.key) }
        do {
            try data.write(to:directory.appendingPathComponent(name),options:.atomic)
            entries[name] = Entry(size:data.count,touched:Date()); bytes += data.count
            return true
        } catch {
            DiagnosticsLog.shared.event("cache.disk_write_error",tile:key.name,fields:DiagnosticsLog.errorFields(error)); return false
        }
    }
    func clear() {
        revision += 1
        for name in Array(entries.keys) { remove(name) }
    }
}
