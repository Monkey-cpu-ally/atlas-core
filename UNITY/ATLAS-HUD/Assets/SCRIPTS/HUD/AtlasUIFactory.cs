using System;
using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// Static utility that creates common UI building blocks for the Atlas HUD.
/// All methods return the primary component on the newly-created GameObject so
/// callers can configure colours, callbacks, etc.
/// </summary>
public static class AtlasUIFactory
{
    // ── Stretched panels ──────────────────────────────────────────────────────

    /// <summary>Full-stretch RectTransform under <paramref name="parent"/>.</summary>
    public static RectTransform CreateStretchRect(string name, Transform parent,
        Vector2 anchorMin, Vector2 anchorMax,
        Vector2 offsetMin, Vector2 offsetMax)
    {
        var go = new GameObject(name);
        go.transform.SetParent(parent, false);
        var rt        = go.AddComponent<RectTransform>();
        rt.anchorMin  = anchorMin;
        rt.anchorMax  = anchorMax;
        rt.offsetMin  = offsetMin;
        rt.offsetMax  = offsetMax;
        return rt;
    }

    /// <summary>Full-screen stretch under <paramref name="parent"/> with zero offset.</summary>
    public static RectTransform CreateFullStretch(string name, Transform parent)
        => CreateStretchRect(name, parent, Vector2.zero, Vector2.one, Vector2.zero, Vector2.zero);

    // ── Point-anchored elements ───────────────────────────────────────────────

    /// <summary>
    /// Creates a point-anchored RectTransform (anchorMin == anchorMax).
    /// </summary>
    public static RectTransform CreateElement(string name, Transform parent,
        Vector2 anchor, Vector2 pivot, Vector2 position, Vector2 size)
    {
        var go = new GameObject(name);
        go.transform.SetParent(parent, false);
        var rt               = go.AddComponent<RectTransform>();
        rt.anchorMin         = anchor;
        rt.anchorMax         = anchor;
        rt.pivot             = pivot;
        rt.anchoredPosition  = position;
        rt.sizeDelta         = size;
        return rt;
    }

    // ── Images ────────────────────────────────────────────────────────────────

    /// <summary>Adds an Image component with the given colour.</summary>
    public static Image AddImage(RectTransform rt, Color color)
    {
        var img   = rt.gameObject.AddComponent<Image>();
        img.color = color;
        return img;
    }

    /// <summary>Convenience: create a full-stretch coloured background image.</summary>
    public static Image CreateBackground(string name, Transform parent, Color color)
    {
        var rt = CreateFullStretch(name, parent);
        return AddImage(rt, color);
    }

    // ── Thin border strips ────────────────────────────────────────────────────

    /// <summary>Creates a 2-pixel-thick border strip along one edge.</summary>
    public static Image CreateBorderStrip(string name, Transform parent,
        bool horizontal, bool isTopOrLeft, Color color)
    {
        var go = new GameObject(name);
        go.transform.SetParent(parent, false);
        var rt = go.AddComponent<RectTransform>();

        if (horizontal)
        {
            rt.anchorMin = new Vector2(0, isTopOrLeft ? 1f : 0f);
            rt.anchorMax = new Vector2(1, isTopOrLeft ? 1f : 0f);
            rt.offsetMin = new Vector2(0, isTopOrLeft ? -2 :  0);
            rt.offsetMax = new Vector2(0, isTopOrLeft ?  0 :  2);
        }
        else
        {
            rt.anchorMin = new Vector2(isTopOrLeft ? 0f : 1f, 0);
            rt.anchorMax = new Vector2(isTopOrLeft ? 0f : 1f, 1);
            rt.offsetMin = new Vector2(isTopOrLeft ? 0 : -2, 0);
            rt.offsetMax = new Vector2(isTopOrLeft ? 2 :  0, 0);
        }

        var img   = go.AddComponent<Image>();
        img.color = color;
        return img;
    }

    // ── Text labels ───────────────────────────────────────────────────────────

    /// <summary>Creates a legacy Text label at a point-anchored position.</summary>
    public static Text CreateLabel(string name, Transform parent,
        string text, Vector2 anchor, Vector2 pivot,
        Vector2 position, Vector2 size,
        int fontSize, Color color, TextAnchor alignment = TextAnchor.MiddleLeft)
    {
        var rt = CreateElement(name, parent, anchor, pivot, position, size);
        var lbl           = rt.gameObject.AddComponent<Text>();
        lbl.text          = text;
        lbl.fontSize      = fontSize;
        lbl.color         = color;
        lbl.alignment     = alignment;
        lbl.resizeTextForBestFit = false;
        return lbl;
    }

    // ── Buttons ───────────────────────────────────────────────────────────────

    /// <summary>
    /// Creates a holographic-style button with a coloured background and label.
    /// </summary>
    public static Button CreateButton(string name, Transform parent,
        Vector2 anchor, Vector2 pivot, Vector2 position, Vector2 size,
        string label, int fontSize, Color bgColor, Color textColor,
        Action onClick)
    {
        var rt = CreateElement(name, parent, anchor, pivot, position, size);
        var img   = rt.gameObject.AddComponent<Image>();
        img.color = bgColor;

        var btn = rt.gameObject.AddComponent<Button>();
        if (onClick != null)
            btn.onClick.AddListener(() => onClick());

        // Label child
        var lblRT = CreateElement("Label", rt, new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f),
            Vector2.zero, size - new Vector2(16, 0));
        var lbl       = lblRT.gameObject.AddComponent<Text>();
        lbl.text      = label;
        lbl.fontSize  = fontSize;
        lbl.color     = textColor;
        lbl.alignment = TextAnchor.MiddleCenter;

        return btn;
    }

    // ── Divider lines ─────────────────────────────────────────────────────────

    /// <summary>Horizontal 1-pixel divider at a fractional vertical position.</summary>
    public static Image CreateHorizontalDivider(string name, Transform parent,
        float yAnchor, float xPadding, Color color)
    {
        var go = new GameObject(name);
        go.transform.SetParent(parent, false);
        var rt       = go.AddComponent<RectTransform>();
        rt.anchorMin = new Vector2(0, yAnchor);
        rt.anchorMax = new Vector2(1, yAnchor);
        rt.offsetMin = new Vector2(xPadding,  -1);
        rt.offsetMax = new Vector2(-xPadding,  1);
        var img   = go.AddComponent<Image>();
        img.color = color;
        return img;
    }
}
