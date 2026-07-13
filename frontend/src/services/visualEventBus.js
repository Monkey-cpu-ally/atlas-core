const ATLAS_EVENT_NAME = "atlas:visual-event";

const PERSONAS = new Set(["ajani", "minerva", "hermes", "council", "atlas"]);
const STATES = new Set([
  "idle",
  "listening",
  "thinking",
  "speaking",
  "working",
  "warning",
  "error",
  "offline",
]);

export function createVisualEvent(event, payload = {}, options = {}) {
  if (!event || typeof event !== "string") {
    throw new TypeError("ATLAS visual events require a string event name.");
  }

  if (payload.persona && !PERSONAS.has(payload.persona)) {
    throw new TypeError(`Unknown ATLAS persona: ${payload.persona}`);
  }

  if (payload.state && !STATES.has(payload.state)) {
    throw new TypeError(`Unknown ATLAS visual state: ${payload.state}`);
  }

  return {
    version: "1.0",
    event,
    timestamp: new Date().toISOString(),
    source: options.source || "atlas-web",
    correlation_id: options.correlationId || null,
    payload,
  };
}

export function publishVisualEvent(event, payload = {}, options = {}) {
  const envelope = createVisualEvent(event, payload, options);
  window.dispatchEvent(new CustomEvent(ATLAS_EVENT_NAME, { detail: envelope }));
  return envelope;
}

export function subscribeToVisualEvents(handler) {
  if (typeof handler !== "function") {
    throw new TypeError("ATLAS visual-event subscriber must be a function.");
  }

  const listener = (browserEvent) => handler(browserEvent.detail);
  window.addEventListener(ATLAS_EVENT_NAME, listener);

  return () => window.removeEventListener(ATLAS_EVENT_NAME, listener);
}

export function connectVisualEventSocket({ url, onEvent, onStatus } = {}) {
  if (!url) {
    throw new TypeError("A WebSocket URL is required.");
  }

  let socket;
  let closedByClient = false;
  let reconnectTimer;
  let attempt = 0;

  const report = (status, detail = {}) => onStatus?.({ status, ...detail });

  const connect = () => {
    report("connecting", { attempt });
    socket = new WebSocket(url);

    socket.addEventListener("open", () => {
      attempt = 0;
      report("connected");
    });

    socket.addEventListener("message", (message) => {
      try {
        const envelope = JSON.parse(message.data);
        publishVisualEvent(envelope.event, envelope.payload, {
          source: envelope.source,
          correlationId: envelope.correlation_id,
        });
        onEvent?.(envelope);
      } catch (error) {
        report("invalid-message", { error });
      }
    });

    socket.addEventListener("close", () => {
      report("disconnected");
      if (closedByClient) return;
      attempt += 1;
      const delay = Math.min(1000 * 2 ** attempt, 15000);
      reconnectTimer = window.setTimeout(connect, delay);
    });

    socket.addEventListener("error", (error) => report("error", { error }));
  };

  connect();

  return {
    send(event, payload = {}) {
      if (socket?.readyState !== WebSocket.OPEN) {
        throw new Error("ATLAS visual-event socket is not connected.");
      }
      socket.send(JSON.stringify(createVisualEvent(event, payload)));
    },
    close() {
      closedByClient = true;
      window.clearTimeout(reconnectTimer);
      socket?.close();
    },
  };
}

export const visualEventName = ATLAS_EVENT_NAME;
