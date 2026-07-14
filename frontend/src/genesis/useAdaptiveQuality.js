import { useEffect, useMemo, useState } from "react";

const PROFILE_ORDER = ["eco", "balanced", "creator", "presentation"];

function detectProfile() {
  if (typeof window === "undefined") return "balanced";

  const reducedMotion = window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches;
  const saveData = navigator.connection?.saveData === true;
  const memory = Number(navigator.deviceMemory || 4);
  const cores = Number(navigator.hardwareConcurrency || 4);
  const narrow = window.innerWidth < 760;
  const highRefresh = window.matchMedia?.("(min-resolution: 2dppx)")?.matches;

  if (reducedMotion || saveData || memory <= 2 || cores <= 2) return "eco";
  if (narrow || memory <= 4 || cores <= 4) return "balanced";
  if (memory >= 8 && cores >= 8 && highRefresh) return "presentation";
  return "creator";
}

export default function useAdaptiveQuality() {
  const [profile, setProfile] = useState(detectProfile);

  useEffect(() => {
    let frame;
    const update = () => {
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() => setProfile(detectProfile()));
    };

    window.addEventListener("resize", update, { passive: true });
    navigator.connection?.addEventListener?.("change", update);
    const motion = window.matchMedia?.("(prefers-reduced-motion: reduce)");
    motion?.addEventListener?.("change", update);

    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener("resize", update);
      navigator.connection?.removeEventListener?.("change", update);
      motion?.removeEventListener?.("change", update);
    };
  }, []);

  return useMemo(() => ({
    profile,
    rank: PROFILE_ORDER.indexOf(profile),
    reducedEffects: profile === "eco",
    enhancedEffects: profile === "creator" || profile === "presentation",
    presentationEffects: profile === "presentation",
  }), [profile]);
}
