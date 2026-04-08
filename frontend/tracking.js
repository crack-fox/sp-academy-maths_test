const API_ENDPOINT = '/api/events';
const SESSION_KEY = 'session_id';
const MAX_RETRIES = 3;

export function getSessionId() {
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
  const sessionId = getSessionId();
  const studentId = context.studentId ?? metadata.student_id ?? 'anonymous_student';

  const payload = {
    event_id: crypto.randomUUID(),
    session_id: sessionId,
    user_id: context.userId ?? null,
    student_id: studentId,
    event_name: eventName,
    timestamp: new Date().toISOString(),
    metadata: {
      ...metadata,
      session_id: sessionId,
      student_id: studentId,
    },
  };

  void postEvent(payload);
}

export function trackQuizCompletion({ score, total, xp }, context = {}) {
  trackEvent(
    'complete_assessment',
    {
      score,
      total,
      xp,
    },
    context,
  );
}
