const API_ENDPOINT = '/api/events';
const SESSION_KEY = 'sp_math_session_id';
const MAX_RETRIES = 3;

export function getOrCreateSessionId() {
  const existing = window.localStorage.getItem(SESSION_KEY);
  if (existing) return existing;

  const sessionId = crypto.randomUUID();
  window.localStorage.setItem(SESSION_KEY, sessionId);
  return sessionId;
}

function retryDelay(attempt) {
  return Math.min(2000, 250 * (2 ** attempt));
}

async function postEvent(payload, attempt = 0) {
  try {
    const response = await fetch(API_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      keepalive: true,
    });

    if (!response.ok) {
      throw new Error(`Event post failed with ${response.status}`);
    }
  } catch (err) {
    if (attempt >= MAX_RETRIES) {
      console.error('trackEvent failed after retries', err, payload);
      return;
    }
    await new Promise((resolve) => setTimeout(resolve, retryDelay(attempt)));
    await postEvent(payload, attempt + 1);
  }
}

export function trackEvent(eventName, metadata = {}, context = {}) {
  const payload = {
    event_id: crypto.randomUUID(),
    session_id: getOrCreateSessionId(),
    user_id: context.userId ?? null,
    student_id: context.studentId ?? 'anonymous_student',
    event_name: eventName,
    timestamp: new Date().toISOString(),
    metadata,
  };

  // Non-blocking fire-and-forget.
  void postEvent(payload);
}

/* Example usage in React:
import { trackEvent } from './tracking';

trackEvent('start_assessment', {
  device: 'desktop',
  stage: 'diagnostic',
  score: 0,
  total: 0,
  xp: 0,
}, {
  userId: 'user_123',
  studentId: 'Raphael',
});
*/
