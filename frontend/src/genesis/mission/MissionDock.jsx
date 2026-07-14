import React from "react";
import "./mission.css";

export default function MissionDock({ mission, onOpen }) {
  if (!mission) return null;

  return (
    <button className="mission-dock" type="button" onClick={() => onOpen?.(mission.id)}>
      <div className="mission-dock__topline">
        <span>Current Mission</span>
        <b>{mission.progress}%</b>
      </div>
      <strong>{mission.title}</strong>
      <div className="mission-dock__progress" aria-label={`${mission.progress}% complete`}>
        <span style={{ width: `${mission.progress}%` }} />
      </div>
      <small>{mission.nextStep}</small>
    </button>
  );
}
