import React from "react";

const labels = {
  ajani: "Ajani",
  minerva: "Minerva",
  hermes: "Hermes",
};

export default function PortraitController({ visiblePersonas = [], activePersona, state = "idle" }) {
  if (!visiblePersonas.length) return null;

  return (
    <aside
      className={`portrait-controller ${visiblePersonas.length === 3 ? "is-council" : "is-single"}`}
      aria-label="Active ATLAS AI presence"
    >
      {visiblePersonas.map((persona) => (
        <article
          className={`portrait-card ${persona === activePersona || activePersona === "council" ? "is-active" : ""}`}
          data-persona={persona}
          key={persona}
        >
          <div className="portrait-card__image" aria-hidden="true">
            <span>{labels[persona]?.slice(0, 1)}</span>
          </div>
          <div className="portrait-card__meta">
            <strong>{labels[persona]}</strong>
            <small>{state}</small>
          </div>
        </article>
      ))}
    </aside>
  );
}
