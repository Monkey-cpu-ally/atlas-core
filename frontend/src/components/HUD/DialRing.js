/* eslint-disable */
import React, { useCallback, useEffect, useRef, useState } from 'react';

/**
 * DialRing — drag-rotate ring with snap-to-tile.
 *
 * The ring rotates as you drag with weighted resistance. On release it
 * snaps to the angle that places the nearest tile at the top (12 o'clock)
 * AND selects that tile. The rotation persists — the ring doesn't snap
 * back home. Selecting a different tile elsewhere also rotates the ring
 * to put it on top.
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
  const rotationRef = useRef(0);
  useEffect(() => { rotationRef.current = rotation; }, [rotation]);

  const dragRef = useRef({ active: false, startAngle: 0, startRot: 0, total: 0 });

  // When `selectedId` changes (e.g. from a click), rotate the ring so the
  // selected tile sits at the top. We do this off the drag-end path so
  // external selections (voice, etc.) also align.
  useEffect(() => {
    if (isDragging || !selectedId) return;
    const it = items.find((i) => i.id === selectedId);
    if (!it) return;
    // We want effective angle (it.angle + rotation) ≡ -90 (top).
    let target = -90 - it.angle;
    // Normalise to nearest multiple of 360 relative to current.
    const cur = rotationRef.current;
    while (target - cur > 180) target -= 360;
    while (cur - target > 180) target += 360;
    setRotation(target);
  }, [selectedId, items, isDragging]);

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

      // 1:1 rotation so dragging feels direct (not weighted/sluggish).
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
        // Find the tile closest to the top (12 o'clock = -90°).
        let best = null;
        let bestDist = Infinity;
        for (const it of items) {
          const eff = it.angle + releaseRotation;
          const d = Math.abs(((eff + 90 + 540) % 360) - 180);
          if (d < bestDist) { bestDist = d; best = it; }
        }
        if (best) {
          // Snap the ring so the chosen tile lands exactly at the top,
          // taking the shortest rotational path from the current angle.
          let target = -90 - best.angle;
          while (target - releaseRotation > 180) target -= 360;
          while (releaseRotation - target > 180) target += 360;
          setRotation(target);
          setTimeout(() => onSelect && onSelect(best, 'drag-release'), 0);
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
  }, [items, slotAngle, selectedId, onSelect, pointerAngle]);

  const onPointerDown = (e) => {
    if (!containerRef.current) return;
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

  const handleTileClick = (item, e) => {
    if (isDragging) { e.preventDefault(); return; }
    onSelect && onSelect(item, 'click');
  };

  return (
    <div
      ref={containerRef}
      className={`dial-ring ${isDragging ? 'dragging' : ''}`}
      data-testid={ringTestId}
      onPointerDown={onPointerDown}
      style={{ touchAction: 'none' }}
    >
      <svg className="ring-track" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid meet">
        <circle cx="50" cy="50" r={radiusPct} className="drag-hit" />
        <circle cx="50" cy="50" r={radiusPct} className="ring-visible" />
      </svg>

      {items.map((item) => {
        const effective = item.angle + rotation;
        const rad = (effective * Math.PI) / 180;
        const x = 50 + radiusPct * Math.cos(rad);
        const y = 50 + radiusPct * Math.sin(rad);

        const diffFromTop = Math.abs(((effective + 90 + 540) % 360) - 180);
        const isTop = diffFromTop < slotAngle / 2;

        const isActiveAI = item.type === 'ai' && activeAI === item.id;
        const Icon = item.icon;

        return (
          <button
            key={item.id}
            type="button"
            className={`dial-tile ${isTop ? 'is-top' : ''} ${isActiveAI ? 'active-ai' : ''} ${item.type === 'ai' ? 'ai-tile' : ''}`}
            style={{
              left: `${x}%`,
              top: `${y}%`,
              '--tile-color': item.color || 'rgba(148, 163, 184, 0.9)',
            }}
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
