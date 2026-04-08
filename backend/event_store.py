from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List

try:
    import boto3
except Exception:  # boto3 optional
    boto3 = None

ROOT = os.path.dirname(__file__)
DEFAULT_JSONL_PATH = os.path.join(ROOT, "events.jsonl")

LOGGER = logging.getLogger("event_store")


class EventStore:
    def append_event(self, event: Dict[str, Any]) -> None:
        raise NotImplementedError

    def load_events(self) -> List[Dict[str, Any]]:
        raise NotImplementedError


class JsonlEventStore(EventStore):
    def __init__(self, path: str = DEFAULT_JSONL_PATH):
        self.path = path

    def append_event(self, event: Dict[str, Any]) -> None:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")

    def load_events(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.path):
            return []
        rows: List[Dict[str, Any]] = []
        with open(self.path, "r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                rows.append(json.loads(line))
        return rows


class DynamoDbEventStore(EventStore):
    def __init__(self, table_name: str, region_name: str = "us-east-1"):
        if boto3 is None:
            raise RuntimeError("boto3 is not installed")
        resource = boto3.resource("dynamodb", region_name=region_name)
        self.table = resource.Table(table_name)

    def append_event(self, event: Dict[str, Any]) -> None:
        self.table.put_item(Item=event)

    def load_events(self) -> List[Dict[str, Any]]:
        response = self.table.scan()
        items = response.get("Items", [])
        while "LastEvaluatedKey" in response:
            response = self.table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
            items.extend(response.get("Items", []))
        return items


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_event_store() -> EventStore:
    table_name = os.environ.get("EVENTS_DYNAMODB_TABLE", "").strip()
    if table_name:
        try:
            return DynamoDbEventStore(
                table_name=table_name,
                region_name=os.environ.get("AWS_REGION", "us-east-1"),
            )
        except Exception as exc:
            LOGGER.error("DynamoDB unavailable, falling back to JSONL: %s", exc)

    jsonl_path = os.environ.get("EVENTS_JSONL_PATH", DEFAULT_JSONL_PATH)
    return JsonlEventStore(jsonl_path)


def append_many(store: EventStore, events: Iterable[Dict[str, Any]]) -> None:
    for event in events:
        store.append_event(event)
