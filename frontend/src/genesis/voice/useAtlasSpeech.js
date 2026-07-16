import { useCallback, useEffect, useRef, useState } from "react";

function getSpeechSynthesis() {
  if (typeof window === "undefined") return null;
  return window.speechSynthesis || null;
}

export default function useAtlasSpeech() {
  const utteranceRef = useRef(null);
  const [state, setState] = useState("idle");
  const supported = Boolean(getSpeechSynthesis() && typeof window.SpeechSynthesisUtterance === "function");

  const cancel = useCallback(() => {
    const synthesis = getSpeechSynthesis();
    synthesis?.cancel();
    utteranceRef.current = null;
    setState("idle");
  }, []);

  const speak = useCallback((message) => {
    const text = String(message || "").trim();
    const synthesis = getSpeechSynthesis();
    if (!text || !synthesis || typeof window.SpeechSynthesisUtterance !== "function") return false;

    synthesis.cancel();
    const utterance = new window.SpeechSynthesisUtterance(text);
    utterance.rate = 0.96;
    utterance.pitch = 0.95;
    utterance.volume = 0.9;
    utterance.onstart = () => setState("speaking");
    utterance.onend = () => {
      utteranceRef.current = null;
      setState("idle");
    };
    utterance.onerror = () => {
      utteranceRef.current = null;
      setState("error");
    };
    utteranceRef.current = utterance;
    synthesis.speak(utterance);
    return true;
  }, []);

  useEffect(() => cancel, [cancel]);

  return { supported, state, speak, cancel };
}
