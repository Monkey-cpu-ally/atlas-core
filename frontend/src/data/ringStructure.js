// Radial HUD layout — 4 visible orbits + core ring, with strict diameter
// ratios relative to the orb (per user spec):
//   Core Ring   ≈ 1.3× orb (decorative containment ring)
//   Inner Orbit ≈ 2.5× orb (AI personas — N/E/S/W)
//   Mid System  ≈ 4×   orb (operating-system shell)
//   Outer World ≈ 6×   orb (knowledge / exploration)
//
// Angles: -90° = top (12 o'clock), 0° = right, 90° = bottom, 180° = left.

import {
  // Inner ring (AIs)
  User, Brain, Zap, Users,
  // Middle ring — operating system shell
  Book, BookMarked, Database, Settings, Layout,
  // Outer ring — knowledge / exploration
  BookOpen, FlaskConical, FolderOpen, FileCode, Archive, Compass,
} from 'lucide-react';

// --- Inner Orbit (AI personas, 4 slots @ 90°, compass directions) ---
export const INNER_RING = {
  slotAngle: 90,
  items: [
    { angle: -90, id: 'ajani',   label: 'AJANI',   icon: User,  color: '#F03246', type: 'ai' },
    { angle:   0, id: 'minerva', label: 'MINERVA', icon: Brain, color: '#28C8BE', type: 'ai' },
    { angle:  90, id: 'hermes',  label: 'HERMES',  icon: Zap,   color: '#E0E0EA', type: 'ai' },
    { angle: 180, id: 'trinity', label: 'COUNCIL', icon: Users, color: '#A878E6', type: 'ai' },
  ],
};

// --- Mid System Ring (operating-system shell, 5 items on an 8-slot grid) ---
export const MIDDLE_RING = {
  slotAngle: 45,
  items: [
    { angle: -90, id: 'manual',        label: 'MANUAL',        icon: Book,       type: 'section' },
    { angle:   0, id: 'encyclopedia',  label: 'ENCYCLOPEDIA',  icon: BookMarked, type: 'section' },
    { angle:  45, id: 'memory',        label: 'MEMORY',        icon: Database,   type: 'section' },
    { angle:  90, id: 'systems',       label: 'SYSTEMS',       icon: Layout,     type: 'section' },
    { angle: 135, id: 'customization', label: 'CUSTOMIZATION', icon: Settings,   type: 'section' },
  ],
};

// --- Outer World Ring (knowledge / exploration, 6 items on an 8-slot grid) ---
export const OUTER_RING = {
  slotAngle: 45,
  items: [
    { angle: -90, id: 'subjects',   label: 'SUBJECTS',     icon: BookOpen,     type: 'section' },
    { angle:   0, id: 'lab',        label: 'LAB',          icon: FlaskConical, type: 'section' },
    { angle:  45, id: 'projects',   label: 'PROJECTS',     icon: FolderOpen,   type: 'section' },
    { angle:  90, id: 'blueprints', label: 'BLUEPRINTS',   icon: FileCode,     type: 'section' },
    { angle: 135, id: 'archive',    label: 'ARCHIVE',      icon: Archive,      type: 'section' },
    { angle: 180, id: 'explore',    label: 'EXPLORE MODE', icon: Compass,      type: 'section' },
  ],
};
