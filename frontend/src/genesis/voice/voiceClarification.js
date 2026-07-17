const EMPTY_CLARIFICATION = Object.freeze({ kind: null, options: [], originalCommand: null });
let pendingClarification = { ...EMPTY_CLARIFICATION };

function normalize(value) {
  return String(value || "")
    .toLowerCase()
    .replace(/[.,!?;:]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function optionTerms(option) {
  return [option?.id, option?.title, ...(option?.aliases || [])]
    .map(normalize)
    .filter(Boolean);
}

export function getPendingClarification() {
  return {
    ...pendingClarification,
    options: [...pendingClarification.options],
  };
}

export function clearPendingClarification() {
  pendingClarification = { ...EMPTY_CLARIFICATION };
}

export function requestProjectClarification(options, originalCommand = null) {
  pendingClarification = {
    kind: "project",
    options: [...options].slice(0, 3),
    originalCommand,
  };

  return {
    type: "clarification",
    clarificationKind: "project",
    options: pendingClarification.options,
    originalCommand,
    transcript: originalCommand?.transcript || "",
    contextual: true,
  };
}

export function resolvePendingClarification(transcript) {
  if (!pendingClarification.kind || !pendingClarification.options.length) return null;

  const text = normalize(transcript);
  if (!text) return null;

  if (["cancel", "never mind", "nevermind", "none", "neither"].includes(text)) {
    clearPendingClarification();
    return { type: "cancel", transcript: text, clarificationCancelled: true };
  }

  const ordinal = text.match(/\b(first|second|third|1|2|3)\b/)?.[1];
  const ordinalIndex = { first: 0, "1": 0, second: 1, "2": 1, third: 2, "3": 2 }[ordinal];
  const selectedByOrdinal = Number.isInteger(ordinalIndex)
    ? pendingClarification.options[ordinalIndex]
    : null;

  const selectedByName = pendingClarification.options.find((option) =>
    optionTerms(option).some((term) => text === term || text.includes(term)),
  );
  const selected = selectedByName || selectedByOrdinal;
  if (!selected?.id) return null;

  const originalCommand = pendingClarification.originalCommand;
  clearPendingClarification();

  return {
    ...(originalCommand || {}),
    type: originalCommand?.type === "conversation" ? "conversation" : "project",
    project: selected,
    projectId: selected.id,
    persona: originalCommand?.persona || selected.persona || null,
    transcript: text,
    contextual: true,
    resolvedFromClarification: true,
  };
}
