// Atlas HUD — Orb Core Shader
//
// Renders a glowing plasma sphere using procedural fBm noise.
// Applied to the CoreField and CoreGlow Image layers of AtlasCoreOrb.
//
// The Image colour (set via Image.color or AtlasCoreOrb.SetAIIdentity()) is used
// as the plasma tint — it is passed through the vertex colour channel.
//
// Blend: standard alpha compositing so the sphere stacks over the ring layers.
// ─────────────────────────────────────────────────────────────────────────────
Shader "Atlas/OrbCore"
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

        // Controls how much the animated noise shifts the colour
        _PlasmaIntensity ("Plasma Intensity", Range(0.0, 1.0)) = 0.60
        // Noise animation speed
        _FlowSpeed       ("Flow Speed",       Range(0.0, 2.0)) = 0.22

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
            Name "AtlasOrbCore"
            CGPROGRAM
            #pragma vertex   vert
            #pragma fragment frag
            #pragma target   3.0       // Target 3.0 for loops in noise function

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
            float     _PlasmaIntensity;
            float     _FlowSpeed;

            // ── Noise primitives ──────────────────────────────────────────────

            float2 hash2(float2 p)
            {
                p = float2(dot(p, float2(127.1f, 311.7f)),
                           dot(p, float2(269.5f, 183.3f)));
                return -1.0f + 2.0f * frac(sin(p) * 43758.545f);
            }

            float vnoise(float2 p)
            {
                float2 i = floor(p);
                float2 f = frac(p);
                float2 u = f * f * (3.0f - 2.0f * f);
                return lerp(lerp(dot(hash2(i + float2(0,0)), f - float2(0,0)),
                                 dot(hash2(i + float2(1,0)), f - float2(1,0)), u.x),
                            lerp(dot(hash2(i + float2(0,1)), f - float2(0,1)),
                                 dot(hash2(i + float2(1,1)), f - float2(1,1)), u.x), u.y);
            }

            // fBm — 4 octaves
            float fbm(float2 p)
            {
                float v = 0.0f;
                float a = 0.5f;
                float2 shift = float2(100.0f, 100.0f);
                float2x2 rot = float2x2(cos(0.5f), sin(0.5f), -sin(0.5f), cos(0.5f));
                for (int i = 0; i < 4; i++)
                {
                    v += a * vnoise(p);
                    p  = mul(rot, p) * 2.0f + shift;
                    a *= 0.5f;
                }
                return v;
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
                float2 uv   = IN.texcoord - 0.5f;          // -0.5..+0.5
                float  dist = length(uv);

                // ── Sphere shape: radial falloff ──────────────────────────────
                float sphere = 1.0f - smoothstep(0.0f, 0.50f, dist);
                sphere       = pow(sphere, 1.8f);           // concentrate towards centre

                // Hard clip at the circle boundary
                if (dist > 0.50f) { clip(-1); return (fixed4)0; }

                // ── Animated plasma noise ─────────────────────────────────────
                float  t       = _Time.y * _FlowSpeed;
                float2 noiseUV = uv * 3.5f + float2(t * 0.31f, t * 0.17f);
                float  plasma  = fbm(noiseUV) * 0.5f + 0.5f;          // 0..1

                // Modulate noise by sphere falloff so edges are dark
                plasma = lerp(0.55f, 1.0f, plasma * sphere);

                // ── Colour ────────────────────────────────────────────────────
                // Vertex colour = AI primary colour
                fixed3 baseRGB = IN.color.rgb;
                // Brighten the centre; mix in a cooler (whiter) core highlight
                float  centreBias  = 1.0f - smoothstep(0.0f, 0.25f, dist);
                fixed3 coreHighlight = fixed3(1.0f, 1.0f, 1.0f);
                fixed3 rgb = lerp(baseRGB, coreHighlight, centreBias * 0.45f);
                rgb *= lerp(1.0f, plasma, _PlasmaIntensity);

                float alpha = sphere * IN.color.a;

                fixed4 color = fixed4(rgb, alpha);

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
