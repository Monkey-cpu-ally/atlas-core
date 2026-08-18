using UnityEngine;

/// <summary>
/// Singleton that creates and caches every runtime Material used by the Atlas HUD.
///
/// Call AtlasVisualAssets.Initialize() once at application startup (done by
/// ATLASMANAGER.Bootstrap before any environments are built) so that all
/// other HUD scripts can safely call AtlasVisualAssets.OrbRingMat etc.
///
/// Materials are created with new Material(shader) — each is a standalone
/// instance so per-material property changes don't bleed between UI elements.
/// Colour tinting is handled through Image.color (vertex colour), which all
/// Atlas shaders read from the vertex COLOR channel, not the material _Color
/// property. This means a single shared material instance is safe to use on
/// multiple Image components with different colours.
/// </summary>
public class AtlasVisualAssets : MonoBehaviour
{
    // ── Singleton ─────────────────────────────────────────────────────────────

    public static AtlasVisualAssets Instance { get; private set; }

    // ── Cached materials ──────────────────────────────────────────────────────

    /// <summary>
    /// Applied to OrbRingLayer Image components.
    /// Renders a procedural ring/torus shape with additive blending.
    /// </summary>
    public static Material OrbRingMat { get; private set; }

    /// <summary>
    /// Applied to the CoreField Image inside AtlasCoreOrb.
    /// Renders an animated plasma sphere.
    /// </summary>
    public static Material OrbCoreMat { get; private set; }

    /// <summary>
    /// Applied to the BG_Glow Image inside HolographicPanel.BuildPanelLayers().
    /// Adds animated scan lines, edge glow, and subtle shimmer.
    /// </summary>
    public static Material HolographicMat { get; private set; }

    /// <summary>
    /// Applied to the fullscreen DeepBG Image in each environment.
    /// Renders an animated procedural star field.
    /// </summary>
    public static Material DeepSpaceMat { get; private set; }

    // ── Cached sprites / textures ─────────────────────────────────────────────

    /// <summary>Sprite built from the glow-circle texture (for status dots etc.).</summary>
    public static Sprite GlowCircleSprite { get; private set; }

    /// <summary>Sprite built from the rounded-rect button texture.</summary>
    public static Sprite RoundedButtonSprite { get; private set; }

    /// <summary>Sprite built from the rounded-rect card texture.</summary>
    public static Sprite RoundedCardSprite { get; private set; }

    /// <summary>Sprite for the glow divider (replaces the 1-pixel horizontal rule).</summary>
    public static Sprite GlowDividerSprite { get; private set; }

    /// <summary>Portrait placeholder sprite for AIPortraitPanel.</summary>
    public static Sprite PortraitSprite { get; private set; }

    /// <summary>256×32 icon atlas (five 32×32 icons in a row).</summary>
    public static Texture2D IconAtlas { get; private set; }

    // ── Initialisation ────────────────────────────────────────────────────────

    private static bool _initialised;

    /// <summary>
    /// Call this once before any HUD environments are constructed.
    /// Safe to call multiple times; subsequent calls are no-ops.
    /// </summary>
    public static void Initialize()
    {
        if (_initialised) return;
        _initialised = true;

        // ── Materials ─────────────────────────────────────────────────────────

        OrbRingMat    = CreateMaterial("Atlas/OrbRing",    "OrbRing");
        OrbCoreMat    = CreateMaterial("Atlas/OrbCore",    "OrbCore");
        HolographicMat = CreateMaterial("Atlas/Holographic","Holographic");
        DeepSpaceMat  = CreateMaterial("Atlas/DeepSpace",  "DeepSpace");

        // ── Sprites ───────────────────────────────────────────────────────────

        GlowCircleSprite    = AtlasTextureFactory.MakeSprite(AtlasTextureFactory.GlowCircle);
        RoundedButtonSprite = AtlasTextureFactory.MakeSprite(AtlasTextureFactory.RoundedRectButton);
        RoundedCardSprite   = AtlasTextureFactory.MakeSprite(AtlasTextureFactory.RoundedRectCard);
        GlowDividerSprite   = AtlasTextureFactory.MakeSprite(AtlasTextureFactory.GlowDivider);
        PortraitSprite      = AtlasTextureFactory.MakeSprite(AtlasTextureFactory.PortraitPlaceholder);
        IconAtlas           = AtlasTextureFactory.IconAtlas;

        if (OrbRingMat == null)
            Debug.LogWarning("[AtlasVisualAssets] Atlas/OrbRing shader not found — ring visuals will be plain-colour squares. Ensure Assets/SHADERS/AtlasOrbRing.shader is in the build.");
        if (DeepSpaceMat == null)
            Debug.LogWarning("[AtlasVisualAssets] Atlas/DeepSpace shader not found — backgrounds will be flat colour.");
    }

    // ── MonoBehaviour lifecycle ───────────────────────────────────────────────

    private void Awake()
    {
        if (Instance != null && Instance != this) { Destroy(gameObject); return; }
        Instance = this;
        Initialize();
    }

    // ── Helpers ───────────────────────────────────────────────────────────────

    private static Material CreateMaterial(string shaderName, string matName)
    {
        var shader = Shader.Find(shaderName);
        if (shader == null)
        {
            Debug.LogWarning($"[AtlasVisualAssets] Shader '{shaderName}' not found.");
            return null;
        }
        var mat      = new Material(shader);
        mat.name     = matName;
        mat.hideFlags = HideFlags.DontSave;
        return mat;
    }

    // ── Per-icon sprite extraction from the atlas ─────────────────────────────

    /// <summary>
    /// Returns a Sprite for icon <paramref name="index"/> (0–4) from the 5-icon atlas.
    /// 0=ATLAS, 1=AI HUB, 2=WORKSPACE, 3=ARCHIVE, 4=OPS
    /// </summary>
    public static Sprite GetIconSprite(int index)
    {
        if (IconAtlas == null) return null;
        int iconW = IconAtlas.width / 5;
        int iconH = IconAtlas.height;
        var rect  = new Rect(index * iconW, 0, iconW, iconH);
        return Sprite.Create(IconAtlas, rect, new Vector2(0.5f, 0.5f), iconW);
    }
}
