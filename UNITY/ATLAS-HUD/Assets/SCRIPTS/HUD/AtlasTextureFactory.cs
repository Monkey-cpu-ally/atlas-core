using UnityEngine;

/// <summary>
/// Generates procedural Texture2D and Sprite assets at runtime.
///
/// All results are cached after first use. Nothing is read from disk —
/// every texture is computed from first principles via CPU pixel operations.
///
/// Textures generated:
///   • RingSprite         — unused (ring shape now handled by AtlasOrbRing shader)
///   • GlowCircle         — radial glow gradient circle (status dots, particles)
///   • ScanLineOverlay    — 1×4 repeating scanline band (panel overlay)
///   • HexDiamondGrid     — 256×256 diagonal grid for backgrounds
///   • RoundedRectButton  — 128×40 dark-blue button with rounded corners + glow border
///   • RoundedRectCard    — 260×160 card face with rounded corners + glow border
///   • CornerBracketTL    — 32×32 top-left L-bracket corner accent
///   • GlowDivider        — 256×4 horizontal line with centre-bright glow falloff
///   • PortraitPlaceholder— 128×128 silhouette-style AI portrait placeholder
///   • IconAtlas          — 256×32 row of five minimalist HUD icons
/// </summary>
public static class AtlasTextureFactory
{
    // ── Cached instances ──────────────────────────────────────────────────────

    private static Texture2D _glowCircle;
    private static Texture2D _scanLine;
    private static Texture2D _hexGrid;
    private static Texture2D _roundedBtn;
    private static Texture2D _roundedCard;
    private static Texture2D _cornerBracket;
    private static Texture2D _glowDivider;
    private static Texture2D _portraitPlaceholder;
    private static Texture2D _iconAtlas;

    // ── Public accessors ──────────────────────────────────────────────────────

    public static Texture2D GlowCircle          => _glowCircle          ?? (_glowCircle          = BuildGlowCircle(128));
    public static Texture2D ScanLineOverlay     => _scanLine            ?? (_scanLine            = BuildScanLine());
    public static Texture2D HexDiamondGrid      => _hexGrid             ?? (_hexGrid             = BuildDiamondGrid(256, 8, new Color(0f, 0.78f, 1f, 0.06f)));
    public static Texture2D RoundedRectButton   => _roundedBtn          ?? (_roundedBtn          = BuildRoundedRect(128, 40,  6f, new Color(0.00f, 0.25f, 0.55f, 0.82f), HolographicPanel.BorderCyan, 1.5f, 6f));
    public static Texture2D RoundedRectCard     => _roundedCard         ?? (_roundedCard         = BuildRoundedRect(260, 160, 8f, new Color(0.03f, 0.07f, 0.16f, 0.90f), HolographicPanel.BorderCyan, 1.5f, 10f));
    public static Texture2D CornerBracketTL     => _cornerBracket       ?? (_cornerBracket       = BuildCornerBracket(32));
    public static Texture2D GlowDivider         => _glowDivider         ?? (_glowDivider         = BuildGlowDivider(256, 4));
    public static Texture2D PortraitPlaceholder => _portraitPlaceholder ?? (_portraitPlaceholder = BuildPortraitPlaceholder(128));
    public static Texture2D IconAtlas           => _iconAtlas           ?? (_iconAtlas           = BuildIconAtlas(256, 32));

    // Creates a Sprite from a Texture2D with the default full-rect pivot.
    public static Sprite MakeSprite(Texture2D tex)
        => Sprite.Create(tex, new Rect(0, 0, tex.width, tex.height),
                         new Vector2(0.5f, 0.5f), tex.width);

    // ── Builders ──────────────────────────────────────────────────────────────

    // Radial glow gradient: opaque bright centre, transparent at radius.
    private static Texture2D BuildGlowCircle(int size)
    {
        var tex  = new Texture2D(size, size, TextureFormat.RGBA32, false);
        tex.filterMode = FilterMode.Bilinear;
        tex.wrapMode   = TextureWrapMode.Clamp;

        float half = size * 0.5f;
        var   px   = new Color[size * size];

        for (int y = 0; y < size; y++)
        for (int x = 0; x < size; x++)
        {
            float dist  = Vector2.Distance(new Vector2(x, y), new Vector2(half, half)) / half;
            float alpha = Mathf.Clamp01(1f - dist * dist);              // quadratic falloff
            alpha       = Mathf.Pow(alpha, 1.6f);
            px[y * size + x] = new Color(1f, 1f, 1f, alpha);
        }

        tex.SetPixels(px);
        tex.Apply(false, true);
        return tex;
    }

    // 1×4 scanline strip: transparent / transparent / dark / transparent
    // Tiled over a panel gives horizontal banding without GPU shader overhead.
    private static Texture2D BuildScanLine()
    {
        var tex = new Texture2D(1, 4, TextureFormat.RGBA32, false);
        tex.filterMode = FilterMode.Point;
        tex.wrapMode   = TextureWrapMode.Repeat;
        tex.SetPixels(new[]
        {
            new Color(0f, 0f, 0f, 0.00f),
            new Color(0f, 0f, 0f, 0.00f),
            new Color(0f, 0f, 0f, 0.10f),
            new Color(0f, 0f, 0f, 0.00f),
        });
        tex.Apply(false, true);
        return tex;
    }

