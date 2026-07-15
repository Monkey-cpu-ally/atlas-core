import React, { useMemo, useState } from "react";
import { mergePulseItems, pulseSources } from "./pulse/pulseRegistry";
import "./pulse/pulse.css";

export default function PulsePanel({ items = [], updatedAt }) {
  const [filter, setFilter] = useState("all");
  const mergedItems = useMemo(() => mergePulseItems(items), [items]);
  const visibleItems = useMemo(
    () => mergedItems.filter((item) => filter === "all" || item.sourceId === filter),
    [filter, mergedItems],
  );
  const connectedCount = pulseSources.filter((source) => source.enabled).length;

  return (
    <section className="pulse-panel" aria-label="The Pulse">
      <header className="pulse-panel__header">
        <div>
          <p>The Pulse</p>
          <h2>What matters and why</h2>
          <span>{connectedCount} of {pulseSources.length} sources connected</span>
        </div>
        <time>{updatedAt ? new Date(updatedAt).toLocaleTimeString() : "Awaiting live sources"}</time>
      </header>

      <nav className="pulse-panel__filters" aria-label="Pulse categories">
        <button type="button" className={filter === "all" ? "is-active" : ""} onClick={() => setFilter("all")}>All</button>
        {pulseSources.map((source) => (
          <button
            type="button"
            key={source.id}
            className={filter === source.id ? "is-active" : ""}
            data-connected={source.enabled}
            onClick={() => setFilter(source.id)}
          >
            {source.label}
          </button>
        ))}
      </nav>

      <div className="pulse-panel__grid">
        {visibleItems.slice(0, 12).map((item) => (
          <article
            className="pulse-card"
            data-persona={item.persona || "atlas"}
            data-status={item.status || "live"}
            key={item.id}
          >
            <div className="pulse-card__topline">
              <span>{item.category}</span>
              <div>
                {item.status ? <em>{item.status}</em> : null}
                {item.urgency && item.urgency !== "normal" ? <b>{item.urgency}</b> : null}
              </div>
            </div>
            <h3>{item.title}</h3>
            {item.summary ? <p>{item.summary}</p> : null}
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
