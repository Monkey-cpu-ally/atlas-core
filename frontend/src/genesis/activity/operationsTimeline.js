function parseTime(value) {
  if (!value) return 0;
  const timestamp = new Date(value).getTime();
  return Number.isFinite(timestamp) ? timestamp : 0;
}

function eventTime(item) {
  return item?.occurredAt || item?.timestamp || item?.updatedAt || null;
}

function normalizePulse(item) {
  return {
    id: `pulse-${item.id}`,
    kind: "pulse",
    persona: item.persona || "atlas",
    title: item.title || "Pulse update",
    detail: item.summary || item.why || item.category || "Verified external update received.",
    status: item.urgency === "high" || item.status === "attention" ? "attention" : "normal",
    occurredAt: eventTime(item),
    source: item.sourceId || item.category || "pulse",
    url: item.url || null,
  };
}

function normalizeAlert(alert) {
  return {
    id: `awareness-${alert.id}`,
    kind: "awareness",
    persona: alert.persona || "atlas",
    title: alert.title || alert.message || "Awareness alert",
    detail: alert.reason || alert.action || "ATLAS surfaced an item requiring review.",
    status: alert.urgency === "high" ? "attention" : "normal",
    occurredAt: eventTime(alert),
    source: "awareness",
    url: null,
  };
}

function normalizeProject(project) {
  return {
    id: `project-${project.id}`,
    kind: "project",
    persona: project.persona || "atlas",
    title: project.title,
    detail: project.updated || project.next || "Project record available.",
    status: ["risk", "blocked", "watch"].includes(String(project.health || "").toLowerCase())
      ? "attention"
      : "normal",
    occurredAt: project.updatedAt || null,
    source: "project registry",
    url: null,
  };
}

export function buildOperationsTimeline({
  mission,
  projects = [],
  pulseItems = [],
  awarenessItems = [],
  limit = 8,
} = {}) {
  const events = [
    ...pulseItems.filter((item) => item?.id).map(normalizePulse),
    ...awarenessItems.filter((item) => item?.id).map(normalizeAlert),
    ...projects.filter((project) => project?.id && project?.title).map(normalizeProject),
  ];

  if (mission?.id || mission?.title) {
    events.push({
      id: `mission-${mission.id || "active"}`,
      kind: "mission",
      persona: mission.owner || "atlas",
      title: mission.title || "Active mission",
      detail: mission.nextStep || "Mission is active.",
      status: "normal",
      occurredAt: mission.updatedAt || null,
      source: "mission registry",
      url: null,
    });
  }

  return events
    .sort((a, b) => {
      const timeDifference = parseTime(b.occurredAt) - parseTime(a.occurredAt);
      if (timeDifference !== 0) return timeDifference;
      const attentionDifference = Number(b.status === "attention") - Number(a.status === "attention");
      if (attentionDifference !== 0) return attentionDifference;
      return a.title.localeCompare(b.title);
    })
    .slice(0, Math.max(1, limit));
}

export function formatTimelineTime(value) {
  if (!value) return "Stored record";
  const date = new Date(value);
  if (!Number.isFinite(date.getTime())) return "Stored record";
  return date.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
}
