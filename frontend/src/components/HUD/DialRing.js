import React, { useCallback, useEffect, useRef, useState } from 'react';

/**
 * DialRing — a rotating radial ring of tiles.
 *
 * Tiles are positioned via polar coordinates (center, radius, angle).
 * The ring follows the pointer during a drag and snaps to the nearest slot
 * on release. When a new tile lands at the top (-90°) it fires onSelect.
 * Click-vs-drag is detected by tracking total angular movement during the
 * gesture; short taps fall through to the tile's native click handler.
 *
 * Implementation detail: pointer move/up are attached at the window level
 * (instead of using setPointerCapture on the ring container) so that the
 * native click event on tile buttons is not swallowed.
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

  // Drag state lives in a ref so handlers can read it without re-binding.
  const dragRef = useRef({ active: false, startAngle: 0, startRot: 0, total: 0 });

  // Rotate ring so a given item lands at top when selectedId changes externally.
  useEffect(() => {
    if (!selectedId) return;
    const item = items.find(it => it.id === selectedId);
    if (!item) return;
    const target = -90 - item.angle;
    setRotation(prev => {
      const diff = ((target - prev + 540) % 360) - 180;
      return prev + diff;
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedId]);

  const pointerAngle = useCallback((clientX, clientY) => {
    const rect = containerRef.current.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;
    return Math.atan2(clientY - cy, clientX - cx) * (180 / Math.PI);
  }, []);

  // Window-level listeners attached on pointerdown and torn down on pointerup.
  useEffect(() => {
    const onMove = (e) => {
      const st = dragRef.current;
      if (!st.active) return;
      const a = pointerAngle(e.clientX, e.clientY);
      let delta = a - st.startAngle;
      delta = ((delta + 540) % 360) - 180;
      st.total = Math.max(st.total, Math.abs(delta));
      if (st.total > 4) setIsDragging(true);
      setRotation(st.startRot + delta);
    };

    const onUp = () => {
      const st = dragRef.current;
      if (!st.active) return;
      const dragged = st.total > 4;
      st.active = false;
      window.removeEventListener('pointermove', onMove);
      window.removeEventListener('pointerup', onUp);

      if (dragged) {
        setRotation(prev => {
          const snapped = Math.round(prev / slotAngle) * slotAngle;
          // Find whichever item is now nearest to top (-90°).
          let best = null;
          let bestDist = Infinity;
          for (const it of items) {
            const eff = it.angle + snapped;
            const d = Math.abs(((eff + 90 + 540) % 360) - 180);
            if (d < bestDist) { bestDist = d; best = it; }
          }
          if (best && best.id !== selectedId && bestDist < slotAngle / 2 + 1) {
            setTimeout(() => onSelect && onSelect(best, 'snap'), 0);
          }
          return snapped;
        });
        // Keep drag flag briefly so the trailing click on a tile is ignored.
        setTimeout(() => setIsDragging(false), 80);
      } else {
        setIsDragging(false);
      }
    };

    // Expose to pointerdown handler via closure
    dragRef.current._onMove = onMove;
    dragRef.current._onUp = onUp;
    return () => {
      window.removeEventListener('pointermove', onMove);
      window.removeEventListener('pointerup', onUp);
    };
  }, [items, slotAngle, selectedId, onSelect, pointerAngle]);

  const onPointerDown = (e) => {
    if (!containerRef.current) return;
    // Only main button / touch / pen
    if (e.button !== undefined && e.button !== 0) return;
    const a = pointerAngle(e.clientX, e.clientY);
    dragRef.current.active = true;
    dragRef.current.startAngle = a;
    dragRef.current.startRot = rotation;
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
        {/* Thick invisible hit-zone stroke for drag-to-rotate. */}
        <circle cx="50" cy="50" r={radiusPct} className="drag-hit" />
        {/* Thin visible ring. */}
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
              {Icon && <Icon size={22} strokeWidth={1.5} />}
            </div>
            <div className="tile-label">{item.label}</div>
          </button>
        );
      })}
    </div>
  );
}
