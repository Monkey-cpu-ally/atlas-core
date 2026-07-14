import React, { useState } from "react";
import { getPortrait } from "./portraitRegistry";

function PortraitCard({ persona, active, state }) {
  const portrait = getPortrait(persona, state);
  const [failed, setFailed] = useState(false);
  if (!portrait) return null;

  return (
    <article
      className={`portrait-card ${active ? "is-active" : ""}`}
      data-persona={persona}
      data-state={state}
    >
      <div className="portrait-card__image">
        {!failed ? (
          <img
            src={portrait.src}
            alt={`${portrait.label} ${state}`}
            loading="eager"
            decoding="async"
            onError={() => setFailed(true)}
          />
        ) : (
          <div className="portrait-card__fallback" aria-label={`${portrait.label} portrait asset pending`}>
            <span>{portrait.label.slice(0, 1)}</span>
          </div>
        )}
        <div className="portrait-card__scan" aria-hidden="true" />
      </div>
      <div className="portrait-card__meta">
        <div>
          <strong>{portrait.label}</strong>
          <span>{portrait.role}</span>
        </div>
        <small>{state}</small>
      </div>
    </article>
  );
}

export default function PortraitController({ visiblePersonas = [], activePersona, state = "idle" }) {
  if (!visiblePersonas.length) return null;

  const council = visiblePersonas.length === 3;
  return (
    <aside
      className={`portrait-controller ${council ? "is-council" : "is-single"}`}
      aria-label="Active ATLAS AI presence"
    >
      {visiblePersonas.map((persona) => (
        <PortraitCard
          key={persona}
          persona={persona}
          state={state}
          active={persona === activePersona || activePersona === "council"}
        />
      ))}
    </aside>
  );
}
