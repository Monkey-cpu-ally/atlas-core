// Radial HUD layout — tile positions designed so that tiles from different
// orbits NEVER align radially, creating clean visual separation between
// rings (each ring has its own angular signature).
//
// Diameter ratios per spec:
//   Core orb     ≈ 1×   (anchor)
//   Core ring    ≈ 1.3× orb
//   Inner orbit  ≈ 2.5× orb (4 AI personas at compass cardinals)
//   Mid system   ≈ 4×   orb (offset 22.5° from outer to interleave)
//   Outer world  ≈ 6×   orb (cardinals + ordinals)
//
// Angles: -90° = top (12 o'clock), 0° = right, 90° = bottom, 180° = left.
// Positive = clockwise.

import {
  // Inner ring (AIs)
  User, Brain, Zap, Users,
  // Middle ring — operating system shell
  Book, BookMarked, Database, Settings, Layout,
  // Outer ring — knowledge / exploration
  BookOpen, FlaskConical, FolderOpen, FileCode, Archive, Compass,
} from 'lucide-react';

// --- Inner Orbit (4 AIs at compass cardinals) ---
export const INNER_RING = {
  slotAngle: 90,
  items: [
    { angle: -90, id: 'ajani',   label: 'AJANI',   icon: User,  color: '#F03246', type: 'ai' },
    { angle:   0, id: 'minerva', label: 'MINERVA', icon: Brain, color: '#28C8BE', type: 'ai' },
    { angle:  90, id: 'hermes',  label: 'HERMES',  icon: Zap,   color: '#E0E0EA', type: 'ai' },
    { angle: 180, id: 'trinity', label: 'COUNCIL', icon: Users, color: '#A878E6', type: 'ai' },
  ],
};

// --- Mid System Ring (5 items, offset 22.5° from outer to interleave) ---
// Tiles sit at NNE / ENE / SSE / SSW / WSW so they fall between outer ring spokes.
export const MIDDLE_RING = {
  slotAngle: 45,
  items: [
    { angle: -67.5, id: 'manual',        label: 'MANUAL',        icon: Book,       type: 'section' },
    { angle: -22.5, id: 'encyclopedia',  label: 'CYCLOPEDIA',    icon: BookMarked, type: 'section' },
    { angle:  22.5, id: 'memory',        label: 'MEMORY',        icon: Database,   type: 'section' },
    { angle:  67.5, id: 'systems',       label: 'SYSTEMS',       icon: Layout,     type: 'section' },
    { angle: 112.5, id: 'customization', label: 'CUSTOMIZATION', icon: Settings,   type: 'section' },
  ],
};

// --- Outer World Ring (6 items at cardinals + 2 ordinals) ---
export const OUTER_RING = {
  slotAngle: 45,
  items: [
    { angle: -90, id: 'subjects',   label: 'SUBJECTS',     icon: BookOpen,     type: 'section' },
    { angle: -45, id: 'lab',        label: 'LAB',          icon: FlaskConical, type: 'section' },
    { angle:   0, id: 'projects',   label: 'PROJECTS',     icon: FolderOpen,   type: 'section' },
    { angle:  90, id: 'blueprints', label: 'BLUEPRINTS',   icon: FileCode,     type: 'section' },
    { angle: 135, id: 'archive',    label: 'ARCHIVE',      icon: Archive,      type: 'section' },
    { angle: 180, id: 'explore',    label: 'EXPLORE MODE', icon: Compass,      type: 'section' },
  ],
};
