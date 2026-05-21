import { useCallback, useRef, useState } from 'react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

/**
 * useAtlasJob — submit a long-running Atlas job and poll until it
 * completes. The Kubernetes ingress in front of the backend has a 60s
 * timeout; Atlas jobs (tri-council blueprint, 4-band teach) routinely
 * take 90–200s. The backend returns a job_id immediately; we poll
 * `GET /api/atlas/jobs/{job_id}` every 2 seconds until done/failed.
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

  const cancel = useCallback(() => {
    cancelledRef.current = true;
    if (pollRef.current) {
      clearTimeout(pollRef.current);
      pollRef.current = null;
    }
    setStatus('idle');
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
    try {
      const res = await fetch(`${API_URL}${path}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (!res.ok) throw new Error(`${path} → HTTP ${res.status}`);
      const data = await res.json();
      if (!data.job_id) throw new Error('No job_id returned');
      pollOnce(data.job_id);
    } catch (e) {
      setStatus('failed');
      setError(String(e.message || e));
    }
  }, [pollOnce]);

  return { run, cancel, status, result, error };
}
