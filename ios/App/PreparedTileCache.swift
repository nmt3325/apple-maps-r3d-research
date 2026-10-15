import Foundation
import CryptoKit

struct PreparedTileSnapshot: Codable {
    static let version = 1
    static let maximumBytes = 32*1024*1024
    var version: Int
    var key: TileKey
    var created: Date
    var payload: [String:Data]
    var checksums: [String:Data]

    static func supports(_ key: TileKey) -> Bool {
        key.style == 100 || (key.style == 98 && key.z == StreamingPolicy.coarseZoom)
    }
    static func valid(_ payload: [String:Data], for key: TileKey) -> Bool {
        guard supports(key), payload.values.reduce(0,{$0+$1.count}) <= maximumBytes,
              let json = payload["json"] else { return false }
        if key.style == 100 {
            guard Set(payload.keys) == ["json"], json.count <= 2*1024*1024,
                  let index = try? JSONDecoder().decode(HeightIndex.self,from:json) else { return false }
            return index.valid(for:key)
        }
        let fields: Set<String> = ["json","vertices","indices","splats","atlas","preview_atlas"]
        guard Set(payload.keys).isSubset(of:fields), fields.subtracting(["preview_atlas"]).isSubset(of:Set(payload.keys)),
              json.count <= 16384, (payload["preview_atlas"]?.count ?? 0) <= 1024*1024,
              let info = try? JSONDecoder().decode(TileInfo.self,from:json) else { return false }
        return info.validBuffers(payload)
    }
    func verified(for expected: TileKey, now: Date) -> Bool {
        let age = now.timeIntervalSince(created)
        guard version == Self.version, key == expected, age >= 0, age < 3600,
              Self.valid(payload,for:key), Set(payload.keys) == Set(checksums.keys) else { return false }
        return payload.allSatisfy { name,data in checksums[name] == Data(SHA256.hash(data:data)) }
    }
}

struct PreparedTileLookup: Sendable {
    var payload: [String:Data]?
    var revision: Int
}

extension RawCache {
    func readPrepared(_ key: TileKey, now: Date = Date()) -> PreparedTileLookup {
        let miss = PreparedTileLookup(payload:nil,revision:revision)
        guard PreparedTileSnapshot.supports(key), let bytes = read(key) else { return miss }
        guard bytes.count <= PreparedTileSnapshot.maximumBytes,
              let snapshot = try? PropertyListDecoder().decode(PreparedTileSnapshot.self,from:bytes),
              snapshot.verified(for:key,now:now) else {
            remove(key.name+".bin"); return miss
        }
        return PreparedTileLookup(payload:snapshot.payload,revision:revision)
    }
    func storePrepared(_ payload: [String:Data], for key: TileKey, revision expected: Int, now: Date = Date()) -> Bool {
        // The same actor orders clearing and persistence; old jobs cannot repopulate it.
        guard !Task.isCancelled, revision == expected, PreparedTileSnapshot.valid(payload,for:key) else { return false }
        let snapshot = PreparedTileSnapshot(version:PreparedTileSnapshot.version,key:key,created:now,payload:payload,
            checksums:payload.mapValues { Data(SHA256.hash(data:$0)) })
        let encoder = PropertyListEncoder(); encoder.outputFormat = .binary
        guard let data = try? encoder.encode(snapshot), data.count <= PreparedTileSnapshot.maximumBytes else { return false }
        return write(key,data)
    }
}