    // Diagonal diamond grid: two families of diagonal lines at 45°.
    private static Texture2D BuildDiamondGrid(int size, int cellPx, Color lineColor)
    {
        var tex  = new Texture2D(size, size, TextureFormat.RGBA32, false);
        tex.filterMode = FilterMode.Bilinear;
        tex.wrapMode   = TextureWrapMode.Repeat;

        float lineWidth = 0.8f;     // pixels
        var   px        = new Color[size * size];

        for (int y = 0; y < size; y++)
        for (int x = 0; x < size; x++)
        {
            // Two diagonal families
            float d1 = Mathf.Abs(Mathf.Sin((x + y) * Mathf.PI / cellPx));
            float d2 = Mathf.Abs(Mathf.Sin((x - y) * Mathf.PI / cellPx));
            float g  = Mathf.Min(d1, d2);
            float a  = 1f - Mathf.SmoothStep(0f, lineWidth / cellPx, g);

            Color c = lineColor;
            c.a *= a;
            px[y * size + x] = c;
        }

        tex.SetPixels(px);
        tex.Apply(false, true);
        return tex;
    }

    // Rounded-rectangle with optional glow border.
    private static Texture2D BuildRoundedRect(int w, int h, float cornerR,
        Color fill, Color borderColor, float borderWidth, float glowRadius)
    {
        var tex = new Texture2D(w, h, TextureFormat.RGBA32, false);
        tex.filterMode = FilterMode.Bilinear;
        tex.wrapMode   = TextureWrapMode.Clamp;

        var px = new Color[w * h];

        for (int y = 0; y < h; y++)
        for (int x = 0; x < w; x++)
        {
            float fx = x + 0.5f;
            float fy = y + 0.5f;

            // Signed distance from rounded-rect interior (negative = inside)
            float sdf = RoundedRectSDF(fx, fy, w, h, cornerR);

            float fillA   = Mathf.Clamp01(-sdf / 1.0f);                         // inside = 1
            fillA         = Mathf.SmoothStep(0f, 1f, fillA);

            float borderA = Mathf.Clamp01((sdf + borderWidth) / 1.0f)           // near edge
                          * Mathf.Clamp01(1f - sdf / borderWidth);
            float glowA   = Mathf.Clamp01(1f - sdf / glowRadius) * 0.4f;        // outer glow

            Color c = fill * fillA;
            c += borderColor * borderA * borderColor.a;
            c.a = fillA * fill.a + Mathf.Max(borderA * borderColor.a, glowA);
            c.a = Mathf.Clamp01(c.a);

            px[y * w + x] = c;
        }

        tex.SetPixels(px);
        tex.Apply(false, true);
        return tex;
    }

    // Rounded-rect SDF: negative = inside, positive = outside.
    private static float RoundedRectSDF(float px, float py, int w, int h, float r)
    {
        float cx = w * 0.5f;
        float cy = h * 0.5f;
        float qx = Mathf.Abs(px - cx) - (cx - r);
        float qy = Mathf.Abs(py - cy) - (cy - r);
        return Mathf.Sqrt(Mathf.Max(qx, 0f) * Mathf.Max(qx, 0f) +
                          Mathf.Max(qy, 0f) * Mathf.Max(qy, 0f))
               + Mathf.Min(Mathf.Max(qx, qy), 0f) - r;
    }

    // 32×32 top-left corner bracket (L-shape: top bar + left bar, 2px thick).
    private static Texture2D BuildCornerBracket(int size)
    {
        var tex = new Texture2D(size, size, TextureFormat.RGBA32, false);
        tex.filterMode = FilterMode.Point;
        tex.wrapMode   = TextureWrapMode.Clamp;

        Color on  = HolographicPanel.BorderCyan;
        Color off = Color.clear;
        var   px  = new Color[size * size];

        int thick = 2;
        int arm   = size - 2;           // arm length in pixels

        for (int y = 0; y < size; y++)
        for (int x = 0; x < size; x++)
        {
            // Top bar: y near top, x within arm length
            bool topBar  = (y >= size - thick) && (x < arm);
            // Left bar: x near left, y within arm length
            bool leftBar = (x < thick) && (y >= size - arm);

            px[y * size + x] = (topBar || leftBar) ? on : off;
        }

        tex.SetPixels(px);
        tex.Apply(false, true);
        return tex;
    }

    // Horizontal glow divider: centre-bright, fades to transparent at sides.
    private static Texture2D BuildGlowDivider(int w, int h)
    {
        var tex = new Texture2D(w, h, TextureFormat.RGBA32, false);
        tex.filterMode = FilterMode.Bilinear;
        tex.wrapMode   = TextureWrapMode.Clamp;

        var   px      = new Color[w * h];
        Color cyan    = HolographicPanel.BorderCyan;

        for (int y = 0; y < h; y++)
        for (int x = 0; x < w; x++)
        {
            // Horizontal centre-bright gradient
            float tx = x / (float)(w - 1);
            float gx = 1f - Mathf.Abs(tx - 0.5f) * 2f;         // 0 at edges → 1 at centre
            gx       = Mathf.Pow(gx, 0.6f);

            // Vertical: bright at centre of the 4px height
            float ty = (y + 0.5f) / h;
            float gy = 1f - Mathf.Abs(ty - 0.5f) * 2f;         // row intensity

            Color c = cyan;
            c.a     = gx * gy * 0.85f;
            px[y * w + x] = c;
        }

        tex.SetPixels(px);
        tex.Apply(false, true);
        return tex;
    }

