using System.Collections;
using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// Animated background layer for Atlas HUD environments.
///
/// Attach via AtlasBackgroundFX.Attach(envRoot) from each environment's
/// BuildUI() method.  Two optional layers are created:
///
///   Layer A — DeepSpace shader fullscreen Image (star field, rays, vignette)
///             Replaces the plain flat-colour DeepBG Image.
///
///   Layer B — Diamond grid overlay (RawImage with tiling texture).
///             Very low alpha, slow UV scroll — gives the sense of a data-grid.
///
///   Layer C — Scanline overlay (RawImage, 1×4 repeating texture).
///             Applied over the entire environment content.
///
/// The component self-registers via a static factory; environments don't need
/// to hold a reference to it.
/// </summary>
[RequireComponent(typeof(RectTransform))]
public class AtlasBackgroundFX : MonoBehaviour
{
    // ── Layer control ─────────────────────────────────────────────────────────

    private RawImage gridLayer;
    private RawImage scanLayer;
    private float    gridScrollX;
    private float    gridScrollY;

    // Subtle grid scroll speeds (UV units per second)
    private const float GridScrollX = 0.008f;
    private const float GridScrollY = 0.004f;

    // ── Factory ───────────────────────────────────────────────────────────────

    /// <summary>
    /// Replaces the "DeepBG" child of <paramref name="envRoot"/> with the
    /// animated DeepSpace material, then adds diamond-grid and scanline overlays.
    ///
    /// Must be called AFTER HolographicPanel layers and environment content have
    /// been built so the z-order is correct (background sits at sibling index 0).
    /// </summary>
    public static AtlasBackgroundFX Attach(Transform envRoot, Color envTint)
    {
        if (envRoot == null) return null;

        // ── Layer A: Replace flat DeepBG with animated star field ─────────────
        Transform deepBG = envRoot.Find("DeepBG");
        if (deepBG != null)
        {
            var img = deepBG.GetComponent<Image>();
            if (img != null && AtlasVisualAssets.DeepSpaceMat != null)
            {
                img.material  = AtlasVisualAssets.DeepSpaceMat;
                img.color     = envTint;
                // Ensure it stays at the back
                deepBG.SetAsFirstSibling();
            }
        }

        // ── Create an FX host GameObject ──────────────────────────────────────
        var go  = new GameObject("BackgroundFX");
        go.transform.SetParent(envRoot, false);

        var rt       = go.AddComponent<RectTransform>();
        rt.anchorMin = Vector2.zero;
        rt.anchorMax = Vector2.one;
        rt.offsetMin = Vector2.zero;
        rt.offsetMax = Vector2.zero;

        // Position behind all environment content but in front of DeepBG
        go.transform.SetSiblingIndex(1);

        var fx = go.AddComponent<AtlasBackgroundFX>();

        // ── Layer B: Diamond grid overlay ─────────────────────────────────────
        if (AtlasTextureFactory.HexDiamondGrid != null)
        {
            var gridGO       = new GameObject("GridOverlay");
            gridGO.transform.SetParent(go.transform, false);

            var gridRT       = gridGO.AddComponent<RectTransform>();
            gridRT.anchorMin = Vector2.zero;
            gridRT.anchorMax = Vector2.one;
            gridRT.offsetMin = Vector2.zero;
            gridRT.offsetMax = Vector2.zero;

            fx.gridLayer          = gridGO.AddComponent<RawImage>();
            fx.gridLayer.texture  = AtlasTextureFactory.HexDiamondGrid;
            fx.gridLayer.color    = new Color(1f, 1f, 1f, 0.55f);
            fx.gridLayer.uvRect   = new Rect(0, 0, 3f, 3f);    // tile 3×3
            fx.gridLayer.raycastTarget = false;
        }

        // ── Layer C: Scanline overlay ─────────────────────────────────────────
        if (AtlasTextureFactory.ScanLineOverlay != null)
        {
            var scanGO       = new GameObject("ScanlineOverlay");
            scanGO.transform.SetParent(go.transform, false);

            var scanRT       = scanGO.AddComponent<RectTransform>();
            scanRT.anchorMin = Vector2.zero;
            scanRT.anchorMax = Vector2.one;
            scanRT.offsetMin = Vector2.zero;
            scanRT.offsetMax = Vector2.zero;

            fx.scanLayer              = scanGO.AddComponent<RawImage>();
            fx.scanLayer.texture      = AtlasTextureFactory.ScanLineOverlay;
            fx.scanLayer.color        = new Color(1f, 1f, 1f, 1f);
            // Tile to cover full screen — 1920/4 = 480 rows visible
            fx.scanLayer.uvRect       = new Rect(0, 0, 1f, 270f);
            fx.scanLayer.raycastTarget = false;
        }

        return fx;
    }

    // ── Update ────────────────────────────────────────────────────────────────

    private void Update()
    {
        if (gridLayer == null) return;

        gridScrollX += Time.deltaTime * GridScrollX;
        gridScrollY += Time.deltaTime * GridScrollY;

        Rect r = gridLayer.uvRect;
        r.x = gridScrollX;
        r.y = gridScrollY;
        gridLayer.uvRect = r;
    }
}
