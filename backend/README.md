# Backend: Event Tracking + Billing API

Run server:

```bash
python3 backend/server.py
```

Base URL: `http://localhost:8787`

## Event collector endpoint

### `POST /api/events`
Validates and stores event records quickly (append-only).

#### Event schema

```json
{
  "event_id": "uuid",
  "session_id": "string",
  "user_id": "string or null",
  "student_id": "Raphael",
  "event_name": "view_landing",
  "timestamp": "2026-04-08T12:00:00Z",
  "metadata": {
    "device": "desktop",
    "stage": "diagnostic",
    "score": 0,
    "total": 10,
    "xp": 0
  }
}
```

Supported `event_name` values:

- `view_landing`
- `start_assessment`
- `question_answered`
- `complete_assessment`
- `view_report`
- `click_upgrade`
- `purchase`

### Storage strategy

- Preferred: DynamoDB table via `EVENTS_DYNAMODB_TABLE` env var.
- Fallback: local JSONL append-only file (`backend/events.jsonl` or `EVENTS_JSONL_PATH`).

## Analytics

`backend/analytics.py` includes:

- `compute_funnel(events)`
- `compute_student_stats(events, student_id)`
- `segment_funnel(events, key)`

### Demo analytics output

```bash
python3 backend/analytics_demo.py
```

## Tests

```bash
python3 -m unittest backend.tests.test_event_pipeline
```

## Example API usage

```bash
curl -X POST http://localhost:8787/api/events \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "11111111-1111-1111-1111-111111111111",
    "session_id": "sess_abc",
    "user_id": "user_42",
    "student_id": "Raphael",
    "event_name": "start_assessment",
    "timestamp": "2026-04-08T12:10:00Z",
    "metadata": {
      "device": "desktop",
      "stage": "diagnostic",
      "score": 0,
      "total": 0,
      "xp": 0
    }
  }'
```

## Existing billing endpoints

- `GET /api/worksheets`
- `POST /billing/quote`
- `POST /billing/order`
- `POST /billing/payments/initiate`
- `POST /billing/payments/webhook`
- `POST /billing/allocate-partial`
- `GET /billing/entitlements?accountId=acct_demo&studentId=stu_demo`
- `POST /billing/access-worksheet`
