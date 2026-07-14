import React from "react";

const fallbackItems = [
  { id: "weather", category: "Weather", title: "Weather source not connected", why: "Connect a forecast provider to receive local conditions and severe-weather alerts.", persona: "minerva", urgency: "normal" },
  { id: "markets", category: "Markets", title: "Market source not connected", why: "Connect market data before ATLAS reports prices or movement.", persona: "ajani", urgency: "normal" },
  { id: "technology", category: "Technology", title: "Technology feed not connected", why: "Connect verified news and research sources for project-relevant developments.", persona: "hermes", urgency: "normal" },
];

export default function PulsePanel({ items, updatedAt }) {
  const visibleItems = items?.length ? items : fallbackItems;

  return (
    <section className="pulse-panel" aria-label="The Pulse">
      <header className="pulse-panel__header">
        <div>
          <p>The Pulse</p>
          <h2>What matters and why</h2>
        </div>
        <time>{updatedAt ? new Date(updatedAt).toLocaleTimeString() : "Awaiting live sources"}</time>
      </header>
      <div className="pulse-panel__grid">
        {visibleItems.slice(0, 6).map((item) => (
          <article className="pulse-card" data-persona={item.persona || "atlas"} key={item.id}>
            <div className="pulse-card__topline">
              <span>{item.category}</span>
              {item.urgency && item.urgency !== "normal" ? <b>{item.urgency}</b> : null}
            </div>
            <h3>{item.title}</h3>
            <p>{item.summary}</p>
            <footer>
              <strong>Why Frazier should care</strong>
              <span>{item.why}</span>
            </footer>
          </article>
        ))}
      </div>
    </section>
  );
}
