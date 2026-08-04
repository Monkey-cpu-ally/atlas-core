using System.Collections;
using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// Dialogue Panel — right-column chat/response stream for the Atlas Face environment
/// (x: 0.80–1.00, y: 0.12–0.90).
///
/// Displays:
///   • Scrollable message history with speaker labels
///   • "ATLAS LISTENING" indicator with animated blink cursor
///   • Input stub area showing "AWAITING INPUT . . ."
///
/// Usage: DialoguePanel.Create(environmentRectTransform)
/// </summary>
[RequireComponent(typeof(RectTransform))]
public class DialoguePanel : MonoBehaviour
{
    // ── References ────────────────────────────────────────────────────────────

    private RectTransform messageContainer;
    private Text          lblIndicator;
    private Image         cursorBar;
    private Coroutine     cursorRoutine;

    // Pre-seeded opening lines so the panel looks populated from the first frame.
    private static readonly string[] SeedSpeakers = { "ATLAS", "ATLAS" };
    private static readonly string[] SeedTexts    =
    {
        "Neural core online. All systems nominal.",
        "Standing by for your directive.",
    };

    // ── Factory ───────────────────────────────────────────────────────────────

    /// <summary>
    /// Builds the dialogue panel as a child of <paramref name="envRoot"/>,
    /// anchored to the right column of the environment's rect.
    /// </summary>
    public static DialoguePanel Create(Transform envRoot)
    {
        var go = new GameObject("DialoguePanel");
        go.transform.SetParent(envRoot, false);

        var rt       = go.AddComponent<RectTransform>();
        rt.anchorMin = new Vector2(0.80f, 0.12f);
        rt.anchorMax = new Vector2(1.00f, 0.90f);
        rt.offsetMin = new Vector2(4, 4);
        rt.offsetMax = new Vector2(-12, -4);

        var panel = go.AddComponent<DialoguePanel>();
        panel.BuildUI(rt);
        return panel;
    }

    // ── UI Construction ───────────────────────────────────────────────────────

    private void BuildUI(RectTransform root)
    {
        var content = HolographicPanel.BuildPanelLayers(root);

        // ── Header bar (93–100%) ──────────────────────────────────────────────
        var headerRT = AtlasUIFactory.CreateStretchRect("Header", content,
            new Vector2(0f, 0.94f), Vector2.one,
            new Vector2(6, 0), new Vector2(-6, 0));
        var headerLbl  = headerRT.gameObject.AddComponent<Text>();
        headerLbl.font      = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        headerLbl.text      = "DIALOGUE STREAM";
        headerLbl.fontSize  = 9;
        headerLbl.color     = HolographicPanel.TextAccent;
        headerLbl.alignment = TextAnchor.MiddleCenter;

        AtlasUIFactory.CreateHorizontalDivider("Divider_Top", content,
            yAnchor: 0.93f, xPadding: 4f, HolographicPanel.BorderCyan);

        // ── Message history area (18–93%) ─────────────────────────────────────
        var historyRT = AtlasUIFactory.CreateStretchRect("MessageHistory", content,
            new Vector2(0f, 0.18f), new Vector2(1f, 0.93f),
            new Vector2(6, 4), new Vector2(-6, -4));
        var historyBG   = historyRT.gameObject.AddComponent<Image>();
        historyBG.color = new Color(0f, 0.03f, 0.10f, 0.40f);

        var vLayout              = historyRT.gameObject.AddComponent<VerticalLayoutGroup>();
        vLayout.childAlignment   = TextAnchor.LowerLeft;
        vLayout.spacing          = 4f;
        vLayout.childForceExpandWidth  = true;
        vLayout.childForceExpandHeight = false;
        vLayout.padding              = new RectOffset(6, 6, 4, 4);

        messageContainer = historyRT;

        // Seed initial messages
        for (int i = 0; i < SeedSpeakers.Length; i++)
            AppendMessageInternal(SeedSpeakers[i], SeedTexts[i], HolographicPanel.TextPrimary);

        AtlasUIFactory.CreateHorizontalDivider("Divider_Bottom", content,
            yAnchor: 0.17f, xPadding: 4f, HolographicPanel.BorderCyan);

        // ── Listening indicator row (10–17%) ──────────────────────────────────
        var indicatorRT = AtlasUIFactory.CreateStretchRect("IndicatorRow", content,
            new Vector2(0f, 0.10f), new Vector2(1f, 0.17f),
            new Vector2(8, 0), new Vector2(-8, 0));

        // Blinking cursor square
        var cursorRT    = AtlasUIFactory.CreateStretchRect("Cursor", indicatorRT,
            new Vector2(0f, 0.20f), new Vector2(0.09f, 0.80f),
            Vector2.zero, Vector2.zero);
        cursorBar       = cursorRT.gameObject.AddComponent<Image>();
        cursorBar.color = HolographicPanel.BorderCyan;

        var indicatorLabel = AtlasUIFactory.CreateStretchRect("Lbl_Indicator", indicatorRT,
            new Vector2(0.12f, 0f), Vector2.one,
            Vector2.zero, Vector2.zero);
        lblIndicator           = indicatorLabel.gameObject.AddComponent<Text>();
        lblIndicator.font      = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        lblIndicator.text      = "ATLAS LISTENING";
        lblIndicator.fontSize  = 8;
        lblIndicator.color     = HolographicPanel.TextMuted;
        lblIndicator.alignment = TextAnchor.MiddleLeft;

        // ── Input stub (1–9%) ─────────────────────────────────────────────────
        var inputRT    = AtlasUIFactory.CreateStretchRect("InputArea", content,
            new Vector2(0f, 0.01f), new Vector2(1f, 0.09f),
            new Vector2(6, 2), new Vector2(-6, -2));
        var inputBG    = inputRT.gameObject.AddComponent<Image>();
        inputBG.color  = new Color(0f, 0.08f, 0.18f, 0.75f);

        var inputLabelRT = AtlasUIFactory.CreateStretchRect("Lbl_Input", inputRT,
            Vector2.zero, Vector2.one,
            new Vector2(8, 0), new Vector2(-8, 0));
        var inputLbl  = inputLabelRT.gameObject.AddComponent<Text>();
        inputLbl.font      = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        inputLbl.text      = "AWAITING INPUT . . .";
        inputLbl.fontSize  = 8;
        inputLbl.color     = new Color(0.30f, 0.55f, 0.70f, 1f);
        inputLbl.alignment = TextAnchor.MiddleLeft;

        cursorRoutine = StartCoroutine(CursorBlinkRoutine());
    }

