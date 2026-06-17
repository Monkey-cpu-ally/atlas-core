/* eslint-disable */
import { useCallback, useEffect, useRef, useState } from 'react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

/**
 * useAtlasJob — submit a long-running Atlas job and poll until it
 * completes. The Kubernetes ingress in front of the backend has a 60s
 * timeout; Atlas jobs (tri-council blueprint, 4-band teach) routinely
 * take 90–200s. The backend returns a job_id immediately; we poll
 * `GET /api/atlas/jobs/{job_id}` every 2 seconds until done/failed.
 *
 * The hook auto-cancels in-flight polling when the consuming component
 * unmounts (e.g. user closes a panel mid-generation) so we do not waste
 * LLM calls on hidden UI.
 *
 * Usage:
 *   const { run, cancel, status, result, error } = useAtlasJob();
 *   run('/api/atlas/blueprint/council', { concept });
 *   // status: 'idle' | 'pending' | 'running' | 'done' | 'failed'
 */
export function useAtlasJob() {
  const [status, setStatus] = useState('idle');
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const pollRef = useRef(null);
  const cancelledRef = useRef(false);
  const abortRef = useRef(null);

  const cancel = useCallback(() => {
    cancelledRef.current = true;
    if (pollRef.current) {
      clearTimeout(pollRef.current);
      pollRef.current = null;
    }
    if (abortRef.current) {
      abortRef.current.abort();
      abortRef.current = null;
    }
    setStatus('idle');
  }, []);

  // Auto-cancel on unmount: stop polling + abort the submit fetch so the
  // backend job (if not yet picked up) and the LLM (if still mid-generation)
  // are not consumed for a UI panel the user already closed.
  useEffect(() => () => {
    cancelledRef.current = true;
    if (pollRef.current) {
      clearTimeout(pollRef.current);
      pollRef.current = null;
    }
    if (abortRef.current) {
      abortRef.current.abort();
      abortRef.current = null;
    }
  }, []);

  const pollOnce = useCallback(async (jobId) => {
    if (cancelledRef.current) return;
    try {
      const res = await fetch(`${API_URL}/api/atlas/jobs/${jobId}`);
      if (!res.ok) throw new Error(`Job poll failed: HTTP ${res.status}`);
      const data = await res.json();
      if (cancelledRef.current) return;
      if (data.status === 'done') {
        setStatus('done');
        setResult(data.result);
        return;
      }
      if (data.status === 'failed') {
        setStatus('failed');
        setError(data.error || 'Job failed');
        return;
      }
      setStatus(data.status);
      pollRef.current = setTimeout(() => pollOnce(jobId), 2000);
    } catch (e) {
      if (cancelledRef.current) return;
      setStatus('failed');
      setError(String(e.message || e));
    }
  }, []);

  const run = useCallback(async (path, body) => {
    cancelledRef.current = false;
    setStatus('pending');
    setResult(null);
    setError(null);
    const controller = new AbortController();
    abortRef.current = controller;
    try {
      const res = await fetch(`${API_URL}${path}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
        signal: controller.signal,
      });
      if (!res.ok) throw new Error(`${path} → HTTP ${res.status}`);
      const data = await res.json();
      if (!data.job_id) throw new Error('No job_id returned');
      pollOnce(data.job_id);
    } catch (e) {
      if (e?.name === 'AbortError' || cancelledRef.current) return;
      setStatus('failed');
      setError(String(e.message || e));
    }
  }, [pollOnce]);

  return { run, cancel, status, result, error };
}
