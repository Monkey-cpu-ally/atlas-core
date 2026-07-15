const GITHUB_EVENTS = new Set([
  "github.commit.created",
  "github.pull_request.opened",
  "github.pull_request.updated",
  "github.workflow.started",
  "github.workflow.completed",
  "github.workflow.failed",
  "github.issue.opened",
]);

export function githubPulseItemFromEnvelope(envelope) {
  if (!GITHUB_EVENTS.has(envelope?.event)) return null;
  const payload = envelope.payload || {};
  const failed = envelope.event === "github.workflow.failed" || payload.conclusion === "failure";
  const complete = envelope.event === "github.workflow.completed";
  const title = payload.title || payload.name || payload.message || envelope.event.replaceAll(".", " ");

  return {
    id: payload.id ? `github-${payload.id}` : `github-${envelope.event}-${envelope.timestamp || Date.now()}`,
    sourceId: "github",
    category: "GitHub",
    title,
    summary: payload.summary || payload.repository || "ATLAS received a verified GitHub project event.",
    why: failed
      ? "A failed build or check can block the current mission and should be reviewed."
      : complete
        ? "The latest automated checks completed and may change project readiness."
        : "This changes the current state of an ATLAS project.",
    persona: "hermes",
    urgency: failed ? "high" : "normal",
    status: failed ? "attention" : "connected",
    occurredAt: envelope.timestamp || new Date().toISOString(),
    url: payload.url || payload.display_url || null,
  };
}

export function upsertPulseItem(items = [], item, limit = 24) {
  if (!item) return items;
  const next = [item, ...items.filter((existing) => existing.id !== item.id)];
  return next.slice(0, limit);
}
