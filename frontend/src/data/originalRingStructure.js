// Original HUD Ring Structure
// Based on user's reference screenshot

export const ORIGINAL_RING_STRUCTURE = {
  // Ring 1 - Outer Ring (8 items at compass points)
  ring1: [
    { id: 'subjects', label: 'SUBJECTS', position: 'top', angle: -90 },
    { id: 'lab', label: 'LAB', position: 'top-right', angle: -45 },
    { id: 'projects', label: 'PROJECTS', position: 'right', angle: 0 },
    { id: 'memory', label: 'MEMORY', position: 'bottom-right', angle: 45 },
    { id: 'customization', label: 'CUSTOMIZATION', position: 'bottom', angle: 90 },
    { id: 'systems', label: 'SYSTEMS', position: 'bottom-left', angle: 135 },
    { id: 'explore', label: 'EXPLORE MODE', position: 'left', angle: 180 },
    { id: 'archive', label: 'ARCHIVE', position: 'top-left', angle: -135 },
  ],
  
  // Ring 2 - Middle Ring (5 items)
  ring2: [
    { id: 'manual', label: 'MANUAL', position: 'top', angle: -90 },
    { id: 'minerva', label: 'MINERVA', position: 'right', angle: 0, type: 'ai' },
    { id: 'system_monitor', label: 'SYSTEM MONITOR', position: 'bottom', angle: 90 },
    { id: 'hermes', label: 'HERMES', position: 'bottom', angle: 90, type: 'ai' },
    { id: 'council', label: 'COUNCIL', position: 'left', angle: 180, type: 'ai' },
  ],
  
  // Ring 3 - Inner Ring (1 item - active AI)
  ring3: [
    { id: 'ajani', label: 'AJANI', position: 'center-top', angle: -90, type: 'ai' },
  ],
};

// AI Personas (from original)
export const AI_LIST = {
  ajani: { name: 'AJANI', color: '#DC143C', role: 'Builder / Strategist / Engineer' },
  minerva: { name: 'MINERVA', color: '#20B2AA', role: 'Guide / Teacher / Healer' },
  hermes: { name: 'HERMES', color: '#C0C0C0', role: 'Messenger / Protector / Validator' },
  council: { name: 'COUNCIL', color: '#9370DB', role: 'Trinity Counsel' },
};

// Compass positioning helper
export const getCompassPosition = (angle, radius, centerX = 50, centerY = 50) => {
  const rad = angle * (Math.PI / 180);
  return {
    x: centerX + radius * Math.cos(rad),
    y: centerY + radius * Math.sin(rad),
  };
};