    // Portrait placeholder: concentric hexagonal scan lines + humanoid silhouette hint.
    private static Texture2D BuildPortraitPlaceholder(int size)
    {
        var tex = new Texture2D(size, size, TextureFormat.RGBA32, false);
        tex.filterMode = FilterMode.Bilinear;
        tex.wrapMode   = TextureWrapMode.Clamp;

        Color cyan = HolographicPanel.BorderCyan;
        var   px   = new Color[size * size];
        float half = size * 0.5f;

        for (int y = 0; y < size; y++)
        for (int x = 0; x < size; x++)
        {
            float fx = (x - half) / half;   // -1..+1
            float fy = (y - half) / half;

            // Concentric rings
            float dist   = Mathf.Sqrt(fx * fx + fy * fy);
            float rings  = Mathf.Abs(Mathf.Sin(dist * Mathf.PI * 5f));
            float ringA  = Mathf.Pow(Mathf.Clamp01(rings), 4f) * 0.35f;

            // Diagonal scan lines
            float scan   = Mathf.Abs(Mathf.Sin((fx + fy) * Mathf.PI * 6f));
            float scanA  = Mathf.Pow(scan, 6f) * 0.12f;

            // Circular clip
            float clip   = 1f - Mathf.SmoothStep(0.90f, 1.0f, dist);

            Color c = new Color(cyan.r, cyan.g, cyan.b, (ringA + scanA) * clip);
            px[y * size + x] = c;
        }

        tex.SetPixels(px);
        tex.Apply(false, true);
        return tex;
    }

    // 256×32 icon atlas: five 32×32 icons side by side.
    // Icons (L→R): ATLAS (hex), AI HUB (grid), WORKSPACE (person), ARCHIVE (book), OPS (cog)
    private static Texture2D BuildIconAtlas(int w, int h)
    {
        var tex = new Texture2D(w, h, TextureFormat.RGBA32, false);
        tex.filterMode = FilterMode.Bilinear;
        tex.wrapMode   = TextureWrapMode.Clamp;

        Color on  = HolographicPanel.TextAccent;
        Color off = Color.clear;
        var   px  = new Color[w * h];

        // All icons are 32×32, 5 columns
        int iconW = w / 5;
        for (int i = 0; i < 5; i++)
            DrawIcon(px, w, h, i * iconW, iconW, h, i, on);

        tex.SetPixels(px);
        tex.Apply(false, true);
        return tex;
    }

    private static void DrawIcon(Color[] px, int texW, int texH,
        int ox, int iw, int ih, int iconIndex, Color on)
    {
        float halfW = iw * 0.5f;
        float halfH = ih * 0.5f;
        float pad   = 2f;

        for (int y = 0; y < ih; y++)
        for (int x = 0; x < iw; x++)
        {
            float fx = (x - halfW) / (halfW - pad);   // -1..+1 within icon
            float fy = (y - halfH) / (halfH - pad);
            float a  = 0f;

            switch (iconIndex)
            {
                case 0: // ATLAS — hexagon outline
                {
                    float hex = HexSDF(fx, fy, 0.70f);
                    a = 1f - Mathf.SmoothStep(-0.06f, -0.01f, hex);    // thin outline
                    a = Mathf.Max(a, Mathf.SmoothStep(-0.04f, -0.00f, hex)
                                   - Mathf.SmoothStep(-0.52f, -0.48f, hex)); // ring
                    break;
                }
                case 1: // AI HUB — 3×3 dot grid
                {
                    for (int gx = -1; gx <= 1; gx++)
                    for (int gy = -1; gy <= 1; gy++)
                    {
                        float px2 = fx - gx * 0.6f;
                        float py2 = fy - gy * 0.6f;
                        float  d  = Mathf.Sqrt(px2 * px2 + py2 * py2);
                        a = Mathf.Max(a, 1f - Mathf.SmoothStep(0.06f, 0.12f, d));
                    }
                    break;
                }
                case 2: // WORKSPACE — simplified person silhouette
                {
                    // Head (circle at top)
                    float headX = fx;
                    float headY = fy - 0.42f;
                    float hd    = Mathf.Sqrt(headX * headX + headY * headY);
                    float body  = Mathf.Max(0f, 1f - Mathf.Abs(fx) * 2.0f)
                                * Mathf.Max(0f, 1f - Mathf.Abs(fy + 0.18f) * 2.5f);
                    a = Mathf.Max(1f - Mathf.SmoothStep(0.18f, 0.24f, hd),
                                  Mathf.SmoothStep(0.0f, 0.15f, body));
                    break;
                }
                case 3: // ARCHIVE — book / stacked lines
                {
                    // Outer rect
                    float rx = Mathf.Abs(fx) - 0.68f;
                    float ry = Mathf.Abs(fy) - 0.78f;
                    a = 1f - Mathf.SmoothStep(-0.05f, -0.00f, Mathf.Max(rx, ry));
                    // Inner lines
                    for (int li = -2; li <= 2; li++)
                    {
                        float lineY = fy - li * 0.22f;
                        float lineA = 1f - Mathf.SmoothStep(0.03f, 0.06f, Mathf.Abs(lineY));
                        lineA *= 1f - Mathf.SmoothStep(-0.60f, -0.55f, Mathf.Max(rx, -1f));
                        a = Mathf.Max(a, lineA * 0.55f);
                    }
                    break;
                }
                case 4: // OPS — cog (circle with teeth)
                {
                    float dist  = Mathf.Sqrt(fx * fx + fy * fy);
                    float angle = Mathf.Atan2(fy, fx);
                    float teeth = Mathf.Sin(angle * 8f);
                    float outerR = 0.75f + teeth * 0.12f;
                    float innerR = 0.38f;
                    // Ring: outer to inner
                    a  = Mathf.Max(0f, 1f - Mathf.SmoothStep(outerR - 0.08f, outerR, dist));
                    a -= Mathf.Clamp01(1f - Mathf.SmoothStep(innerR - 0.05f, innerR, dist));
                    // Centre dot
                    a = Mathf.Max(a, 1f - Mathf.SmoothStep(0.12f, 0.16f, dist));
                    a = Mathf.Clamp01(a);
                    break;
                }
            }

            int idx = (y * texW) + (ox + x);
            if (idx >= 0 && idx < px.Length)
            {
                Color c = on;
                c.a     = a;
                px[idx] = c;
            }
        }
    }

