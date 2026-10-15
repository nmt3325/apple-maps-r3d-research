#include <metal_stdlib>
using namespace metal;

struct Frame {
    float4x4 viewProjection;
    float4 eye;
    float4 forward;
    float4 right;
    float4 up;
    float4 parameters; // aspect, tan(fov/2), time, horizontal draw radius
};
struct MeshVertex { packed_float3 position; packed_float3 normal; packed_float2 uv; };
struct SplatVertex { packed_float3 position; packed_float4 rgba; packed_float3 bary; };
struct MeshOut { float4 position [[position]]; float2 uv; float3 world; };
struct SplatOut { float4 position [[position]]; float4 rgba; float3 bary; float3 world; };
struct SkyOut { float4 position [[position]]; float2 uv; };
struct Coverage { float4 meta; float4 rectangles[256]; };
bool outsideRange(float3 world, constant Frame &frame) {
    float2 delta=world.xz-frame.eye.xz;
    return dot(delta,delta)>frame.parameters.w*frame.parameters.w;
}
bool refined(float3 world, constant Coverage &coverage) {
    for (uint i=0; i<uint(coverage.meta.x); ++i) {
        float4 r=coverage.rectangles[i];
        if (world.x>=r.x && world.x<r.y && world.z>=r.z && world.z<r.w) return true;
    }
    return false;
}

float hash21(float2 p) { return fract(sin(dot(p,float2(127.1,311.7)))*43758.5453); }
float noise(float2 p) {
    float2 i=floor(p), f=fract(p); f=f*f*(3-2*f);
    return mix(mix(hash21(i),hash21(i+float2(1,0)),f.x),
               mix(hash21(i+float2(0,1)),hash21(i+1),f.x),f.y);
}
float3 skyColor(float3 direction, float time) {
    float height=clamp(direction.y,0.0,1.0);
    float3 color=mix(float3(0.35,0.58,0.78),float3(0.08,0.31,0.62),pow(height,0.45));
    float3 sun=normalize(float3(-0.45,0.65,-0.55));
    float s=max(dot(direction,sun),0.0);
    color+=float3(1.0,0.83,0.55)*(pow(s,700.0)*1.8+pow(s,24.0)*0.15);
    float2 p=direction.xz/max(0.12,direction.y)*1.8+float2(time*0.003,0);
    float cloud=noise(p)*0.55+noise(p*2.1)*0.3+noise(p*4.3)*0.15;
    float coverage=smoothstep(0.55,0.76,cloud)*smoothstep(0.02,0.2,height)*0.7;
    return mix(color,float3(0.95,0.96,0.97),coverage);
}
vertex SkyOut skyVertex(uint id [[vertex_id]]) {
    float2 p = id==0 ? float2(-1,-1) : (id==1 ? float2(3,-1) : float2(-1,3));
    SkyOut out; out.position=float4(p,0.9999,1); out.uv=p; return out;
}
fragment float4 skyFragment(SkyOut in [[stage_in]], constant Frame &f [[buffer(1)]]) {
    float3 ray=normalize(f.forward.xyz+f.right.xyz*in.uv.x*f.parameters.x*f.parameters.y+f.up.xyz*in.uv.y*f.parameters.y);
    return float4(skyColor(ray,f.parameters.z),1);
}
vertex MeshOut meshVertex(uint id [[vertex_id]], constant MeshVertex *v [[buffer(0)]],
                          constant Frame &f [[buffer(1)]], constant float4x4 &model [[buffer(2)]]) {
    MeshOut out; float4 world=model*float4(v[id].position,1);
    out.position=f.viewProjection*world; out.world=world.xyz;
    out.uv=float2(v[id].uv.x,1-v[id].uv.y); return out;
}
fragment float4 meshFragment(MeshOut in [[stage_in]], texture2d<float> atlas [[texture(0)]],
                              constant Frame &f [[buffer(1)]], constant Coverage &coverage [[buffer(3)]]) {
    if (outsideRange(in.world,f) || refined(in.world,coverage)) discard_fragment();
    constexpr sampler s(address::clamp_to_edge, filter::linear, mip_filter::linear, max_anisotropy(4));
    float3 rgb=atlas.sample(s,in.uv).rgb;
    return float4(rgb,1);
}
vertex SplatOut splatVertex(uint id [[vertex_id]], constant SplatVertex *v [[buffer(0)]],
                            constant Frame &f [[buffer(1)]], constant float4x4 &model [[buffer(2)]]) {
    SplatOut out; float4 world=model*float4(v[id].position,1);
    out.position=f.viewProjection*world; out.world=world.xyz;
    out.rgba=v[id].rgba; out.bary=v[id].bary; return out;
}
fragment float4 splatFragment(SplatOut in [[stage_in]], constant Frame &f [[buffer(1)]],
                              constant Coverage &coverage [[buffer(3)]]) {
    if (outsideRange(in.world,f) || refined(in.world,coverage)) discard_fragment();
    float product=in.bary.x*in.bary.y*in.bary.z;
    float alpha=min(0.99,in.rgba.a*product*81.0);
    if (alpha < 0.003) discard_fragment();
    float3 rgb=select(in.rgba.rgb/12.92,pow((in.rgba.rgb+0.055)/1.055,float3(2.4)),in.rgba.rgb>0.04045);
    return float4(rgb,alpha);
}
