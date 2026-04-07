#!/usr/bin/env python3
import json
import os
import sqlite3
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

ROOT = os.path.dirname(__file__)
DB_PATH = os.path.join(ROOT, "billing.db")
SCHEMA_PATH = os.path.join(ROOT, "schema.sql")

FREE_WORKSHEET_LIMIT = 3


def db_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = db_conn()
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())

    conn.execute(
        "INSERT OR IGNORE INTO accounts(id,email) VALUES(?,?)",
        ("acct_demo", "demo@spacademy.test"),
    )
    conn.execute(
        "INSERT OR IGNORE INTO students(id,account_id,first_name,grade) VALUES(?,?,?,?)",
        ("stu_demo", "acct_demo", "Player", "Year 3"),
    )
    seeds = [
        ("ws_001", "Worksheet 1: Number Bonds", "Numbers", "Year 3", 199),
        ("ws_002", "Worksheet 2: Fractions", "Fractions", "Year 3", 249),
        ("ws_003", "Worksheet 3: Time", "Measurement", "Year 3", 249),
        ("ws_004", "Worksheet 4: Multiplication", "Multiplication", "Year 3", 299),
        ("ws_005", "Worksheet 5: Division", "Division", "Year 3", 299),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO worksheets(id,title,strand,level,price_cents) VALUES(?,?,?,?,?)",
        seeds,
    )
    conn.commit()
    conn.close()


def upsert_free_or_paid_entitlement(conn, account_id, student_id, worksheet_id, source):
    conn.execute(
        """
        INSERT OR IGNORE INTO entitlements(account_id, student_id, worksheet_id, source)
        VALUES (?, ?, ?, ?)
        """,
        (account_id, student_id, worksheet_id, source),
    )


