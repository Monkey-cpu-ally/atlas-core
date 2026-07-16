import { useEffect } from 'react';

/**
 * Keeps the clean HUD interaction model intact: the center core is the primary
 * conversation trigger. The existing AI face dock still owns persona
 * selection, and its double-click handler remains the single source of truth
 * for opening PersonaChatPanel.
 */
export default function CoreChatBridge() {
  useEffect(() => {
    const handleCoreClick = (event) => {
      const core = event.target?.closest?.('[data-testid="core-orb"]');
      if (!core) return;

      window.setTimeout(() => {
        const activeFace = document.querySelector('.ai-face-card.active');
        if (!activeFace) return;
        activeFace.dispatchEvent(new MouseEvent('dblclick', {
          bubbles: true,
          cancelable: true,
          view: window,
        }));
      }, 120);
    };

    document.addEventListener('click', handleCoreClick);
    return () => document.removeEventListener('click', handleCoreClick);
  }, []);

  return null;
}
