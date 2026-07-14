import React from "react";

export default function AwarenessAlert({ alert, onDismiss }) {
  if (!alert) return null;
  const urgency = alert.urgency || "normal";

  return (
    <section className="awareness-alert" data-urgency={urgency} role={urgency === "critical" ? "alert" : "status"}>
      <div className="awareness-alert__marker" aria-hidden="true" />
      <div>
        <p>{alert.persona || "ATLAS"} noticed something</p>
        <h2>{alert.title || alert.message || "Awareness alert"}</h2>
        {alert.reason ? <span>{alert.reason}</span> : null}
        {alert.action ? <strong>{alert.action}</strong> : null}
      </div>
      <button type="button" onClick={onDismiss} aria-label="Dismiss awareness alert">×</button>
    </section>
  );
}
