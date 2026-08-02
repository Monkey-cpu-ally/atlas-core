using System.Collections;
using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// Holographic glass panel component.
///
/// Attach to any panel root RectTransform (via BuildPanelLayers).
/// Drives continuous glow pulsing and occasional flicker to sell the
/// "transparent holographic glass" aesthetic.
///
/// Colour palette constants are declared here so every Atlas HUD script
/// shares a single source of truth for all UI colours.
/// </summary>
[RequireComponent(typeof(RectTransform))]
public class HolographicPanel : MonoBehaviour
{
    // ── Shared colour palette ─────────────────────────────────────────────────

    /// <summary>Full-screen deep background (nearly-black navy).</summary>
    public static readonly Color DeepBackground = new Color(0.01f, 0.02f, 0.07f, 1.00f);

    /// <summary>Panel fill – semi-transparent dark blue.</summary>
    public static readonly Color PanelFill      = new Color(0.03f, 0.07f, 0.16f, 0.88f);

    /// <summary>Glowing outer halo – muted blue.</summary>
    public static readonly Color PanelGlow      = new Color(0.00f, 0.45f, 1.00f, 0.30f);

    /// <summary>Crisp cyan border line.</summary>
    public static readonly Color BorderCyan     = new Color(0.00f, 0.78f, 1.00f, 1.00f);

    /// <summary>Primary body text – pale cyan.</summary>
    public static readonly Color TextPrimary    = new Color(0.72f, 0.92f, 1.00f, 1.00f);

    /// <summary>Accent text – full cyan.</summary>
    public static readonly Color TextAccent     = new Color(0.00f, 1.00f, 1.00f, 1.00f);

    /// <summary>Muted text / secondary labels.</summary>
    public static readonly Color TextMuted      = new Color(0.40f, 0.65f, 0.80f, 1.00f);

    /// <summary>Call-to-action button fill.</summary>
    public static readonly Color ButtonFill     = new Color(0.00f, 0.38f, 0.72f, 0.75f);

    // ── Inspector-configurable pulse settings ────────────────────────────────

    [SerializeField] private float pulseSpeed     = 1.2f;
    [SerializeField] private float glowMinAlpha   = 0.12f;
    [SerializeField] private float glowMaxAlpha   = 0.42f;
    [SerializeField] private float flickerChance  = 0.002f;   // per-frame probability

    // ── Internal references set by BuildPanelLayers ───────────────────────────

    private Image glowImage;

    // ─────────────────────────────────────────────────────────────────────────

    /// <summary>
    /// Called by BuildPanelLayers after all child images are created.
    /// </summary>
    public void Initialize(Image glow)
    {
        glowImage = glow;
        StartCoroutine(GlowRoutine());
    }

    // ── Glow animation ────────────────────────────────────────────────────────

    private IEnumerator GlowRoutine()
    {
        // Random phase offset so panels don't all pulse in unison
        float phase = Random.Range(0f, Mathf.PI * 2f);
        while (true)
        {
            phase += Time.deltaTime * pulseSpeed;
            float alpha = Mathf.Lerp(glowMinAlpha, glowMaxAlpha,
                                     (Mathf.Sin(phase) + 1f) * 0.5f);

            if (Random.value < flickerChance)
                alpha *= Random.Range(0.2f, 0.6f);  // brief flicker

            if (glowImage != null)
            {
                Color c = glowImage.color;
                c.a     = alpha;
                glowImage.color = c;
            }

            yield return null;
        }
    }

    // ── Static factory ────────────────────────────────────────────────────────

    /// <summary>
    /// Builds the multi-layer holographic panel structure inside
    /// <paramref name="root"/> and returns the "Content" RectTransform
    /// where child widgets should be placed.
    ///
    /// Layer order (bottom → top):
    ///   DeepBackground → GlowHalo (holographic shader) → PanelFill → BorderStrips → ScanlineOverlay → Content
    /// </summary>
    public static RectTransform BuildPanelLayers(RectTransform root)
    {
        // 1 – Deepest background
        AtlasUIFactory.CreateBackground("BG_Deep", root, DeepBackground);

        // 2 – Outer glow halo (slightly oversized, rendered before fill)
        //     Uses the Holographic shader for animated scan lines + edge glow.
        var glowRT   = AtlasUIFactory.CreateStretchRect("BG_Glow", root,
            Vector2.zero, Vector2.one, new Vector2(-5, -5), new Vector2(5, 5));
        glowRT.SetSiblingIndex(1);
        var glowImg  = glowRT.gameObject.AddComponent<Image>();
        glowImg.color = PanelGlow;
        if (AtlasVisualAssets.HolographicMat != null)
            glowImg.material = AtlasVisualAssets.HolographicMat;

        // 3 – Panel fill
        AtlasUIFactory.CreateBackground("BG_Fill", root, PanelFill);

        // 4 – Four border strips (top / bottom / left / right)
        //     Use the glow-divider sprite for top/bottom to add a glow falloff.
        AtlasUIFactory.CreateBorderStrip("Border_Top",    root, horizontal: true,  isTopOrLeft: true,  BorderCyan);
        AtlasUIFactory.CreateBorderStrip("Border_Bottom", root, horizontal: true,  isTopOrLeft: false, BorderCyan);
        AtlasUIFactory.CreateBorderStrip("Border_Left",   root, horizontal: false, isTopOrLeft: true,  BorderCyan);
        AtlasUIFactory.CreateBorderStrip("Border_Right",  root, horizontal: false, isTopOrLeft: false, BorderCyan);

        // 5 – Scanline overlay (full stretch, very low alpha)
        if (AtlasTextureFactory.ScanLineOverlay != null)
        {
            var slGO       = new GameObject("ScanlineOverlay");
            slGO.transform.SetParent(root, false);
            var slRT       = slGO.AddComponent<RectTransform>();
            slRT.anchorMin = Vector2.zero;
            slRT.anchorMax = Vector2.one;
            slRT.offsetMin = Vector2.zero;
            slRT.offsetMax = Vector2.zero;
            var slImg              = slGO.AddComponent<UnityEngine.UI.RawImage>();
            slImg.texture          = AtlasTextureFactory.ScanLineOverlay;
            slImg.color            = new Color(1f, 1f, 1f, 1f);
            slImg.uvRect           = new Rect(0, 0, 1f, 60f);   // tile vertically
            slImg.raycastTarget    = false;
        }

        // 6 – Content area (inset by border width)
        var content  = AtlasUIFactory.CreateStretchRect("Content", root,
            Vector2.zero, Vector2.one, new Vector2(5, 5), new Vector2(-5, -5));

        // Wire up glow animation
        var hp = root.gameObject.AddComponent<HolographicPanel>();
        hp.Initialize(glowImg);

        return content;
    }
}