    // Hexagon SDF (negative inside, positive outside).
    private static float HexSDF(float x, float y, float size)
    {
        float px = Mathf.Abs(x);
        float py = Mathf.Abs(y);
        float kx = -0.866025f;
        float ky =  0.5f;
        float d  = Mathf.Clamp(2f * (kx * px + ky * py), -1f, 1f);
        px -= kx * d * 2f;
        py -= ky * d * 2f;
        float dx = px - Mathf.Clamp(px, -size, size);
        float dy = py - size;
        return Mathf.Sign(py - size) * Mathf.Sqrt(dx * dx + dy * dy);
    }

    // ── Per-AI face portrait ───────────────────────────────────────────────────

    private static System.Collections.Generic.Dictionary<int, Texture2D> _faceCache;

    /// <summary>
    /// Generates (or returns from cache) a 128×128 holographic line-art portrait
    /// texture for the given AI identity and expression state.
    ///
    /// All seven PortraitExpression values produce visually distinct results.
    /// Each of the four recognised identities (Atlas, Ajani, Hermes, Minerva) has
    /// a unique head silhouette and identity detail.
    ///
    /// Combat expression is fully rendered for Ajani; other identities fall back to
    /// Serious for Combat so the caller never needs to special-case it.
    /// </summary>
    public static Texture2D BuildPortraitFace(AIIdentity identity,
        PortraitExpression expression, Color primaryColor)
    {
        if (_faceCache == null)
            _faceCache = new System.Collections.Generic.Dictionary<int, Texture2D>();

        int key = ((int)identity << 8) | (int)expression;
        Texture2D cached;
        if (_faceCache.TryGetValue(key, out cached) && cached != null)
            return cached;

        var tex = GenerateFaceTex(identity, expression, primaryColor, 128);
        _faceCache[key] = tex;
        return tex;
    }

    // ── Face params ─────────────────────────────────────────────────────────

    private struct FaceParams
    {
        // Head ellipse (centred at (0, headCY) in UV [-1,1] space)
        public float headW, headH, headCY;
        // Eyes: mirrored at ±eyeX, centred at eyeY
        public float eyeX, eyeY, eyeW, eyeH;
        // Brows: one brow centred at (±eyeX, browY), extends ±browHW outward
        public float browY, browHW, browThick;
        // base brow slope (positive = outer corner UP for each eye)
        public float browSlope;
        // Nose
        public float noseY, noseHW;
        // Mouth
        public float mouthY, mouthHW, mouthThick;
    }

    private struct ExprParams
    {
        public float browRaise;       // overall Y offset for both brows
        public float slopeDelta;      // added to browSlope (+= outer up, -= outer down/concerned)
        public float eyeVScale;       // multiplier on eyeH (1=normal, 0.5=squint, 1.3=wide)
        public float pupilDY;         // pupil Y offset inside eye (+ = looking up)
        public float mouthCurve;      // +1=full smile, -1=full frown
        public float mouthOpen;       // 0=closed line, 1=fully open
        public float glowBoost;       // extra radial glow intensity
        public bool  scanLines;       // analytical scan-line overlay (Thinking)
        public bool  warMarks;        // diagonal cheek marks (Ajani Combat only)
    }

