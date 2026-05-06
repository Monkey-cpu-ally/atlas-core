// Radial HUD layout — matches the Atlas Core reference screenshot.
// Angles are measured in degrees where -90 = top (12 o'clock),
// 0 = right (3 o'clock), 90 = bottom (6 o'clock), 180 = left (9 o'clock).
// Positive = clockwise.

import {
  BookOpen,       // Subjects
  FlaskConical,   // Lab
  FolderOpen,     // Projects
  Archive,        // Archive
  FileCode,       // Blueprints
  Book,           // Manual / Encyclopedia
  BookMarked,     // Encyclopedia
  Activity,       // System Monitor
  Compass,        // Explore Mode
  Database,       // Memory
  Settings,       // Customization
  Layout,         // Systems
  User,           // Ajani
  Brain,          // Minerva
  Zap,            // Hermes
  Users,          // Council
} from 'lucide-react';

// --- Ring 1 (innermost) — AI personas, 4 slots at 90° ---
export const INNER_RING = {
  slotAngle: 90,
  items: [
    { angle: -90, id: 'ajani',   label: 'AJANI',   icon: User,  color: '#E63946', type: 'ai' },
    { angle: 0,   id: 'minerva', label: 'MINERVA', icon: Brain, color: '#20B2AA', type: 'ai' },
    { angle: 90,  id: 'hermes',  label: 'HERMES',  icon: Zap,   color: '#E5E7EB', type: 'ai' },
    { angle: 180, id: 'trinity', label: 'COUNCIL', icon: Users, color: '#9370DB', type: 'ai' },
  ],
};

// --- Ring 2 (middle) — system / knowledge, 8-slot grid with 2 empty (NE, NW) ---
export const MIDDLE_RING = {
  slotAngle: 45,
  items: [
    { angle: -90, id: 'manual',         label: 'MANUAL',         icon: Book,       type: 'section' },
    { angle: 0,   id: 'encyclopedia',   label: 'ENCYCLOPEDIA',   icon: BookMarked, type: 'section' },
    { angle: 45,  id: 'memory',         label: 'MEMORY',         icon: Database,   type: 'section' },
    { angle: 90,  id: 'system_monitor', label: 'SYSTEM MONITOR', icon: Activity,   type: 'section' },
    { angle: 135, id: 'customization',  label: 'CUSTOMIZATION',  icon: Settings,   type: 'section' },
    { angle: 180, id: 'explore',        label: 'EXPLORE MODE',   icon: Compass,    type: 'section' },
  ],
};

// --- Ring 3 (outer) — knowledge / builder, 8-slot grid with 2 empty (NE, NW) ---
export const OUTER_RING = {
  slotAngle: 45,
  items: [
    { angle: -90, id: 'subjects',   label: 'SUBJECTS',   icon: BookOpen,     type: 'section' },
    { angle: 0,   id: 'lab',        label: 'LAB',        icon: FlaskConical, type: 'section' },
    { angle: 45,  id: 'projects',   label: 'PROJECTS',   icon: FolderOpen,   type: 'section' },
    { angle: 90,  id: 'blueprints', label: 'BLUEPRINTS', icon: FileCode,     type: 'section' },
    { angle: 135, id: 'systems',    label: 'SYSTEMS',    icon: Layout,       type: 'section' },
    { angle: 180, id: 'archive',    label: 'ARCHIVE',    icon: Archive,      type: 'section' },
  ],
};