    // ── Message helpers ───────────────────────────────────────────────────────

    private void AppendMessageInternal(string speaker, string text, Color textColor)
    {
        if (messageContainer == null) return;

        // Entry root
        var entryGO  = new GameObject("Msg");
        entryGO.transform.SetParent(messageContainer, false);
        var entryRT  = entryGO.AddComponent<RectTransform>();
        entryRT.sizeDelta = Vector2.zero;

        var entryVL              = entryGO.AddComponent<VerticalLayoutGroup>();
        entryVL.childAlignment   = TextAnchor.UpperLeft;
        entryVL.spacing          = 1f;
        entryVL.childForceExpandWidth  = true;
        entryVL.childForceExpandHeight = false;
        entryVL.padding = new RectOffset(0, 0, 0, 3);

        var entrySF          = entryGO.AddComponent<ContentSizeFitter>();
        entrySF.verticalFit  = ContentSizeFitter.FitMode.PreferredSize;

        var entryLE              = entryGO.AddComponent<LayoutElement>();
        entryLE.flexibleWidth    = 1;

        // Speaker label
        var speakerGO    = new GameObject("Speaker");
        speakerGO.transform.SetParent(entryGO.transform, false);
        var speakerRT    = speakerGO.AddComponent<RectTransform>();
        speakerRT.sizeDelta = Vector2.zero;

        var speakerLbl         = speakerGO.AddComponent<Text>();
        speakerLbl.font        = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        speakerLbl.text        = speaker;
        speakerLbl.fontSize    = 7;
        speakerLbl.color       = HolographicPanel.TextMuted;
        speakerLbl.alignment   = TextAnchor.UpperLeft;

        var speakerLE          = speakerGO.AddComponent<LayoutElement>();
        speakerLE.preferredHeight = 12;
        speakerLE.flexibleWidth   = 1;

        // Body text
        var textGO     = new GameObject("Body");
        textGO.transform.SetParent(entryGO.transform, false);
        var textRT     = textGO.AddComponent<RectTransform>();
        textRT.sizeDelta = Vector2.zero;

        var textLbl                   = textGO.AddComponent<Text>();
        textLbl.font                  = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        textLbl.text                  = text;
        textLbl.fontSize              = 8;
        textLbl.color                 = textColor;
        textLbl.alignment             = TextAnchor.UpperLeft;
        textLbl.horizontalOverflow    = HorizontalWrapMode.Wrap;
        textLbl.verticalOverflow      = VerticalWrapMode.Overflow;

        var textLE              = textGO.AddComponent<LayoutElement>();
        textLE.preferredHeight  = 26;
        textLE.flexibleWidth    = 1;
    }

    // ── Public API ────────────────────────────────────────────────────────────

    /// <summary>Appends a new message entry to the dialogue stream.</summary>
    public void AppendMessage(string speaker, string text, Color textColor)
    {
        AppendMessageInternal(speaker, text, textColor);
    }

    /// <summary>Updates the listening indicator line.</summary>
    public void SetIndicator(string text)
    {
        if (lblIndicator != null) lblIndicator.text = text;
    }

    // ── Cursor blink ──────────────────────────────────────────────────────────

    private IEnumerator CursorBlinkRoutine()
    {
        while (true)
        {
            yield return new WaitForSeconds(0.55f);
            if (cursorBar != null)
            {
                Color c = cursorBar.color;
                c.a     = c.a > 0.5f ? 0.06f : 1f;
                cursorBar.color = c;
            }
        }
    }
}