    private static FaceParams GetFaceParams(AIIdentity id)
    {
        switch (id)
        {
            case AIIdentity.Ajani:   // Bold, angular, strong jaw
                return new FaceParams
                {
                    headW=0.50f, headH=0.64f, headCY=0.06f,
                    eyeX=0.18f,  eyeY=0.28f, eyeW=0.068f, eyeH=0.030f,
                    browY=0.42f, browHW=0.11f, browThick=0.022f, browSlope=-0.03f,
                    noseY=0.07f, noseHW=0.06f,
                    mouthY=-0.16f, mouthHW=0.22f, mouthThick=0.018f,
                };
            case AIIdentity.Hermes: // Lean, technical, thin-framed
                return new FaceParams
                {
                    headW=0.44f, headH=0.68f, headCY=0.05f,
                    eyeX=0.15f,  eyeY=0.29f, eyeW=0.072f, eyeH=0.027f,
                    browY=0.43f, browHW=0.09f, browThick=0.016f, browSlope=0.01f,
                    noseY=0.09f, noseHW=0.05f,
                    mouthY=-0.17f, mouthHW=0.17f, mouthThick=0.016f,
                };
            case AIIdentity.Minerva: // Smooth oval, large eyes
                return new FaceParams
                {
                    headW=0.51f, headH=0.66f, headCY=0.06f,
                    eyeX=0.17f,  eyeY=0.30f, eyeW=0.072f, eyeH=0.044f,
                    browY=0.44f, browHW=0.10f, browThick=0.020f, browSlope=0.04f,
                    noseY=0.10f, noseHW=0.05f,
                    mouthY=-0.15f, mouthHW=0.19f, mouthThick=0.018f,
                };
            default:                // Atlas — balanced, slightly geometric
                return new FaceParams
                {
                    headW=0.52f, headH=0.62f, headCY=0.06f,
                    eyeX=0.17f,  eyeY=0.29f, eyeW=0.070f, eyeH=0.035f,
                    browY=0.42f, browHW=0.10f, browThick=0.019f, browSlope=0.00f,
                    noseY=0.09f, noseHW=0.055f,
                    mouthY=-0.14f, mouthHW=0.20f, mouthThick=0.018f,
                };
        }
    }

    private static ExprParams GetExprParams(PortraitExpression expr, AIIdentity id)
    {
        switch (expr)
        {
            case PortraitExpression.Neutral:
                return new ExprParams
                {
                    browRaise=0f, slopeDelta=0f, eyeVScale=1.0f,
                    pupilDY=0f, mouthCurve=0f, mouthOpen=0f,
                    glowBoost=0f, scanLines=false, warMarks=false,
                };
            case PortraitExpression.Thinking:
                return new ExprParams
                {
                    browRaise=0.04f, slopeDelta=0.04f, eyeVScale=0.88f,
                    pupilDY=0.4f, mouthCurve=-0.05f, mouthOpen=0f,
                    glowBoost=0.30f, scanLines=true, warMarks=false,
                };
            case PortraitExpression.Speaking:
                return new ExprParams
                {
                    browRaise=0.03f, slopeDelta=0f, eyeVScale=1.18f,
                    pupilDY=0f, mouthCurve=0.1f, mouthOpen=0.60f,
                    glowBoost=0.50f, scanLines=false, warMarks=false,
                };
            case PortraitExpression.Approval:
                return new ExprParams
                {
                    browRaise=0.04f, slopeDelta=0.06f, eyeVScale=0.82f,
                    pupilDY=0f, mouthCurve=0.88f, mouthOpen=0.12f,
                    glowBoost=0.20f, scanLines=false, warMarks=false,
                };
            case PortraitExpression.Concern:
                return new ExprParams
                {
                    browRaise=0.02f, slopeDelta=-0.26f, eyeVScale=1.22f,
                    pupilDY=0f, mouthCurve=-0.55f, mouthOpen=0.08f,
                    glowBoost=0.12f, scanLines=false, warMarks=false,
                };
            case PortraitExpression.Serious:
                return new ExprParams
                {
                    browRaise=-0.02f, slopeDelta=-0.08f, eyeVScale=0.70f,
                    pupilDY=0f, mouthCurve=-0.10f, mouthOpen=0f,
                    glowBoost=0.08f, scanLines=false, warMarks=false,
                };
            case PortraitExpression.Combat:
                // Only Ajani has true Combat — other identities reuse Serious params
                if (id != AIIdentity.Ajani)
                    return GetExprParams(PortraitExpression.Serious, id);
                return new ExprParams
                {
                    browRaise=-0.03f, slopeDelta=-0.32f, eyeVScale=0.58f,
                    pupilDY=-0.15f, mouthCurve=-0.05f, mouthOpen=0f,
                    glowBoost=1.0f, scanLines=false, warMarks=true,
                };
            default:
                return new ExprParams { eyeVScale=1.0f };
        }
    }

    // ── Core generator ───────────────────────────────────────────────────────

