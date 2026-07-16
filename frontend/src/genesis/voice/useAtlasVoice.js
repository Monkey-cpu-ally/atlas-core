import { useCallback, useEffect, useRef, useState } from "react";

function getRecognitionConstructor() {
  if (typeof window === "undefined") return null;
  return window.SpeechRecognition || window.webkitSpeechRecognition || null;
}

export default function useAtlasVoice({ onTranscript } = {}) {
  const recognitionRef = useRef(null);
  const onTranscriptRef = useRef(onTranscript);
  const [state, setState] = useState("idle");
  const [transcript, setTranscript] = useState("");
  const [error, setError] = useState(null);
  const supported = Boolean(getRecognitionConstructor());

  useEffect(() => {
    onTranscriptRef.current = onTranscript;
  }, [onTranscript]);

  const stop = useCallback(() => {
    const recognition = recognitionRef.current;
    if (!recognition) {
      setState("idle");
      return;
    }
    try {
      recognition.stop();
    } catch (_) {
      setState("idle");
    }
  }, []);

  const start = useCallback(() => {
    const Recognition = getRecognitionConstructor();
    if (!Recognition) {
      setError("Voice recognition is unavailable in this browser.");
      setState("unsupported");
      return false;
    }

    if (recognitionRef.current) {
      try { recognitionRef.current.abort(); } catch (_) { /* no-op */ }
    }

    const recognition = new Recognition();
    recognition.lang = "en-US";
    recognition.interimResults = true;
    recognition.continuous = false;
    recognition.maxAlternatives = 1;
    recognitionRef.current = recognition;
    setTranscript("");
    setError(null);
    setState("listening");

    recognition.onresult = (event) => {
      const text = Array.from(event.results)
        .map((result) => result[0]?.transcript || "")
        .join(" ")
        .trim();
      setTranscript(text);
      const finalResult = Array.from(event.results).some((result) => result.isFinal);
      if (finalResult && text) {
        setState("processing");
        onTranscriptRef.current?.(text);
      }
    };
    recognition.onerror = (event) => {
      setError(event.error || "Voice recognition failed.");
      setState(event.error === "not-allowed" ? "permission-denied" : "error");
    };
    recognition.onend = () => {
      recognitionRef.current = null;
      setState((current) => current === "processing" ? "idle" : current === "listening" ? "idle" : current);
    };

    try {
      recognition.start();
      return true;
    } catch (startError) {
      recognitionRef.current = null;
      setError(startError?.message || "Voice recognition could not start.");
      setState("error");
      return false;
    }
  }, []);

  useEffect(() => () => {
    if (recognitionRef.current) {
      try { recognitionRef.current.abort(); } catch (_) { /* no-op */ }
    }
  }, []);

  return { supported, state, transcript, error, start, stop };
}
