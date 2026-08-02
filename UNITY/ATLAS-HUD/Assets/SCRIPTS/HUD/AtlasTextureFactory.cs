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
}
