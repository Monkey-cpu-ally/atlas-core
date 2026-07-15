/* eslint-disable */
import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  Atom,
  Bot,
  BriefcaseBusiness,
  Building2,
  Cpu,
  FlaskConical,
  Gauge,
  Hammer,
  HeartPulse,
  Landmark,
  Leaf,
  Network,
  Orbit,
  Scale,
  ShieldCheck,
  Sparkles,
  Target,
  Users,
  Wrench,
} from 'lucide-react';
import './AIFocusRing.css';

const AI_FOCUS_BRANCHES = {
  ajani: [
    { id: 'strategy', label: 'STRATEGY', icon: Target },
    { id: 'operations', label: 'OPERATIONS', icon: Gauge },
    { id: 'business', label: 'BUSINESS', icon: BriefcaseBusiness },
    { id: 'economics', label: 'ECONOMICS', icon: Landmark },
    { id: 'risk', label: 'RISK', icon: ShieldCheck },
    { id: 'leadership', label: 'LEADERSHIP', icon: Users },
  ],
  minerva: [
    { id: 'biology', label: 'BIOLOGY', icon: Leaf },
    { id: 'chemistry', label: 'CHEMISTRY', icon: FlaskConical },
    { id: 'physics', label: 'PHYSICS', icon: Atom },
    { id: 'medicine', label: 'MEDICINE', icon: HeartPulse },
    { id: 'environment', label: 'NATURE', icon: Orbit },
    { id: 'research', label: 'RESEARCH', icon: Sparkles },
  ],
  hermes: [
    { id: 'engineering', label: 'ENGINEERING', icon: Wrench },
    { id: 'robotics', label: 'ROBOTICS', icon: Bot },
    { id: 'software', label: 'SOFTWARE', icon: Cpu },
    { id: 'manufacturing', label: 'MANUFACTURING', icon: Hammer },
    { id: 'architecture', label: 'ARCHITECTURE', icon: Building2 },
    { id: 'systems', label: 'SYSTEMS', icon: Network },
  ],
  trinity: [
    { id: 'council-review', label: 'REVIEW', icon: Scale },
    { id: 'council-synthesis', label: 'SYNTHESIS', icon: Network },
    { id: 'council-plan', label: 'PLAN', icon: Target },
    { id: 'council-build', label: 'BUILD', icon: Hammer },
    { id: 'council-validate', label: 'VALIDATE', icon: ShieldCheck },
    { id: 'council-decide', label: 'DECIDE', icon: Sparkles },
  ],
};

const FOCUS_EVENT = 'atlas-ai-focus-mode';
const BRANCH_EVENT = 'atlas-ai-focus-branch';

/**
 * DialRing — drag-rotate ring with snap-to-tile.
 *
 * Default mode preserves the original three-ring HUD. Selecting an AI from the
 * inner ring enters Focus Mode: the other rings fade away and the inner ring
 * expands into one large branch navigator inspired by the approved reference.
 * Back/Escape restores the three-ring HUD. Hidden banks remain backstage.
 */
