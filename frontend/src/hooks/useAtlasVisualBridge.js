import { useEffect, useMemo, useState } from "react";
import { connectVisualEventSocket } from "../services/visualEventBus";

function defaultVisualSocketUrl() {
  const configured = process.env.REACT_APP_ATLAS_VISUAL_WS;
  if (configured) return configured;

  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${protocol}//${window.location.host}/api/atlas/visual/ws`;
}

export default function useAtlasVisualBridge() {
  const url = useMemo(defaultVisualSocketUrl, []);
  const [status, setStatus] = useState("connecting");
  const [lastEvent, setLastEvent] = useState(null);

  useEffect(() => {
    const bridge = connectVisualEventSocket({
      url,
      onEvent: setLastEvent,
      onStatus: ({ status: nextStatus }) => setStatus(nextStatus),
    });

    return () => bridge.close();
  }, [url]);

  return { status, lastEvent, url };
}
