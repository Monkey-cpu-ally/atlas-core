// Atlas HUD — Holographic Panel Shader
//
// Adds three visual effects on top of the flat panel fill:
//   1. Animated horizontal scan lines (CRT/hologram band pattern)
//   2. Edge-proximity glow: panels glow brighter near their borders
//   3. Slow animated shimmer: barely-perceptible temporal noise
//
// Applied to the BG_Glow Image inside HolographicPanel.BuildPanelLayers().
// The base panel colour still comes from the Image.color vertex tint.
//
// Blend: SrcAlpha OneMinusSrcAlpha (standard transparent composite).
// ─────────────────────────────────────────────────────────────────────────────
Shader "Atlas/Holographic"
{
    Properties
    {
        _StencilComp      ("Stencil Comparison", Float) = 8
        _Stencil          ("Stencil ID",          Float) = 0
        _StencilOp        ("Stencil Operation",   Float) = 0
        _StencilWriteMask ("Stencil Write Mask",  Float) = 255
        _StencilReadMask  ("Stencil Read Mask",   Float) = 255
        _ColorMask        ("Color Mask",           Float) = 15
        [Toggle(UNITY_UI_ALPHACLIP)] _UseUIAlphaClip ("Use Alpha Clip", Float) = 0

        // Scan lines
        _ScanLineCount  ("Scan Lines per UV unit", Float) = 90.0
        _ScanLineDark   ("Scan Line Darkness",  Range(0.0, 0.5)) = 0.14

        // Edge glow: fraction of panel width that shows the glow gradient
        _EdgeGlowWidth  ("Edge Glow Width (UV)", Range(0.0, 0.40)) = 0.12
        _EdgeGlowAmt    ("Edge Glow Amount",     Range(0.0, 1.0))  = 0.55

        // Shimmer
        _ShimmerSpeed   ("Shimmer Speed",  Float) = 0.45
        _ShimmerAmt     ("Shimmer Amount", Range(0.0, 0.15)) = 0.04

        _MainTex ("Texture", 2D) = "white" {}
    }

    SubShader
    {
        Tags
        {
            "Queue"           = "Transparent"
            "IgnoreProjector" = "True"
            "RenderType"      = "Transparent"
            "PreviewType"     = "Plane"
        }

        Stencil
        {
            Ref       [_Stencil]
            Comp      [_StencilComp]
            Pass      [_StencilOp]
            ReadMask  [_StencilReadMask]
            WriteMask [_StencilWriteMask]
        }

        Cull Off  Lighting Off  ZWrite Off
        ZTest [unity_GUIZTestMode]
        Blend SrcAlpha OneMinusSrcAlpha
        ColorMask [_ColorMask]

        Pass
        {
            Name "AtlasHolographic"
            CGPROGRAM
            #pragma vertex   vert
            #pragma fragment frag
            #pragma target   2.0

            #include "UnityCG.cginc"
            #include "UnityUI.cginc"

            #pragma multi_compile_local _ UNITY_UI_CLIP_RECT
            #pragma multi_compile_local _ UNITY_UI_ALPHACLIP

            struct appdata_t
            {
                float4 vertex   : POSITION;
                float4 color    : COLOR;
                float2 texcoord : TEXCOORD0;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct v2f
            {
                float4 vertex        : SV_POSITION;
                fixed4 color         : COLOR;
                float2 texcoord      : TEXCOORD0;
                float4 worldPosition : TEXCOORD1;
                UNITY_VERTEX_OUTPUT_STEREO
            };

            sampler2D _MainTex;
            float4    _ClipRect;
            float4    _MainTex_ST;
            float     _ScanLineCount;
            float     _ScanLineDark;
            float     _EdgeGlowWidth;
            float     _EdgeGlowAmt;
            float     _ShimmerSpeed;
            float     _ShimmerAmt;

            // Simple fast hash for shimmer
            float hash(float2 p)
            {
                return frac(sin(dot(p, float2(127.1f, 311.7f))) * 43758.545f);
            }

            v2f vert(appdata_t v)
            {
                v2f OUT;
                UNITY_SETUP_INSTANCE_ID(v);
                UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(OUT);
                OUT.worldPosition = v.vertex;
                OUT.vertex        = UnityObjectToClipPos(v.vertex);
                OUT.texcoord      = TRANSFORM_TEX(v.texcoord, _MainTex);
                OUT.color         = v.color;
                return OUT;
            }

            fixed4 frag(v2f IN) : SV_Target
            {
                float2 uv = IN.texcoord;    // 0..1

                fixed4 color = IN.color;

                // ── 1. Scan lines ─────────────────────────────────────────────
                float scanPos   = frac(uv.y * _ScanLineCount);
                float scanLine  = step(0.5f, scanPos);
                color.rgb      *= 1.0f - scanLine * _ScanLineDark;

                // ── 2. Edge glow ──────────────────────────────────────────────
                // Distance from the nearest horizontal/vertical edge (0..0.5)
                float edgeX = min(uv.x, 1.0f - uv.x);
                float edgeY = min(uv.y, 1.0f - uv.y);
                float edge  = min(edgeX, edgeY);
                float glow  = 1.0f - smoothstep(0.0f, _EdgeGlowWidth, edge);
                color.rgb  += glow * _EdgeGlowAmt * color.rgb;

                // ── 3. Shimmer ────────────────────────────────────────────────
                float  t        = _Time.y * _ShimmerSpeed;
                float2 shimUV   = floor(uv * 24.0f) / 24.0f;   // low-frequency grid
                float  shimmer  = hash(shimUV + float2(t, t * 0.7f));
                shimmer         = (shimmer - 0.5f) * _ShimmerAmt;
                color.rgb      += shimmer;

                // ── Clamp and clip ────────────────────────────────────────────
                color.rgb = saturate(color.rgb);

                #ifdef UNITY_UI_CLIP_RECT
                color.a *= UnityGet2DClipping(IN.worldPosition.xy, _ClipRect);
                #endif
                #ifdef UNITY_UI_ALPHACLIP
                clip(color.a - 0.001);
                #endif

                return color;
            }
            ENDCG
        }
    }
}
