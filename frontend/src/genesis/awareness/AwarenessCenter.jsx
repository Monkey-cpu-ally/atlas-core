import React from "react";
import "./awareness.css";

export default function AwarenessCenter({ alerts = [], onSelect, onDismiss, onClose }) {
  return (
    <section className="awareness-center" aria-label="Awareness Center">
      <header>
        <div>
          <p>Awareness</p>
          <h2>Things worth your attention</h2>
        </div>
        <button type="button" onClick={onClose}>Close</button>
      </header>

      <div className="awareness-center__list">
        {alerts.length ? alerts.map((alert) => (
          <article key={alert.id} data-urgency={alert.urgency || "normal"}>
            <button type="button" className="awareness-center__body" onClick={() => onSelect?.(alert)}>
              <span>{alert.persona || "atlas"}</span>
              <h3>{alert.title || alert.message}</h3>
              {alert.reason ? <p>{alert.reason}</p> : null}
              {alert.action ? <strong>{alert.action}</strong> : null}
            </button>
            <button type="button" className="awareness-center__dismiss" onClick={() => onDismiss?.(alert.id)} aria-label="Dismiss awareness item">×</button>
          </article>
        )) : (
          <div className="awareness-center__empty">
            <strong>Nothing urgent.</strong>
            <span>ATLAS will stay quiet until something deserves your attention.</span>
          </div>
        )}
      </div>
    </section>
  );
}
