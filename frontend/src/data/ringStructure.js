// Radial HUD layout — visible controls only. Knowledge, memory, and project
// banks remain backend services and are never exposed as standalone HUD banks.
//
// Angles: -90° = top (12 o'clock), 0° = right, 90° = bottom, 180° = left.
// Positive = clockwise.

import {
  // Middle ring — operating system shell
  Book, BookMarked, Settings, Layout,
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

// --- Mid System Ring ---
// Memory and knowledge banks intentionally do not appear here. Their services
// support every workspace behind the scenes.
export const MIDDLE_RING = {
  slotAngle: 90,
  items: [
    { angle: -90, id: 'manual',        label: 'MANUAL',        icon: Book,       type: 'section' },
    { angle:   0, id: 'encyclopedia',  label: 'CYCLOPEDIA',    icon: BookMarked, type: 'section' },
    { angle:  90, id: 'systems',       label: 'SYSTEMS',       icon: Layout,     type: 'section' },
    { angle: 180, id: 'customization', label: 'CUSTOMIZATION', icon: Settings,   type: 'section' },
  ],
};

// --- Outer World Ring (6 items, evenly spaced at 60° intervals) ---
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
