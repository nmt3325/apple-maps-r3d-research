import Foundation

// Shared signing constants published in the MIT-licensed reference below.
// They are not an Apple ID, per-user token, saved accessKey, or GitHub secret.
// https://github.com/SynArchive/Apple-3D-RE-Lightweight/blob/df3e354d1c0f2dc7a35ecb425b0f49973b7d46ee/main.go
// See ThirdParty/Apple-3D-RE-Lightweight-LICENSE.txt.
extension FetchConfiguration {
    static var standard: FetchConfiguration {
        FetchConfiguration(
            endpoint: "https://gspe11-ssl.ls.apple.com/tile",
            queryParameters: [["style","98"],["v","714"],["region","0"],
                ["z","20"],["x","0"],["y","0"],["h","0"],["preflight","2"]],
            signingParts: ["4cjLaD4jGRwlQ9U","72xIzEBe0vHBmf9"],
            headers: ["Accept":"application/octet-stream"])
    }
}
