# Billing backend (worksheets)

Run:

```bash
python3 backend/server.py
```

Base URL: `http://localhost:8787`

## Endpoints
- `GET /api/worksheets`
- `POST /billing/quote`
- `POST /billing/order`
- `POST /billing/payments/initiate`
- `POST /billing/payments/webhook`
- `POST /billing/allocate-partial`
- `GET /billing/entitlements?accountId=acct_demo&studentId=stu_demo`
- `POST /billing/access-worksheet`
