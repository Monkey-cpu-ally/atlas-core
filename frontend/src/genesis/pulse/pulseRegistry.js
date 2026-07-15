export const pulseSources = Object.freeze([
  { id: "weather", label: "Weather", persona: "minerva", enabled: false },
  { id: "disasters", label: "Natural Disasters", persona: "ajani", enabled: false },
  { id: "markets", label: "Markets", persona: "ajani", enabled: false },
  { id: "technology", label: "Technology", persona: "hermes", enabled: false },
  { id: "engineering", label: "Engineering", persona: "hermes", enabled: false },
  { id: "local-events", label: "Local Events", persona: "minerva", enabled: false },
  { id: "space", label: "Space", persona: "hermes", enabled: false },
  { id: "github", label: "GitHub", persona: "hermes", enabled: true },
]);

const disconnectedCopy = {
  weather: ["Weather source not connected", "Connect a forecast provider for local conditions and severe-weather alerts."],
  disasters: ["Disaster source not connected", "Connect verified emergency feeds before ATLAS reports earthquakes, storms, fires, or other hazards."],
  markets: ["Market source not connected", "Connect licensed market data before ATLAS reports prices, movements, or portfolio impact."],
  technology: ["Technology feed not connected", "Connect verified technology-news and primary research sources."],
  engineering: ["Engineering feed not connected", "Connect trusted engineering publications and standards sources."],
  "local-events": ["Local events source not connected", "Connect a location-aware events source for festivals, activities, closures, and community events."],
  space: ["Space feed not connected", "Connect launch, mission, and space-weather sources."],
};

export function buildPulseFallbacks() {
  return pulseSources
    .filter((source) => !source.enabled)
    .map((source) => {
      const [title, why] = disconnectedCopy[source.id] || [`${source.label} source not connected`, "Connect a verified source."];
      return {
        id: `source-${source.id}`,
        sourceId: source.id,
        category: source.label,
        title,
        summary: "ATLAS will not invent live information while this source is unavailable.",
        why,
        persona: source.persona,
        urgency: "normal",
        status: "disconnected",
      };
    });
}

export function mergePulseItems(items = []) {
  const realSourceIds = new Set(items.map((item) => item.sourceId).filter(Boolean));
  const fallbacks = buildPulseFallbacks().filter((item) => !realSourceIds.has(item.sourceId));
  return [...items, ...fallbacks];
}