export default function DialRing({
  items,
  slotAngle = 90,
  radiusPct,
  selectedId,
  onSelect,
  ringTestId = 'ring',
  activeAI,
}) {
  const containerRef = useRef(null);
  const [rotation, setRotation] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [focusAI, setFocusAI] = useState(null);
  const [focusBranch, setFocusBranch] = useState(null);
  const rotationRef = useRef(0);
  useEffect(() => { rotationRef.current = rotation; }, [rotation]);

  const isInnerRing = ringTestId === 'ring-inner';
  const isFocusRing = isInnerRing && !!focusAI;
  const isSuppressedRing = !isInnerRing && !!focusAI;

  useEffect(() => {
    const handleFocus = (event) => {
      const nextAI = event.detail?.ai || null;
      setFocusAI(nextAI);
      setFocusBranch(null);
      setRotation(0);
    };
    const handleKey = (event) => {
      if (event.key === 'Escape') {
        window.dispatchEvent(new CustomEvent(FOCUS_EVENT, { detail: { ai: null } }));
      }
    };
    window.addEventListener(FOCUS_EVENT, handleFocus);
    window.addEventListener('keydown', handleKey);
    return () => {
      window.removeEventListener(FOCUS_EVENT, handleFocus);
      window.removeEventListener('keydown', handleKey);
    };
  }, []);

  const displayItems = isFocusRing
    ? (AI_FOCUS_BRANCHES[focusAI] || []).map((item, index, all) => ({
        ...item,
        angle: -90 + index * (360 / all.length),
        type: 'focus-branch',
      }))
    : items;
  const displaySlotAngle = isFocusRing && displayItems.length
    ? 360 / displayItems.length
    : slotAngle;
  const displayRadius = isFocusRing ? 45 : radiusPct;

  const dragRef = useRef({ active: false, startAngle: 0, startRot: 0, total: 0 });

  useEffect(() => {
    if (isDragging || !selectedId || isFocusRing) return;
    const it = displayItems.find((i) => i.id === selectedId);
    if (!it) return;
    let target = -90 - it.angle;
    const cur = rotationRef.current;
    while (target - cur > 180) target -= 360;
    while (cur - target > 180) target += 360;
    setRotation(target);
  }, [selectedId, displayItems, isDragging, isFocusRing]);

  const pointerAngle = useCallback((clientX, clientY) => {
    const rect = containerRef.current.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;
    return Math.atan2(clientY - cy, clientX - cx) * (180 / Math.PI);
  }, []);

  useEffect(() => {
    const onMove = (e) => {
      const st = dragRef.current;
      if (!st.active) return;
      const a = pointerAngle(e.clientX, e.clientY);
      let delta = a - st.startAngle;
      delta = ((delta + 540) % 360) - 180;
      st.total = Math.max(st.total, Math.abs(delta));
      if (st.total > 3) setIsDragging(true);
      setRotation(st.startRot + delta);
    };

    const onUp = () => {
      const st = dragRef.current;
      if (!st.active) return;
      const dragged = st.total > 3;
      const releaseRotation = rotationRef.current;
      st.active = false;
      window.removeEventListener('pointermove', onMove);
      window.removeEventListener('pointerup', onUp);

      if (dragged) {
        let best = null;
        let bestDist = Infinity;
        for (const it of displayItems) {
          const eff = it.angle + releaseRotation;
          const d = Math.abs(((eff + 90 + 540) % 360) - 180);
          if (d < bestDist) { bestDist = d; best = it; }
        }
        if (best) {
          let target = -90 - best.angle;
          while (target - releaseRotation > 180) target -= 360;
          while (releaseRotation - target > 180) target += 360;
          setRotation(target);
          setTimeout(() => handleSelection(best, 'drag-release'), 0);
        }
        setTimeout(() => setIsDragging(false), 380);
      } else {
        setIsDragging(false);
      }
    };

    dragRef.current._onMove = onMove;
    dragRef.current._onUp = onUp;
    return () => {
      window.removeEventListener('pointermove', onMove);
      window.removeEventListener('pointerup', onUp);
    };
  }, [displayItems, displaySlotAngle, selectedId, onSelect, pointerAngle, isFocusRing]);

  const onPointerDown = (e) => {
    if (!containerRef.current || isSuppressedRing) return;
    if (e.button !== undefined && e.button !== 0) return;
    const a = pointerAngle(e.clientX, e.clientY);
    dragRef.current.active = true;
    dragRef.current.startAngle = a;
    dragRef.current.startRot = rotationRef.current;
    dragRef.current.total = 0;
    setIsDragging(false);
    window.addEventListener('pointermove', dragRef.current._onMove);
    window.addEventListener('pointerup', dragRef.current._onUp);
  };

  const handleSelection = (item, source = 'click') => {
    if (item.type === 'ai' && isInnerRing) {
      onSelect && onSelect(item, source);
      window.dispatchEvent(new CustomEvent(FOCUS_EVENT, { detail: { ai: item.id } }));
      return;
    }
    if (item.type === 'focus-branch') {
      setFocusBranch(item.id);
      window.dispatchEvent(new CustomEvent(BRANCH_EVENT, {
        detail: { ai: focusAI, branch: item.id },
      }));
      return;
    }
    onSelect && onSelect(item, source);
  };

  const handleTileClick = (item, e) => {
    if (isDragging) { e.preventDefault(); return; }
    handleSelection(item, 'click');
  };

  const exitFocus = () => {
    window.dispatchEvent(new CustomEvent(FOCUS_EVENT, { detail: { ai: null } }));
  };

  return (
    <div
      ref={containerRef}
      className={`dial-ring ${isDragging ? 'dragging' : ''} ${isFocusRing ? 'ai-focus-ring' : ''} ${isSuppressedRing ? 'focus-suppressed' : ''}`}
      data-testid={ringTestId}
      data-focus-ai={focusAI || undefined}
      onPointerDown={onPointerDown}
      style={{ touchAction: 'none' }}
    >
      <svg className="ring-track" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid meet">
        <circle cx="50" cy="50" r={displayRadius} className="drag-hit" />
        <circle cx="50" cy="50" r={displayRadius} className="ring-visible" />
      </svg>

      {isFocusRing && (
        <button
          type="button"
          className="ai-focus-back"
          onPointerDown={(e) => e.stopPropagation()}
          onClick={exitFocus}
          data-testid="ai-focus-back"
          aria-label="Return to the three-ring HUD"
        >
          BACK
        </button>
      )}

      {displayItems.map((item) => {
        const effective = item.angle + rotation;
        const rad = (effective * Math.PI) / 180;
        const x = 50 + displayRadius * Math.cos(rad);
        const y = 50 + displayRadius * Math.sin(rad);
        const diffFromTop = Math.abs(((effective + 90 + 540) % 360) - 180);
        const isTop = diffFromTop < displaySlotAngle / 2;
        const isActiveAI = item.type === 'ai' && activeAI === item.id;
        const isActiveBranch = item.type === 'focus-branch' && focusBranch === item.id;
        const Icon = item.icon;

        return (
          <button
            key={item.id}
            type="button"
            className={`dial-tile ${isTop ? 'is-top' : ''} ${isActiveAI ? 'active-ai' : ''} ${isActiveBranch ? 'active-branch' : ''} ${item.type === 'ai' ? 'ai-tile' : ''} ${item.type === 'focus-branch' ? 'focus-branch-tile' : ''}`}
            style={{
              left: `${x}%`,
              top: `${y}%`,
              '--tile-color': item.color || 'rgba(148, 163, 184, 0.9)',
            }}
            onPointerDown={(e) => e.stopPropagation()}
            onClick={(e) => handleTileClick(item, e)}
            data-testid={`${ringTestId}-${item.id}`}
          >
            <div className="tile-icon">
              {item.logo ? <img src={item.logo} alt="" className="tile-logo" /> : Icon && <Icon size={22} strokeWidth={1.5} />}
            </div>
            <div className="tile-label">{item.label}</div>
          </button>
        );
      })}
    </div>
  );
}
