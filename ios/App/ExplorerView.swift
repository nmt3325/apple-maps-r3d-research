import SwiftUI
import MetalKit
import UniformTypeIdentifiers

final class BoundedMetalView: MTKView {
    var renderScale: CGFloat = 1.5
    override func layoutSubviews() {
        super.layoutSubviews()
        let size = CGSize(width:max(1,bounds.width*renderScale),height:max(1,bounds.height*renderScale))
        if drawableSize != size { drawableSize = size }
    }
}

struct MetalViewport: UIViewRepresentable {
    @ObservedObject var model: ExplorerModel
    func makeCoordinator() -> Coordinator { Coordinator() }
    final class Coordinator { var renderer: MetalRenderer? }
    func makeUIView(context: Context) -> MTKView {
        let view = BoundedMetalView(frame:.zero,device:model.device)
        view.colorPixelFormat = .bgra8Unorm_srgb
        view.depthStencilPixelFormat = .depth32Float
        view.preferredFramesPerSecond = 60
        view.framebufferOnly = true
        view.autoResizeDrawable = false
        if let device = model.device {
            do {
                let renderer = try MetalRenderer(device:device)
                renderer.world = model; context.coordinator.renderer = renderer; view.delegate = renderer
            } catch { model.rendererError = error.localizedDescription }
        }
        return view
    }
    func updateUIView(_ view: MTKView, context: Context) {
        view.isPaused = !model.active
        view.preferredFramesPerSecond = ProcessInfo.processInfo.thermalState == .serious || ProcessInfo.processInfo.isLowPowerModeEnabled ? 30 : 60
        let scale: CGFloat = model.quality == 0 ? 1 : min(1.5,view.window?.screen.scale ?? 1.5)
        (view as? BoundedMetalView)?.renderScale = scale
        let size = CGSize(width:max(1,view.bounds.width*scale),height:max(1,view.bounds.height*scale))
        if view.drawableSize != size { view.drawableSize = size }
    }
}

struct Joystick: View {
    var changed: (SIMD2<Double>) -> Void
    @State var offset = CGSize.zero
    var body: some View {
        ZStack {
            Circle().fill(.ultraThinMaterial).frame(width:116,height:116)
            Image(systemName:"arrow.up.and.down.and.arrow.left.and.right").font(.title2).foregroundStyle(.white.opacity(0.5))
            Circle().fill(.white.opacity(0.65)).frame(width:45,height:45).offset(offset)
        }.contentShape(Circle())
            .gesture(DragGesture(minimumDistance:0).onChanged { value in
                let x = value.location.x-58, y = value.location.y-58
                let length = max(1,hypot(x,y)/38)
                offset = CGSize(width:x/length,height:y/length)
                changed(SIMD2(Double(offset.width/38),Double(-offset.height/38)))
            }.onEnded { _ in offset = .zero; changed(.zero) })
            .accessibilityLabel("移動スティック")
    }
}

struct HoldControl: View {
    let symbol: String
    let label: String
    let pressed: (Bool) -> Void
    var body: some View {
        Image(systemName:symbol).font(.title2).foregroundStyle(.white)
            .frame(width:52,height:52).background(.ultraThinMaterial,in:Circle())
            .gesture(DragGesture(minimumDistance:0).onChanged{_ in pressed(true)}.onEnded{_ in pressed(false)})
            .accessibilityLabel(label)
    }
}

