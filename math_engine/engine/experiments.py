from __future__ import annotations

import hashlib
import threading
from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

ALLOWED_EVENTS = {"view_report", "click_cta", "purchase"}


@dataclass
class ExperimentState:
    """In-memory container for assignment and tracking data."""

    assignments: Dict[str, str] = field(default_factory=dict)
    events: List[Dict[str, str]] = field(default_factory=list)


class PricingExperimentEngine:
    """Simple in-memory experiment engine for pricing and funnel testing."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._variants = ("A", "B")
        self._state = ExperimentState()

        self._pricing_config: Dict[str, Dict[str, Any]] = {
            "free": {"price": 0, "currency": "USD", "features": ["weekly report"]},
            "basic": {"price": 19, "currency": "USD", "features": ["report", "practice set"]},
            "premium": {
                "price": 49,
                "currency": "USD",
                "features": ["report", "practice set", "parent alerts", "priority support"],
            },
        }

        self._funnel_variants: Dict[str, Dict[str, Any]] = {
            "A": {
                "cta_text": "Start personalised plan",
                "paywall_timing": "after_first_report",
            },
            "B": {
                "cta_text": "Unlock your child’s full growth plan",
                "paywall_timing": "after_second_report",
            },
        }

    def assign_variant(self, user_id: str) -> str:
        """Assign a deterministic A/B variant to a user."""
        user_key = str(user_id)

        with self._lock:
            if user_key in self._state.assignments:
                return self._state.assignments[user_key]

            digest = hashlib.sha256(user_key.encode("utf-8")).hexdigest()
            bucket = int(digest[:8], 16)
            variant = self._variants[bucket % len(self._variants)]
            self._state.assignments[user_key] = variant
            return variant

    def track_event(self, user_id: str, event_type: str) -> Dict[str, str]:
        """Track experiment funnel events for a given user."""
        if event_type not in ALLOWED_EVENTS:
            allowed = ", ".join(sorted(ALLOWED_EVENTS))
            raise ValueError(f"Unsupported event_type '{event_type}'. Allowed values: {allowed}")

        user_key = str(user_id)
        with self._lock:
            variant = self.assign_variant(user_key)
            event = {"user_id": user_key, "variant": variant, "event_type": event_type}
            self._state.events.append(event)
            return event

    def evaluate_experiment(self) -> Dict[str, Any]:
        """Compare variant conversion rates and funnel metrics."""
        with self._lock:
            assigned_users: Dict[str, set[str]] = defaultdict(set)
            converters: Dict[str, set[str]] = defaultdict(set)
            clickers: Dict[str, set[str]] = defaultdict(set)
            viewers: Dict[str, set[str]] = defaultdict(set)

            for user_id, variant in self._state.assignments.items():
                assigned_users[variant].add(user_id)

            for event in self._state.events:
                user_id = event["user_id"]
                variant = event["variant"]
                event_type = event["event_type"]

                if event_type == "view_report":
                    viewers[variant].add(user_id)
                elif event_type == "click_cta":
                    clickers[variant].add(user_id)
                elif event_type == "purchase":
                    converters[variant].add(user_id)

            by_variant: Dict[str, Dict[str, Any]] = {}
            for variant in self._variants:
                assigned_count = len(assigned_users[variant])
                viewer_count = len(viewers[variant])
                click_count = len(clickers[variant])
                purchase_count = len(converters[variant])

                conversion_rate = (purchase_count / assigned_count) if assigned_count else 0.0
                click_through_rate = (click_count / viewer_count) if viewer_count else 0.0

                by_variant[variant] = {
                    "assigned_users": assigned_count,
                    "view_report_users": viewer_count,
                    "click_cta_users": click_count,
                    "purchase_users": purchase_count,
                    "conversion_rate": round(conversion_rate, 4),
                    "click_through_rate": round(click_through_rate, 4),
                }

            a_rate = by_variant["A"]["conversion_rate"]
            b_rate = by_variant["B"]["conversion_rate"]
            lift_vs_a = round(((b_rate - a_rate) / a_rate), 4) if a_rate else None
            winner: Optional[str]
            if a_rate == b_rate:
                winner = None
            else:
                winner = "B" if b_rate > a_rate else "A"

            return {
                "by_variant": by_variant,
                "summary": {
                    "winner": winner,
                    "conversion_rate_lift_b_vs_a": lift_vs_a,
                    "total_tracked_events": len(self._state.events),
                },
            }

    @property
    def pricing_config(self) -> Dict[str, Dict[str, Any]]:
        """Return a copy of pricing configuration for external reads."""
        with self._lock:
            return deepcopy(self._pricing_config)

    def set_pricing_tier(self, tier_name: str, tier_config: Dict[str, Any]) -> None:
        """Create or replace an entire pricing tier configuration."""
        with self._lock:
            self._pricing_config[tier_name] = deepcopy(tier_config)

    def update_pricing_tier(self, tier_name: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Apply partial updates to a pricing tier and return the latest tier."""
        with self._lock:
            current = self._pricing_config.get(tier_name, {})
            merged = {**current, **updates}
            self._pricing_config[tier_name] = merged
            return deepcopy(merged)

    @property
    def funnel_variants(self) -> Dict[str, Dict[str, Any]]:
        """Return funnel variants with CTA copy and paywall timing settings."""
        with self._lock:
            return deepcopy(self._funnel_variants)

    def set_funnel_variant(self, variant: str, config: Dict[str, Any]) -> None:
        """Create or replace a funnel variant config."""
        with self._lock:
            self._funnel_variants[variant] = deepcopy(config)


_engine = PricingExperimentEngine()


def assign_variant(user_id: str) -> str:
    return _engine.assign_variant(user_id)


def track_event(user_id: str, event_type: str) -> Dict[str, str]:
    return _engine.track_event(user_id, event_type)


def evaluate_experiment() -> Dict[str, Any]:
    return _engine.evaluate_experiment()


def get_pricing_config() -> Dict[str, Dict[str, Any]]:
    return _engine.pricing_config


def set_pricing_tier(tier_name: str, tier_config: Dict[str, Any]) -> None:
    _engine.set_pricing_tier(tier_name=tier_name, tier_config=tier_config)


def update_pricing_tier(tier_name: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    return _engine.update_pricing_tier(tier_name=tier_name, updates=updates)


def get_funnel_variants() -> Dict[str, Dict[str, Any]]:
    return _engine.funnel_variants


def set_funnel_variant(variant: str, config: Dict[str, Any]) -> None:
    _engine.set_funnel_variant(variant=variant, config=config)
