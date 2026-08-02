// Atlas HUD — Orb Ring Shader
//
// Renders a procedural torus / ring shape entirely in the fragment shader.
// No sprite texture is required.
//
// The Image this material is applied to should be sized to the ring diameter
// (e.g. 260 * 0.52 px for the outer ring).  The ring fills ~84% of the Image
// rect so there is room for the glow halo at the edges.
//
// Usage (C#):
//   var mat = new Material(Shader.Find("Atlas/OrbRing"));
//   ringImage.material = mat;
//
// The ring colour comes through the Image.color vertex tint (_Color is not set
// directly — Unity UI passes it via vertex colour).
//
// Blend mode: Additive (SrcAlpha One) so rings glow on dark backgrounds.
// ─────────────────────────────────────────────────────────────────────────────
Shader "Atlas/OrbRing"
{
    Properties
    {
        // Required by Unity UI stencil / clipping system
        _StencilComp      ("Stencil Comparison", Float) = 8
        _Stencil          ("Stencil ID",          Float) = 0
        _StencilOp        ("Stencil Operation",   Float) = 0
        _StencilWriteMask ("Stencil Write Mask",  Float) = 255
        _StencilReadMask  ("Stencil Read Mask",   Float) = 255
        _ColorMask        ("Color Mask",           Float) = 15
        [Toggle(UNITY_UI_ALPHACLIP)] _UseUIAlphaClip ("Use Alpha Clip", Float) = 0

        // Ring geometry (normalised 0..0.5 UV radius units)
        _RingRadius    ("Ring Radius",    Range(0.10, 0.49)) = 0.40
        _CoreHalfWidth ("Core Half Width",Range(0.01, 0.12)) = 0.05
        _GlowHalfWidth ("Glow Half Width",Range(0.01, 0.18)) = 0.09

        // Rotation-reveal: angular brightness variation so the transform
        // rotation is visually apparent even for a circular ring.
        _AngularContrast ("Angular Contrast", Range(0.0, 0.7)) = 0.35

        // Unused texture slot kept for Unity UI compatibility
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
            "CanUseSpriteAtlas" = "True"
        }

        Stencil
        {
            Ref       [_Stencil]
            Comp      [_StencilComp]
            Pass      [_StencilOp]
            ReadMask  [_StencilReadMask]
            WriteMask [_StencilWriteMask]
        }

        Cull     Off
        Lighting Off
        ZWrite   Off
        ZTest    [unity_GUIZTestMode]
        Blend    SrcAlpha One          // Additive — rings glow on dark BG
        ColorMask [_ColorMask]

        Pass
        {
            Name "AtlasOrbRing"
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
            float     _RingRadius;
            float     _CoreHalfWidth;
            float     _GlowHalfWidth;
            float     _AngularContrast;

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
                // ── Ring distance field ──────────────────────────────────────
                float2 uv   = IN.texcoord - 0.5;          // -0.5 to +0.5
                float  dist = length(uv);                 // 0 (center) → ~0.7 (corner)

                float fromRing = abs(dist - _RingRadius);

                // Core: hard line
                float core = 1.0 - smoothstep(_CoreHalfWidth * 0.6, _CoreHalfWidth, fromRing);
                // Glow: soft halo
                float glow = (1.0 - smoothstep(_CoreHalfWidth, _GlowHalfWidth, fromRing)) * 0.55;

                float ringAlpha = saturate(core + glow);

                // Clip outside the inscribed circle of the Image rect
                ringAlpha *= 1.0 - smoothstep(0.48, 0.50, dist);

                // ── Angular brightness variation ─────────────────────────────
                // Creates two subtly brighter arcs diametrically opposite,
                // so the transform rotation (applied by OrbRingLayer) is visible.
                float angle         = atan2(uv.y, uv.x);                    // -PI..+PI
                float angularBias   = (cos(angle * 2.0) + 1.0) * 0.5;      // 0..1, two peaks
                float brightness    = 1.0 - _AngularContrast + _AngularContrast * angularBias;
                ringAlpha          *= brightness;

                fixed4 color  = IN.color;
                color.a      *= ringAlpha;

                // ── Unity UI stencil clip ────────────────────────────────────
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