struct ExplorerView: View {
    @StateObject var model = ExplorerModel()
    @Environment(\.scenePhase) var phase
    @State var settings = false
    @State var importing = false
    @State var lastDrag = CGSize.zero
    @State var magnification = 1.0
    var body: some View {
        ZStack {
            MetalViewport(model:model).ignoresSafeArea()
                .overlay(Color.clear.contentShape(Rectangle()).gesture(DragGesture(minimumDistance:2).onChanged { value in
                    let delta = CGSize(width:value.translation.width-lastDrag.width,height:value.translation.height-lastDrag.height)
                    model.camera.yaw -= delta.width*0.005
                    model.camera.pitch = min(1.4,max(-1.5,model.camera.pitch+delta.height*0.005))
                    lastDrag = value.translation
                }.onEnded{_ in lastDrag = .zero})
                .simultaneousGesture(MagnificationGesture().onChanged { scale in
                    let step = scale/magnification
                    model.camera.eye += model.camera.forward*Double(step-1)*60
                    model.camera.eye.y = max(2,model.camera.eye.y); magnification = scale
                }.onEnded{_ in magnification = 1})).ignoresSafeArea()
            VStack {
                HStack(spacing:12) {
                    VStack(alignment:.leading,spacing:3) {
                        Text(model.locationLabel).font(.headline)
                        Text(model.message).font(.caption).lineLimit(2)
                    }
                    Spacer()
                    Button { settings = true } label: { Image(systemName:"slider.horizontal.3").font(.title3).padding(12) }
                        .accessibilityLabel("設定")
                }.padding(14).background(.ultraThinMaterial,in:RoundedRectangle(cornerRadius:20))
                HStack {
                    Text("\(Int(model.fps)) fps · 表示 \(model.drawnTiles) · \(model.memoryMB) MB")
                    Spacer()
                    if model.requests > 0 { ProgressView().tint(.white); Text("取得中") }
                }.font(.caption.monospacedDigit()).padding(.horizontal,8).padding(.top,4)
                if let error = model.rendererError { Text(error).padding().background(.ultraThinMaterial,in:RoundedRectangle(cornerRadius:12)) }
                Spacer()
                HStack(alignment:.bottom) {
                    Joystick { model.movement = $0 }
                    Spacer()
                    VStack(spacing:12) {
                        HoldControl(symbol:"arrow.up",label:"上昇") { model.elevation = $0 ? 1 : 0 }
                        HoldControl(symbol:"arrow.down",label:"下降") { model.elevation = $0 ? -1 : 0 }
                    }
                }
                Text("ドラッグで見回す · 左スティックで移動 · 右ボタンで上下移動")
                    .font(.caption2).padding(.top,10)
            }.padding(.horizontal,16).padding(.top,8).padding(.bottom,14).foregroundStyle(.white)
        }.preferredColorScheme(.dark)
            .onChange(of:model.quality) { _,_ in model.qualityChanged() }
            .sheet(isPresented:$settings) { SettingsView(model:model,importing:$importing) }
            .fileImporter(isPresented:$importing,allowedContentTypes:[.json]) { result in
                if case .success(let url) = result { model.importConfiguration(url) }
            }
            .onChange(of:phase) { _,newValue in model.setActive(newValue == .active) }
            .onReceive(NotificationCenter.default.publisher(for:UIApplication.didReceiveMemoryWarningNotification)) { _ in model.memoryWarning() }
            .onReceive(NotificationCenter.default.publisher(for:ProcessInfo.thermalStateDidChangeNotification)) { _ in
                if ProcessInfo.processInfo.thermalState == .serious || ProcessInfo.processInfo.thermalState == .critical {
                    model.quality = 0; model.memoryWarning()
                }
            }
            .onOpenURL { model.importConfiguration($0) }
    }
}

struct SettingsView: View {
    @ObservedObject var model: ExplorerModel
    @Binding var importing: Bool
    @Environment(\.dismiss) var dismiss
    @State var latitude = "35.6586"
    @State var longitude = "139.7454"
    var body: some View {
        NavigationStack {
            Form {
                Section("移動先") {
                    Button("東京タワー") { model.relocate(latitude:35.6586,longitude:139.7454,label:"東京タワー"); dismiss() }
                    Button("ホノルル・ワイキキ") { model.relocate(latitude:21.2828,longitude:-157.8369,label:"ワイキキ"); dismiss() }
                    TextField("緯度",text:$latitude).keyboardType(.numbersAndPunctuation)
                    TextField("経度",text:$longitude).keyboardType(.numbersAndPunctuation)
                    Button("この座標へ移動") {
                        if let lat = Double(latitude), let lon = Double(longitude) {
                            model.relocate(latitude:lat,longitude:lon,label:"\(lat), \(lon)"); dismiss()
                        }
                    }
                }
                Section("描画と移動") {
                    Picker("画質",selection:$model.quality) { Text("軽量").tag(0); Text("標準").tag(1) }.pickerStyle(.segmented)
                    Text("描画範囲 \(Int(model.viewDistance)) m")
                    Slider(value:$model.viewDistance,in:120...600,step:10)
                    Toggle("移動・新規取得を一時停止",isOn:$model.paused)
                    Button("視点をリセット") { model.camera = CameraState(); dismiss() }
                }
                Section("接続") {
                    LabeledContent("データ取得",value:"Apple Maps へ直接接続")
                    LabeledContent("状態",value:model.configured ? "設定済み" : "未設定")
                    Button("再接続") { model.retry() }
                    Button("標準の接続設定に戻す") { model.restoreStandardConfiguration() }
                    Button("取得設定を更新") { dismiss(); importing = true }
                    Button("キャッシュを消去",role:.destructive) { model.clearCache() }
                }
            }.navigationTitle("3D Explorer")
                .toolbar { ToolbarItem(placement:.confirmationAction) { Button("完了") { dismiss() } } }
        }
    }
}