    private static Texture2D GenerateFaceTex(AIIdentity id,
        PortraitExpression expr, Color primary, int size)
    {
        var tex = new Texture2D(size, size, TextureFormat.RGBA32, false);
        tex.filterMode = FilterMode.Bilinear;
        tex.wrapMode   = TextureWrapMode.Clamp;
        tex.hideFlags  = HideFlags.DontSave;

        FaceParams fp = GetFaceParams(id);
        ExprParams ep = GetExprParams(expr, id);

        float half = size * 0.5f;
        var   px   = new Color[size * size];

        float effectiveEyeH = fp.eyeH * ep.eyeVScale;
        float browY         = fp.browY + ep.browRaise;
        float browSlope     = fp.browSlope + ep.slopeDelta;

        for (int y = 0; y < size; y++)
        for (int x = 0; x < size; x++)
        {
            float fx = (x + 0.5f - half) / half;   // −1 … +1
            float fy = (y + 0.5f - half) / half;

            // ── Background: deep dark + radial AI-colour glow ────────────
            float rDist = Mathf.Sqrt(fx * fx + fy * fy);
            float bg    = Mathf.Pow(Mathf.Clamp01(1f - rDist), 2.8f)
                          * (0.16f + ep.glowBoost * 0.20f);
            Color c = new Color(primary.r * bg, primary.g * bg, primary.b * bg, 1f);

            // ── Head silhouette ───────────────────────────────────────────
            float hSDF = FaceEllipseSDF(fx, fy - fp.headCY, fp.headW, fp.headH);

            // Interior tint (darker AI colour)
            float headFill = Mathf.SmoothStep(0.02f, -0.02f, hSDF);
            c = Color.Lerp(c,
                new Color(primary.r * 0.14f, primary.g * 0.14f, primary.b * 0.14f, 1f),
                headFill);

            // Outer glow halo
            float haloA = Mathf.Clamp01(1f - Mathf.Abs(hSDF + 0.03f) * 14f) * 0.35f;
            c.r += primary.r * haloA;
            c.g += primary.g * haloA;
            c.b += primary.b * haloA;

            // Crisp outline
            float outlineA = Mathf.Clamp01(1f - Mathf.Abs(hSDF) * 22f) * 0.85f;
            c.r += primary.r * outlineA;
            c.g += primary.g * outlineA;
            c.b += primary.b * outlineA;
            c.a  = 1f;

            // ── Eyes (only inside head) ───────────────────────────────────
            if (effectiveEyeH > 0.005f && hSDF < 0.05f)
            {
                float eyePY = fp.eyeY + ep.pupilDY * fp.eyeH * 0.35f;

                float lEye = FaceEllipseSDF(fx + fp.eyeX, fy - fp.eyeY, fp.eyeW, effectiveEyeH);
                float rEye = FaceEllipseSDF(fx - fp.eyeX, fy - fp.eyeY, fp.eyeW, effectiveEyeH);
                float eyeIn = Mathf.Max(
                    Mathf.SmoothStep(0.015f, -0.015f, lEye),
                    Mathf.SmoothStep(0.015f, -0.015f, rEye));

                // Eye fill (bright AI colour)
                c = Color.Lerp(c, new Color(primary.r, primary.g, primary.b, 1f), eyeIn * 0.88f);

                // Pupil (darker centre)
                float lPup = FaceEllipseSDF(fx + fp.eyeX, fy - eyePY, fp.eyeW * 0.38f, effectiveEyeH * 0.38f);
                float rPup = FaceEllipseSDF(fx - fp.eyeX, fy - eyePY, fp.eyeW * 0.38f, effectiveEyeH * 0.38f);
                float pupIn = Mathf.Max(
                    Mathf.SmoothStep(0.010f, -0.010f, lPup),
                    Mathf.SmoothStep(0.010f, -0.010f, rPup));
                c = Color.Lerp(c,
                    new Color(primary.r * 0.06f, primary.g * 0.06f, primary.b * 0.06f, 1f),
                    pupIn);

                // Eye edge glow
                float eGlowA = Mathf.Max(
                    Mathf.Clamp01(1f - Mathf.Abs(lEye) * 20f),
                    Mathf.Clamp01(1f - Mathf.Abs(rEye) * 20f)) * 0.50f;
                c.r += primary.r * eGlowA;
                c.g += primary.g * eGlowA;
                c.b += primary.b * eGlowA;
                c.a  = 1f;

                // ── Thinking: small upward directional glints ─────────────
                if (ep.scanLines)
                {
                    float glintL = FaceEllipseSDF(fx + fp.eyeX - 0.02f, fy - fp.eyeY + effectiveEyeH * 0.20f,
                                        fp.eyeW * 0.18f, effectiveEyeH * 0.18f);
                    float glintR = FaceEllipseSDF(fx - fp.eyeX + 0.02f, fy - fp.eyeY + effectiveEyeH * 0.20f,
                                        fp.eyeW * 0.18f, effectiveEyeH * 0.18f);
                    float glintA = Mathf.Max(
                        Mathf.SmoothStep(0.008f, -0.008f, glintL),
                        Mathf.SmoothStep(0.008f, -0.008f, glintR));
                    c = Color.Lerp(c, Color.white, glintA * 0.75f);
                }
            }

            // ── Brows ─────────────────────────────────────────────────────
            if (hSDF < 0.06f)
            {
                // Left brow segment: from inner (eyeX, browY) to outer (eyeX+browHW, browY + browHW*slope)
                float lbA = LineStroke(fx, fy,
                     fp.eyeX,              browY,
                     fp.eyeX + fp.browHW,  browY + fp.browHW * browSlope,
                     fp.browThick);
                // Right brow (mirrored): from inner (−eyeX, browY) to outer (−eyeX−browHW, …)
                float rbA = LineStroke(fx, fy,
                    -fp.eyeX,              browY,
                    -fp.eyeX - fp.browHW,  browY + fp.browHW * browSlope,
                     fp.browThick);
                float browA = Mathf.Max(lbA, rbA);
                c.r += primary.r * browA * 0.95f;
                c.g += primary.g * browA * 0.95f;
                c.b += primary.b * browA * 0.95f;
                c.a  = 1f;
            }

            // ── Nose bridge (subtle V lines) ──────────────────────────────
            if (hSDF < 0.04f)
            {
                float nL = LineStroke(fx, fy,
                     0f,             fp.eyeY - 0.02f,
                    -fp.noseHW * 0.4f, fp.noseY,
                     0.010f);
                float nR = LineStroke(fx, fy,
                     0f,             fp.eyeY - 0.02f,
                     fp.noseHW * 0.4f, fp.noseY,
                     0.010f);
                float noseA = Mathf.Max(nL, nR) * 0.35f;
                c.r += primary.r * noseA;
                c.g += primary.g * noseA;
                c.b += primary.b * noseA;
                c.a  = 1f;
            }

            // ── Mouth ─────────────────────────────────────────────────────
            if (hSDF < 0.04f)
            {
                float mouthA = MouthStroke(fx, fy,
                    fp.mouthY, fp.mouthHW,
                    ep.mouthCurve, ep.mouthOpen, fp.mouthThick);
                c.r += primary.r * mouthA * 0.92f;
                c.g += primary.g * mouthA * 0.92f;
                c.b += primary.b * mouthA * 0.92f;
                c.a  = 1f;
            }

            // ── AI-specific identity detail ───────────────────────────────
            c = ApplyFaceDetail(c, fx, fy, primary, id, fp, hSDF);

            // ── Expression overlays ───────────────────────────────────────

            // Thinking — analytical scan lines across forehead
            if (ep.scanLines && hSDF < 0f)
            {
                float scanY = fy - fp.headCY;
                // Lines spaced ~0.09 apart, only in upper head
                float linePattern = Mathf.Abs(Mathf.Sin(scanY * Mathf.PI / 0.09f));
                float lineA = Mathf.Pow(linePattern, 14f) * 0.22f;
                // Restrict to upper half of head
                float upperMask = Mathf.Clamp01((fy - (fp.headCY + 0.05f)) / (fp.headH * 0.55f));
                c.r += primary.r * lineA * upperMask;
                c.g += primary.g * lineA * upperMask;
                c.b += primary.b * lineA * upperMask;
                c.a  = 1f;
            }

            // Combat (Ajani) — diagonal cheek war-marks
            if (ep.warMarks)
            {
                float lMark = LineStroke(fx, fy,
                     fp.eyeX * 0.8f,  fp.eyeY - 0.08f,
                     fp.headW * 0.82f, -0.18f,
                     0.016f);
                float rMark = LineStroke(fx, fy,
                    -fp.eyeX * 0.8f,  fp.eyeY - 0.08f,
                    -fp.headW * 0.82f, -0.18f,
                     0.016f);
                float markA = Mathf.Max(lMark, rMark) * 0.85f;
                c.r += primary.r * markA;
                c.g += primary.g * markA;
                c.b += primary.b * markA;
                c.a  = 1f;
            }

            // ── Circular clip: fade at extreme edges ──────────────────────
            float clipFade = 1f - Mathf.SmoothStep(0.82f, 0.98f, rDist);
            c.a *= clipFade;

            px[y * size + x] = c;
        }

        tex.SetPixels(px);
        tex.Apply(false, true);
        return tex;
    }

