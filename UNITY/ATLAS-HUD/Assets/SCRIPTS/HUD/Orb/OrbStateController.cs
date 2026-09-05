using System;
using System.Collections;
using UnityEngine;

/// <summary>
/// State machine that drives the visual behaviour of the Atlas Core Orb.
///
/// States:
///   Standby  — orb is at rest; slow breathing only, rings at idle opacity.
///   Active   — an AI is selected; core brightens, rings glow at AI-keyed pulse.
///   Thinking — AI is reasoning; faster pulse, maximum ring intensity.
///   Speaking — AI is responding; brightest core, rapid pulse rhythm.
///
/// Pulse timing per AI (from atlas_motion_tokens.json):
///   Ajani   1800 ms  (focused, controlled)
///   Minerva 2200 ms  (patient, flowing)
///   Hermes  1400 ms  (inventive, quick)
///   Council 2600 ms  (deliberate, measured)
///
/// Usage: Added automatically by AtlasCoreOrb.Create(). Reference via AtlasCoreOrb.StateController.
/// </summary>
public class OrbStateController : MonoBehaviour
{
    // ── Current state ─────────────────────────────────────────────────────────

    private OrbState    currentState    = OrbState.Standby;
    private float       pulsePeriodSec  = 1.8f;   // default: Ajani pace
    private Coroutine   pulseRoutine;
    private AtlasCoreOrb orb;

    /// <summary>Fires whenever the orb transitions to a new state.</summary>
    public event Action<OrbState> OnStateChanged;

    // ── Setup ─────────────────────────────────────────────────────────────────

    /// <summary>Must be called once after AtlasCoreOrb is fully constructed.</summary>
    public void Initialize(AtlasCoreOrb orbRef)
    {
        orb = orbRef;
        ApplyState(OrbState.Standby);
    }

    // ── Public API ────────────────────────────────────────────────────────────

    public OrbState CurrentState => currentState;

    /// <summary>Transition the orb to a new operational state.</summary>
    public void SetState(OrbState newState)
    {
        if (newState == currentState) return;
        currentState = newState;

        if (pulseRoutine != null)
        {
            StopCoroutine(pulseRoutine);
            pulseRoutine = null;
        }

        ApplyState(newState);
        OnStateChanged?.Invoke(newState);
    }

    /// <summary>
    /// Updates the pulse timing to match the active AI's personality.
    /// Call this whenever SetAIIdentity() is called on the orb.
    /// </summary>
    public void SetPulsePeriod(float seconds)
    {
        pulsePeriodSec = Mathf.Max(0.1f, seconds);

        // Restart the pulse coroutine with the new timing if orb is not in Standby.
        if (currentState != OrbState.Standby && pulseRoutine != null)
        {
            StopCoroutine(pulseRoutine);
            pulseRoutine = StartCoroutine(PulseRoutine(PulseParamsForState(currentState)));
        }
    }

    // ── State application ─────────────────────────────────────────────────────

    private void ApplyState(OrbState state)
    {
        switch (state)
        {
            case OrbState.Standby:
                orb.SetCoreIntensity(0f);
                orb.SetRingIntensity(0f);
                break;

            case OrbState.Active:
                orb.SetCoreIntensity(0.45f);
                orb.SetRingIntensity(0.55f);
                pulseRoutine = StartCoroutine(PulseRoutine(PulseParamsForState(state)));
                break;

            case OrbState.Thinking:
                orb.SetCoreIntensity(0.70f);
                orb.SetRingIntensity(0.80f);
                pulseRoutine = StartCoroutine(PulseRoutine(PulseParamsForState(state)));
                break;

            case OrbState.Speaking:
                orb.SetCoreIntensity(0.90f);
                orb.SetRingIntensity(1.00f);
                pulseRoutine = StartCoroutine(PulseRoutine(PulseParamsForState(state)));
                break;
        }
    }

    // ── Pulse coroutine ───────────────────────────────────────────────────────

    private struct PulseParams
    {
        public float period;
        public float minIntensity;
        public float maxIntensity;
    }

    private PulseParams PulseParamsForState(OrbState state)
    {
        switch (state)
        {
            case OrbState.Active:
                return new PulseParams { period = pulsePeriodSec,         minIntensity = 0.35f, maxIntensity = 0.65f };
            case OrbState.Thinking:
                return new PulseParams { period = pulsePeriodSec * 0.65f, minIntensity = 0.55f, maxIntensity = 0.90f };
            case OrbState.Speaking:
                return new PulseParams { period = pulsePeriodSec * 0.45f, minIntensity = 0.70f, maxIntensity = 1.00f };
            default:
                return new PulseParams { period = pulsePeriodSec,         minIntensity = 0f,    maxIntensity = 0f    };
        }
    }

    private IEnumerator PulseRoutine(PulseParams p)
    {
        float phase = 0f;
        while (true)
        {
            phase += Time.deltaTime * (Mathf.PI * 2f / p.period);
            float t = (Mathf.Sin(phase) + 1f) * 0.5f;
            float intensity = Mathf.Lerp(p.minIntensity, p.maxIntensity, t);
            orb.SetCoreIntensity(intensity);
            yield return null;
        }
    }
    // ── Lifecycle ─────────────────────────────────────────────────────────────

    private void OnEnable()
    {
        // Restart the active pulse after a hide/show cycle.
        if (orb == null) return;   // Initialize() has not run yet; skip.

        if (pulseRoutine != null)
        {
            StopCoroutine(pulseRoutine);
            pulseRoutine = null;
        }
        ApplyState(currentState);
    }
}

/// <summary>Operational states of the Atlas Core Orb.</summary>
public enum OrbState
{
    /// <summary>No AI active. Orb breathes slowly at minimal glow.</summary>
    Standby,

    /// <summary>An AI has been selected and is ready to respond.</summary>
    Active,

    /// <summary>AI is currently processing or reasoning.</summary>
    Thinking,

    /// <summary>AI is actively speaking or streaming a response.</summary>
    Speaking
}
