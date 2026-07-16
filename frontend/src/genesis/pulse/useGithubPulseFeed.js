import { useEffect, useRef, useState } from "react";

const DEFAULT_INTERVAL_MS = 60_000;

function backendBaseUrl() {
  return (process.env.REACT_APP_BACKEND_URL || "").replace(/\/$/, "");
}

export default function useGithubPulseFeed({ enabled = true, intervalMs = DEFAULT_INTERVAL_MS } = {}) {
  const [snapshot, setSnapshot] = useState({
    status: "idle",
    connected: false,
    items: [],
    updatedAt: null,
    message: null,
  });
  const abortRef = useRef(null);

  useEffect(() => {
    if (!enabled) return undefined;
    let mounted = true;
    let timer;

    async function refresh() {
      abortRef.current?.abort();
      const controller = new AbortController();
      abortRef.current = controller;
      setSnapshot((current) => ({ ...current, status: current.updatedAt ? "refreshing" : "loading" }));

      try {
        const response = await fetch(`${backendBaseUrl()}/api/pulse/github/activity`, {
          signal: controller.signal,
          headers: { Accept: "application/json" },
        });
        if (!response.ok) throw new Error(`GitHub Pulse request failed (${response.status})`);
        const data = await response.json();
        if (!mounted) return;
        setSnapshot({
          status: data.status || (data.connected ? "connected" : "unavailable"),
          connected: Boolean(data.connected),
          items: Array.isArray(data.items) ? data.items : [],
          updatedAt: data.updatedAt || new Date().toISOString(),
          message: data.message || null,
        });
      } catch (error) {
        if (!mounted || error.name === "AbortError") return;
        setSnapshot((current) => ({
          ...current,
          status: "unavailable",
          connected: false,
          message: error.message,
        }));
      }
    }

    refresh();
    timer = window.setInterval(refresh, Math.max(15_000, intervalMs));
    return () => {
      mounted = false;
      window.clearInterval(timer);
      abortRef.current?.abort();
    };
  }, [enabled, intervalMs]);

  return snapshot;
}