class Handler(BaseHTTPRequestHandler):
    def _json(self, code, payload):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode("utf-8"))

    def _read_json(self):
        size = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(size).decode("utf-8") if size else "{}"
        return json.loads(raw or "{}")

    def do_OPTIONS(self):
        self._json(200, {"ok": True})

    def do_GET(self):
        parsed = urlparse(self.path)
        conn = db_conn()
        try:
            if parsed.path == "/api/worksheets":
                rows = conn.execute(
                    "SELECT id,title,strand,level,price_cents FROM worksheets WHERE is_active=1 ORDER BY id"
                ).fetchall()
                self._json(200, {"worksheets": [dict(r) for r in rows]})
                return

            if parsed.path == "/billing/entitlements":
                q = parse_qs(parsed.query)
                account_id = q.get("accountId", ["acct_demo"])[0]
                student_id = q.get("studentId", ["stu_demo"])[0]
                rows = conn.execute(
                    """
                    SELECT worksheet_id, source, granted_at
                    FROM entitlements
                    WHERE account_id=? AND student_id=?
                    ORDER BY granted_at DESC
                    """,
                    (account_id, student_id),
                ).fetchall()
                self._json(200, {"entitlements": [dict(r) for r in rows]})
                return

            self._json(404, {"error": "Not found"})
        finally:
            conn.close()

    def do_POST(self):
        conn = db_conn()
        body = self._read_json()
        try:
            if self.path == "/billing/quote":
                account_id = body.get("accountId", "acct_demo")
                student_id = body.get("studentId", "stu_demo")
                worksheet_id = body.get("worksheetId")
                if not worksheet_id:
                    self._json(400, {"error": "worksheetId is required"})
                    return

                used = conn.execute(
                    "SELECT COUNT(*) c FROM free_quota_usage WHERE account_id=? AND student_id=?",
                    (account_id, student_id),
                ).fetchone()["c"]
                ws = conn.execute(
                    "SELECT id,title,price_cents FROM worksheets WHERE id=?",
                    (worksheet_id,),
                ).fetchone()
                if not ws:
                    self._json(404, {"error": "Worksheet not found"})
                    return

                free_remaining = max(FREE_WORKSHEET_LIMIT - used, 0)
                requires_payment = free_remaining == 0
                payable_cents = ws["price_cents"] if requires_payment else 0

                self._json(
                    200,
                    {
                        "worksheet": dict(ws),
                        "freeLimit": FREE_WORKSHEET_LIMIT,
                        "freeUsed": used,
                        "freeRemaining": free_remaining,
                        "requiresPayment": requires_payment,
                        "payableCents": payable_cents,
                        "currency": "USD",
                        "allowedModes": ["card", "wallet", "bank_transfer"],
                        "partialPaymentAllowed": True,
                    },
                )
                return

            if self.path == "/billing/order":
                account_id = body.get("accountId", "acct_demo")
                student_id = body.get("studentId", "stu_demo")
                worksheet_id = body.get("worksheetId")
                total_cents = int(body.get("totalCents", 0))
                order_id = f"ord_{uuid.uuid4().hex[:10]}"
                conn.execute(
                    """
                    INSERT INTO orders(id,account_id,student_id,worksheet_id,total_cents,status)
                    VALUES(?,?,?,?,?,?)
                    """,
                    (order_id, account_id, student_id, worksheet_id, total_cents, "created"),
                )
                conn.commit()
                self._json(201, {"orderId": order_id, "status": "created"})
                return

            if self.path == "/billing/payments/initiate":
                payment_id = f"pay_{uuid.uuid4().hex[:10]}"
                order_id = body.get("orderId")
                mode = body.get("mode", "card")
                amount_cents = int(body.get("amountCents", 0))
                conn.execute(
                    """
                    INSERT INTO payments(id,order_id,mode,provider,provider_ref,amount_cents,status)
                    VALUES(?,?,?,?,?,?,?)
                    """,
                    (
                        payment_id,
                        order_id,
                        mode,
                        "demo-gateway",
                        f"demo_{uuid.uuid4().hex[:8]}",
                        amount_cents,
                        "initiated",
                    ),
                )
                conn.commit()
                self._json(
                    200,
                    {
                        "paymentId": payment_id,
                        "status": "initiated",
                        "clientSecret": f"demo_secret_{payment_id}",
                    },
                )
                return

            if self.path == "/billing/payments/webhook":
                payment_id = body.get("paymentId")
                status = body.get("status", "succeeded")

                pay = conn.execute(
                    "SELECT * FROM payments WHERE id=?", (payment_id,)
                ).fetchone()
                if not pay:
                    self._json(404, {"error": "payment not found"})
                    return

                conn.execute("UPDATE payments SET status=? WHERE id=?", (status, payment_id))
                order = conn.execute(
                    "SELECT * FROM orders WHERE id=?", (pay["order_id"],)
                ).fetchone()
                paid_sum = conn.execute(
                    "SELECT COALESCE(SUM(amount_cents),0) s FROM payments WHERE order_id=? AND status='succeeded'",
                    (order["id"],),
                ).fetchone()["s"]

                if paid_sum >= order["total_cents"]:
                    order_status = "paid"
                    upsert_free_or_paid_entitlement(
                        conn,
                        order["account_id"],
                        order["student_id"],
                        order["worksheet_id"],
                        "paid",
                    )
                elif paid_sum > 0:
                    order_status = "partially_paid"
                else:
                    order_status = "created"

                conn.execute("UPDATE orders SET status=? WHERE id=?", (order_status, order["id"]))
                conn.commit()
                self._json(
                    200,
                    {
                        "orderId": order["id"],
                        "orderStatus": order_status,
                        "paidCents": paid_sum,
                        "totalCents": order["total_cents"],
                    },
                )
                return

            if self.path == "/billing/allocate-partial":
                order_id = body.get("orderId")
                order = conn.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
                if not order:
                    self._json(404, {"error": "order not found"})
                    return
                paid_sum = conn.execute(
                    "SELECT COALESCE(SUM(amount_cents),0) s FROM payments WHERE order_id=? AND status='succeeded'",
                    (order_id,),
                ).fetchone()["s"]
                pct = round((paid_sum / order["total_cents"]) * 100, 2) if order["total_cents"] else 0
                self._json(
                    200,
                    {
                        "orderId": order_id,
                        "paidCents": paid_sum,
                        "totalCents": order["total_cents"],
                        "paidPercent": pct,
                        "unlockState": "full" if paid_sum >= order["total_cents"] else "locked_until_full",
                    },
                )
                return

            if self.path == "/billing/access-worksheet":
                account_id = body.get("accountId", "acct_demo")
                student_id = body.get("studentId", "stu_demo")
                worksheet_id = body.get("worksheetId")
                if not worksheet_id:
                    self._json(400, {"error": "worksheetId is required"})
                    return

                has_entitlement = conn.execute(
                    """
                    SELECT 1 FROM entitlements
                    WHERE account_id=? AND student_id=? AND worksheet_id=?
                    """,
                    (account_id, student_id, worksheet_id),
                ).fetchone()
                if has_entitlement:
                    self._json(200, {"allowed": True, "source": "entitlement"})
                    return

                used = conn.execute(
                    "SELECT COUNT(*) c FROM free_quota_usage WHERE account_id=? AND student_id=?",
                    (account_id, student_id),
                ).fetchone()["c"]

                if used < FREE_WORKSHEET_LIMIT:
                    conn.execute(
                        "INSERT INTO free_quota_usage(account_id,student_id,worksheet_id) VALUES(?,?,?)",
                        (account_id, student_id, worksheet_id),
                    )
                    upsert_free_or_paid_entitlement(
                        conn, account_id, student_id, worksheet_id, "free"
                    )
                    conn.commit()
                    self._json(
                        200,
                        {
                            "allowed": True,
                            "source": "free",
                            "freeUsed": used + 1,
                            "freeRemaining": max(FREE_WORKSHEET_LIMIT - (used + 1), 0),
                        },
                    )
                    return

                self._json(
                    402,
                    {
                        "allowed": False,
                        "reason": "payment_required",
                        "freeUsed": used,
                        "freeRemaining": 0,
                    },
                )
                return

            self._json(404, {"error": "Not found"})
        finally:
            conn.close()


def run():
    init_db()
    port = int(os.environ.get("PORT", "8787"))
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"Billing API listening on http://localhost:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
