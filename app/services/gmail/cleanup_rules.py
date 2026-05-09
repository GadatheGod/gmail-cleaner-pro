"""
Scheduled Cleanup Rules Service
-------------------------------
Persistent cleanup rules that can be saved and executed.
"""

import json
import logging
import os
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

RULES_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "..", "cleanup_rules.json")

class CleanupRule:
    def __init__(self, id: str, sender: str, action: str, enabled: bool = True, schedule: str = "manual"):
        self.id = id
        self.sender = sender
        self.action = action  # "delete", "archive", "mark_read", "label"
        self.enabled = enabled
        self.schedule = schedule  # "manual", "daily", "weekly", "monthly"
        self.label_id = None
        self.created_at = datetime.now().isoformat()
        self.last_run = None
        self.run_count = 0

    def to_dict(self):
        return {
            "id": self.id,
            "sender": self.sender,
            "action": self.action,
            "enabled": self.enabled,
            "schedule": self.schedule,
            "label_id": self.label_id,
            "created_at": self.created_at,
            "last_run": self.last_run,
            "run_count": self.run_count
        }

    @staticmethod
    def from_dict(data: dict):
        rule = CleanupRule(
            id=data.get("id", ""),
            sender=data.get("sender", ""),
            action=data.get("action", "delete"),
            enabled=data.get("enabled", True),
            schedule=data.get("schedule", "manual")
        )
        rule.label_id = data.get("label_id")
        rule.created_at = data.get("created_at", rule.created_at)
        rule.last_run = data.get("last_run")
        rule.run_count = data.get("run_count", 0)
        return rule

def _load_rules() -> list:
    if not os.path.exists(RULES_FILE):
        return []
    try:
        with open(RULES_FILE, "r") as f:
            data = json.load(f)
            return [CleanupRule.from_dict(r) for r in data]
    except (json.JSONDecodeError, OSError):
        return []

def _save_rules(rules: list) -> None:
    try:
        with open(RULES_FILE, "w") as f:
            json.dump([r.to_dict() for r in rules], f, indent=2)
    except OSError:
        logger.exception("Failed to save cleanup rules")

def get_rules() -> list:
    rules = _load_rules()
    return [r.to_dict() for r in rules]

def add_rule(sender: str, action: str, schedule: str = "manual", label_id: Optional[str] = None) -> dict:
    import uuid
    rules = _load_rules()
    rule = CleanupRule(
        id=str(uuid.uuid4()),
        sender=sender,
        action=action,
        enabled=True,
        schedule=schedule,
    )
    rule.label_id = label_id
    rules.append(rule)
    _save_rules(rules)
    return rule.to_dict()

def delete_rule(rule_id: str) -> bool:
    rules = _load_rules()
    rules = [r for r in rules if r.id != rule_id]
    _save_rules(rules)
    return True

def toggle_rule(rule_id: str) -> Optional[dict]:
    rules = _load_rules()
    for rule in rules:
        if rule.id == rule_id:
            rule.enabled = not rule.enabled
            _save_rules(rules)
            return rule.to_dict()
    return None

def run_rule(rule_id: str) -> dict:
    from app.services.auth import get_gmail_service
    from app.services.gmail.delete import delete_emails_by_sender

    rules = _load_rules()
    rule = next((r for r in rules if r.id == rule_id), None)
    if not rule or not rule.enabled:
        return {"success": False, "message": "Rule not found or disabled"}

    result = delete_emails_by_sender(rule.sender)

    if result.get("success"):
        rule.last_run = datetime.now().isoformat()
        rule.run_count += 1
        _save_rules(rules)

    return result