    // ── Face SDF helpers ─────────────────────────────────────────────────────

    // Approximate signed distance to an ellipse: negative = inside.
    private static float FaceEllipseSDF(float x, float y, float rx, float ry)
    {
        float k = Mathf.Sqrt((x / rx) * (x / rx) + (y / ry) * (y / ry));
        return (k - 1f) * Mathf.Min(rx, ry);
    }

    // Alpha for a line-segment stroke (1 = on the line, 0 = away).
    private static float LineStroke(float px, float py,
        float x0, float y0, float x1, float y1, float thick)
    {
        float dx = x1 - x0, dy = y1 - y0;
        float len2 = dx * dx + dy * dy;
        if (len2 < 1e-9f) return 0f;
        float t  = Mathf.Clamp01(((px - x0) * dx + (py - y0) * dy) / len2);
        float ex = px - (x0 + t * dx);
        float ey = py - (y0 + t * dy);
        float d  = Mathf.Sqrt(ex * ex + ey * ey);
        return Mathf.Clamp01(1f - Mathf.SmoothStep(0f, thick, d));
    }

    // Mouth: parabolic upper lip, optional lower lip for open mouth.
    private static float MouthStroke(float px, float py,
        float cy, float hw, float curve, float openF, float thick)
    {
        // Clamp to mouth width region
        float xClamped = Mathf.Clamp(px, -hw, hw);
        float t        = xClamped / hw;                          // −1 … +1
        // Upper lip — parabola curving with 'curve'
        float upperY   = cy + curve * 0.06f * (t * t - 0.5f);
        float dUpper   = Mathf.Abs(py - upperY);
        float upperA   = Mathf.Abs(px) <= hw
                         ? Mathf.Clamp01(1f - Mathf.SmoothStep(0f, thick, dUpper))
                         : 0f;

        if (openF < 0.04f) return upperA;

        // Lower lip (open mouth)
        float lowerY = upperY - openF * 0.065f;
        float dLower = Mathf.Abs(py - lowerY);
        float lowerA = Mathf.Abs(px) <= hw
                       ? Mathf.Clamp01(1f - Mathf.SmoothStep(0f, thick, dLower))
                       : 0f;

        // Corner connectors
        float cornerW = 0.014f;
        float lCorner = 0f, rCorner = 0f;
        if (Mathf.Abs(px + hw) < cornerW)
            lCorner = Mathf.Clamp01((py - lowerY) * 18f) * Mathf.Clamp01((upperY - py) * 18f);
        if (Mathf.Abs(px - hw) < cornerW)
            rCorner = Mathf.Clamp01((py - lowerY) * 18f) * Mathf.Clamp01((upperY - py) * 18f);

        return Mathf.Max(upperA, Mathf.Max(lowerA, Mathf.Max(lCorner, rCorner)));
    }

