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
  // Middle ring — operating system shell
  Book, BookMarked, Database, Settings, Layout,
  // Outer ring — knowledge / exploration
  BookOpen, FlaskConical, FolderOpen, FileCode, Archive, Compass,
} from 'lucide-react';

import ajaniLogo from '../assets/logos/ajani-logo.jpg';
import minervaLogo from '../assets/logos/minerva-logo.jpg';
import hermesLogo from '../assets/logos/hermes-logo.jpg';
import councilLogo from '../assets/logos/atlas-council-logo.jpg';

// --- Inner Orbit (4 AIs at compass cardinals) ---
export const INNER_RING = {
  slotAngle: 90,
  items: [
    { angle: -90, id: 'ajani',   label: 'AJANI',   logo: ajaniLogo,   color: '#F03246', type: 'ai' },
    { angle:   0, id: 'minerva', label: 'MINERVA', logo: minervaLogo, color: '#28C8BE', type: 'ai' },
    { angle:  90, id: 'hermes',  label: 'HERMES',  logo: hermesLogo,  color: '#F4EFE4', type: 'ai' },
    { angle: 180, id: 'trinity', label: 'COUNCIL', logo: councilLogo, color: '#A878E6', type: 'ai' },
  ],
};

// --- Mid System Ring (5 items, evenly spaced at 72° intervals) ---
// Starts at the top (-90°) so MANUAL sits directly above the core, then
// rotates clockwise. Forms a clean pentagon around the inner orbit.
export const MIDDLE_RING = {
  slotAngle: 72,
  items: [
    { angle:  -90, id: 'manual',        label: 'MANUAL',        icon: Book,       type: 'section' },
    { angle:  -18, id: 'encyclopedia',  label: 'CYCLOPEDIA',    icon: BookMarked, type: 'section' },
    { angle:   54, id: 'memory',        label: 'MEMORY',        icon: Database,   type: 'section' },
    { angle:  126, id: 'systems',       label: 'SYSTEMS',       icon: Layout,     type: 'section' },
    { angle: -162, id: 'customization', label: 'CUSTOMIZATION', icon: Settings,   type: 'section' },
  ],
};

// --- Outer World Ring (6 items, evenly spaced at 60° intervals) ---
// Hexagonal layout — symmetric around the centre so no quadrant feels
// empty. Cardinals (top, right, bottom) plus three ordinals.
export const OUTER_RING = {
  slotAngle: 60,
  items: [
    { angle:  -90, id: 'subjects',   label: 'SUBJECTS',     icon: BookOpen,     type: 'section' },
    { angle:  -30, id: 'lab',        label: 'LAB',          icon: FlaskConical, type: 'section' },
    { angle:   30, id: 'projects',   label: 'PROJECTS',     icon: FolderOpen,   type: 'section' },
    { angle:   90, id: 'blueprints', label: 'BLUEPRINTS',   icon: FileCode,     type: 'section' },
    { angle:  150, id: 'archive',    label: 'ARCHIVE',      icon: Archive,      type: 'section' },
    { angle: -150, id: 'explore',    label: 'EXPLORE MODE', icon: Compass,      type: 'section' },
  ],
};
