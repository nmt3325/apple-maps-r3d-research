#if DEBUG
import Foundation

// Only enabled explicitly by a simulator test launch argument.
// Produces a local report, and drives real streaming through the production path.
@MainActor enum ValidationScenario {
    static func run(_ model: ExplorerModel) async {
        let signatureConfig = FetchConfiguration(endpoint:"https://example.apple.com/tile",
            queryParameters:[["style","98"],["v","1"],["region","test"],["z","20"],["x","0"],["y","0"],["h","0"]],
            signingParts:["test-part-a","test-part-b"])
        let signed = try? signatureConfig.signedURL(TileKey(z:20,x:931326,y:412987),now:1700000000,nonce:"aaaaaaaaaaaaaaaa")
        let expected = "https://example.apple.com/tile?style=98&v=1&region=test&z=20&x=931326&y=412987&h=0&accessKey=1700004200_aaaaaaaaaaaaaaaa_ikSpT0OYd%2Bo%2BgyyFDo7jsTtU45JQ9W4ybbMc0kGgKALDuqtGQnDobuLJUU5k5deF0zJQfe%2F4OKEmXKYW0KQj0qsyiS0SoXFFdoxLArswR31HejMrk3t1qdSyckJZUvGn"
        let signatureMatches = signed?.absoluteString == expected
        var cacheConfig = signatureConfig
        cacheConfig.headers = ["Accept":"application/octet-stream","User-Agent":"test"]
        let firstNamespace = cacheConfig.cacheNamespace
        cacheConfig.headers = ["User-Agent":"test","Accept":"application/octet-stream"]
        let cacheNamespaceStable = cacheConfig.cacheNamespace == firstNamespace
        var samples = [[String:Any]]()
        let directory = FileManager.default.urls(for:.documentDirectory,in:.userDomainMask)[0]
        let report = directory.appendingPathComponent("streaming-validation.json")
        for second in 0...120 {
            if second == 40 { model.camera.yaw = .pi }
            if second == 65 { model.camera.eye.x += 450; model.camera.yaw = 0 }
            if second == 85 { model.memoryWarning() }
            if second == 100 { model.relocate(latitude:21.2828,longitude:-157.8369,label:"ワイキキ") }
            let visible = model.renderTiles()
            samples.append(["second":second,"residentTiles":model.tiles.count,
                "drawnTiles":model.drawnTiles,"fps":model.fps,
                "residentBytes":model.tiles.values.reduce(0){$0+$1.cost},"budget":model.budget,
                "pending":model.pending.count,"fetching":model.fetching.count,
                "preparing":model.processing.active,"completed":model.completed,
                "indexCount":model.indices.count,"failures":model.failures.count,
                "visibleLODs":Array(Set(visible.map{$0.key.z})).sorted(),
                "viewDistance":model.renderDistance,
                "cpuCacheBytes":model.decodedCache.bytes,"processFootprintBytes":ExplorerModel.processFootprint(),
                "metalAllocatedBytes":model.device?.currentAllocatedSize ?? 0,
                "textureSizes":model.tiles.values.compactMap{$0.atlas.map{max($0.width,$0.height)}},
                "loadedHeightLayers":Array(Set(model.tiles.keys.map(\.h))).sorted(),
                "eye":[model.camera.eye.x,model.camera.eye.y,model.camera.eye.z],
                "latitude":model.origin.latitude,"longitude":model.origin.longitude,
                "message":model.message])
            if let data = try? JSONSerialization.data(withJSONObject:["samples":samples,"signatureMatchesPython":signatureMatches,"cacheNamespaceStable":cacheNamespaceStable],options:[.prettyPrinted,.sortedKeys]) {
                try? data.write(to:report,options:.atomic)
            }
            try? await Task.sleep(for:.seconds(1))
        }
        model.relocate(latitude:35.6586,longitude:139.7454,label:"東京タワー")
        model.memoryConstrainedUntil = 0; model.viewDistance = 350
        model.camera.eye = SIMD3(60,160,220)
        model.camera.yaw = -0.25; model.camera.pitch = 0.12
    }
}
#endif