    // ── Per-AI identity details ───────────────────────────────────────────────

    private static Color ApplyFaceDetail(Color c, float fx, float fy,
        Color primary, AIIdentity id, FaceParams fp, float headSDF)
    {
        if (headSDF > 0.06f) return c;   // outside head region — skip

        switch (id)
        {
            case AIIdentity.Ajani:
            {
                // Bold cheekbone accent lines from outer eye toward jaw edge
                float lChk = LineStroke(fx, fy,
                    fp.eyeX * 0.3f,   fp.eyeY - 0.10f,
                    fp.headW * 0.88f, -0.08f,
                    0.013f);
                float rChk = LineStroke(fx, fy,
                   -fp.eyeX * 0.3f,   fp.eyeY - 0.10f,
                   -fp.headW * 0.88f, -0.08f,
                    0.013f);
                float chkA = Mathf.Max(lChk, rChk) * 0.45f;
                c.r += primary.r * chkA;
                c.g += primary.g * chkA;
                c.b += primary.b * chkA;
                c.a  = 1f;
                break;
            }
            case AIIdentity.Hermes:
            {
                // Spectacle oval rings around each eye
                float ringRX = fp.eyeW * 1.55f;
                float ringRY = fp.eyeH * 2.10f;
                float lRing  = Mathf.Abs(FaceEllipseSDF(fx + fp.eyeX, fy - fp.eyeY, ringRX, ringRY));
                float rRing  = Mathf.Abs(FaceEllipseSDF(fx - fp.eyeX, fy - fp.eyeY, ringRX, ringRY));
                float glassA = Mathf.Max(
                    Mathf.Clamp01(1f - lRing * 22f),
                    Mathf.Clamp01(1f - rRing * 22f)) * 0.50f;
                c.r += primary.r * glassA;
                c.g += primary.g * glassA;
                c.b += primary.b * glassA;
                c.a  = 1f;
                // Nose bridge between spectacles
                float bridgeX0 = -fp.eyeX + ringRX;
                float bridgeX1 =  fp.eyeX - ringRX;
                if (bridgeX0 < bridgeX1)
                {
                    float bridgeA = LineStroke(fx, fy,
                        bridgeX0, fp.eyeY, bridgeX1, fp.eyeY, 0.009f) * 0.40f;
                    c.r += primary.r * bridgeA;
                    c.g += primary.g * bridgeA;
                    c.b += primary.b * bridgeA;
                    c.a  = 1f;
                }
                break;
            }
            case AIIdentity.Minerva:
            {
                // Three crown dots above the head
                float crownY  = fp.headCY + fp.headH * 0.96f;
                float[] cxArr = { -0.11f, 0f, 0.11f };
                float[] crArr = {  0.020f, 0.028f, 0.020f };
                for (int i = 0; i < 3; i++)
                {
                    float dotSDF = FaceEllipseSDF(fx - cxArr[i], fy - crownY, crArr[i], crArr[i]);
                    float dotA   = Mathf.SmoothStep(0.008f, -0.008f, dotSDF);
                    c.r = Mathf.Lerp(c.r, primary.r, dotA);
                    c.g = Mathf.Lerp(c.g, primary.g, dotA);
                    c.b = Mathf.Lerp(c.b, primary.b, dotA);
                    c.a = 1f;
                }
                break;
            }
            case AIIdentity.Atlas:
            {
                // Three horizontal data lines across the upper forehead
                float baseY = fp.headCY + fp.headH * 0.70f;
                for (int li = 0; li < 3; li++)
                {
                    float lineY  = baseY - li * 0.09f;
                    float lineHW = fp.headW * (0.78f - li * 0.10f);
                    // Only inside head
                    float headCheck = FaceEllipseSDF(fx, fy - fp.headCY, fp.headW, fp.headH);
                    if (headCheck < 0f)
                    {
                        float lineA = LineStroke(fx, fy, -lineHW, lineY, lineHW, lineY, 0.007f) * 0.42f;
                        c.r += primary.r * lineA;
                        c.g += primary.g * lineA;
                        c.b += primary.b * lineA;
                        c.a  = 1f;
                    }
                }
                break;
            }
        }
        return c;
    }
}
