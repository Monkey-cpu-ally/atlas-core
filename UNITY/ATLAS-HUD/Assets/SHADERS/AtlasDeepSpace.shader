// Atlas HUD — Deep Space Background Shader
//
// Renders an animated procedural star field entirely in the fragment shader.
// No texture asset is required.
//
// Visual layers (back to front):
//   • Background gradient: deep navy → near-black
//   • Layer A: fine, dense, dim stars (distant field)
//   • Layer B: coarser, brighter stars (mid-field)
//   • Layer C: sparse bright stars with cross-diffraction spikes
//   • Slow parallax scroll driven by _Time
//   • Subtle moving depth-ray fans (volumetric light shafts suggestion)
//
// Usage:
//   Apply this material to the fullscreen DeepBG Image in each environment.
//   The Image.color tint is multiplied into the final output, allowing
//   per-environment colour temperature shifts.
// ─────────────────────────────────────────────────────────────────────────────
Shader "Atlas/DeepSpace"
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

        // Scroll speed (UV units per second)
        _ScrollSpeed  ("Scroll Speed",  Float) = 0.018
        // Star density multiplier
        _StarDensityA ("Star Density A (fine)",   Float) = 80.0
        _StarDensityB ("Star Density B (mid)",    Float) = 28.0
        _StarDensityC ("Star Density C (bright)", Float) = 12.0
        // Vignette strength (darkens corners)
        _Vignette     ("Vignette",      Range(0.0, 1.5)) = 0.65
        // Depth ray intensity
        _RayIntensity ("Ray Intensity", Range(0.0, 0.35)) = 0.08

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
            Name "AtlasDeepSpace"
            CGPROGRAM
            #pragma vertex   vert
            #pragma fragment frag
            #pragma target   3.0

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
            float     _ScrollSpeed;
            float     _StarDensityA;
            float     _StarDensityB;
            float     _StarDensityC;
            float     _Vignette;
            float     _RayIntensity;

            // ── Hash / noise primitives ────────────────────────────────────────

            float hash11(float n)  { return frac(sin(n) * 43758.5453f); }

            float hash21(float2 p) { return frac(sin(dot(p, float2(127.1f, 311.7f))) * 43758.5453f); }

            float2 hash22(float2 p)
            {
                p = float2(dot(p, float2(127.1f, 311.7f)),
                           dot(p, float2(269.5f, 183.3f)));
                return frac(sin(p) * 43758.5453f);
            }

            // ── Star field layer ───────────────────────────────────────────────
            // Returns star brightness at uv for a grid of `density` cells.
            // Twinkle is modulated by a per-star random phase.
            float starLayer(float2 uv, float density, float minSize, float maxSize, float twinkleSpeed)
            {
                float2 gridUV  = uv * density;
                float2 cell    = floor(gridUV);
                float2 localUV = frac(gridUV) - 0.5f;

                float2 starPos   = hash22(cell) * 0.38f;         // star within cell
                float  starBrightness = hash21(cell + 99.7f);    // 0..1
                float  starSize  = lerp(minSize, maxSize, starBrightness);
                float  phase     = hash21(cell + 7.3f) * 6.283f;
                float  twinkle   = 0.7f + 0.3f * sin(_Time.y * twinkleSpeed + phase);

                float  d = length(localUV - starPos);
                float  star = smoothstep(starSize, 0.0f, d) * starBrightness * twinkle;
                return star;
            }

            // ── Cross diffraction spikes for bright stars ──────────────────────
            float diffSpike(float2 uv, float2 starPos, float starSize, float angle)
            {
                float2 dir  = float2(cos(angle), sin(angle));
                float2 dv   = uv - starPos;
                float  proj = dot(dv, dir);
                float  perp = dot(dv, float2(-dir.y, dir.x));
                float  spike = smoothstep(starSize * 18.0f, 0.0f, abs(proj))
                             * smoothstep(starSize * 0.5f,  0.0f, abs(perp));
                return spike;
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
                float  t  = _Time.y;

                // ── 1. Deep space gradient background ─────────────────────────
                // Near-black navy → very deep navy at top
                float  yGrad  = uv.y * 0.5f;
                fixed3 bgCol  = fixed3(0.007f + yGrad * 0.005f,
                                       0.012f + yGrad * 0.008f,
                                       0.040f + yGrad * 0.018f);

                // ── 2. Star layers (three depths, different scroll speeds) ──────
                float2 scrollA = float2(t * _ScrollSpeed * 0.6f, t * _ScrollSpeed * 0.3f);
                float2 scrollB = float2(t * _ScrollSpeed * 1.0f, t * _ScrollSpeed * 0.5f);
                float2 scrollC = float2(t * _ScrollSpeed * 1.4f, t * _ScrollSpeed * 0.7f);

                float starsA = starLayer(uv + scrollA, _StarDensityA, 0.005f, 0.012f, 1.4f) * 0.40f;
                float starsB = starLayer(uv + scrollB, _StarDensityB, 0.008f, 0.020f, 1.9f) * 0.65f;
                float starsC = starLayer(uv + scrollC, _StarDensityC, 0.012f, 0.030f, 2.5f) * 0.90f;

                fixed3 starCol = fixed3(0.75f, 0.90f, 1.00f);      // cool blue-white stars
                fixed3 stars   = starCol * (starsA + starsB + starsC);

                // ── 3. Bright star diffraction spikes (layer C only) ───────────
                // Re-evaluate layer C to also compute spikes for the 3 brightest cells
                {
                    float2 gridUV = (uv + scrollC) * _StarDensityC;
                    for (int ci = -1; ci <= 1; ci++)
                    for (int ri = -1; ri <= 1; ri++)
                    {
                        float2 cell    = floor(gridUV) + float2(ci, ri);
                        float  bright  = hash21(cell + 99.7f);
                        if (bright > 0.70f)  // only the top 30% of stars
                        {
                            float2 starPos = (cell + hash22(cell) * 0.38f + 0.5f) / _StarDensityC
                                            - scrollC;
                            float  sSize   = lerp(0.012f, 0.030f, bright) / _StarDensityC;
                            float  s1 = diffSpike(uv, starPos, sSize, 0.0f);
                            float  s2 = diffSpike(uv, starPos, sSize, 1.5708f);
                            stars += starCol * (s1 + s2) * bright * 0.5f;
                        }
                    }
                }

                // ── 4. Depth rays ─────────────────────────────────────────────
                // Subtle crepuscular-ray suggestion emanating from top-centre
                float2 rayOrigin = float2(0.5f, 1.1f);
                float2 rayDir    = uv - rayOrigin;
                float  rayAngle  = atan2(rayDir.x, -rayDir.y);    // fan angle
                float  rayDist   = length(rayDir);
                float  rayFan    = abs(sin(rayAngle * 6.0f + t * 0.07f)) * 0.5f;
                rayFan          *= (1.0f - smoothstep(0.2f, 1.2f, rayDist));
                rayFan          *= _RayIntensity;
                fixed3 rayCol    = fixed3(0.05f, 0.25f, 0.60f);
                bgCol           += rayCol * rayFan;

                // ── 5. Vignette ───────────────────────────────────────────────
                float2 vigUV  = uv - 0.5f;
                float  vig    = 1.0f - dot(vigUV * _Vignette, vigUV * _Vignette);
                vig           = saturate(vig);

                // ── Compose ───────────────────────────────────────────────────
                fixed3 finalRGB = (bgCol + saturate(stars)) * vig;
                finalRGB       *= IN.color.rgb;    // Image tint (environment colour shift)
                float  alpha    = IN.color.a;

                fixed4 color = fixed4(finalRGB, alpha);

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
