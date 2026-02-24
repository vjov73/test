from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from coldwing.queue.adapter import QueueAdapter
from coldwing.utils.config_loader import load_yaml


class SubscriptionManager:
    def __init__(self, queue: QueueAdapter, path: Path | None = None) -> None:
        self.queue = queue
        self.scheduler = BackgroundScheduler()
        self.path = path or Path("/data/subscriptions.json")
        self.subscriptions: dict[str, dict] = {}

    def start(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.scheduler.start()
        self.load()

    def stop(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)

    def save(self) -> None:
        self.path.write_text(json.dumps(self.subscriptions, indent=2), encoding="utf-8")

    def load(self) -> None:
        if not self.path.exists():
            return
        self.subscriptions = json.loads(self.path.read_text(encoding="utf-8"))
        for sub_id, sub in self.subscriptions.items():
            self._schedule_existing(sub_id, sub)

    def _schedule_existing(self, sub_id: str, sub: dict) -> None:
        trigger = CronTrigger.from_crontab(sub["cron_expression"])
        self.scheduler.add_job(
            self.enqueue_subscription,
            trigger=trigger,
            id=sub_id,
            replace_existing=True,
            args=[sub_id],
        )

    def enqueue_subscription(self, sub_id: str) -> str:
        sub = self.subscriptions[sub_id]
        scope = load_yaml(sub["scope_path"])
        job_spec = {"scope": scope, "profile": sub["profile"], "tenant_id": sub["tenant_id"]}
        return self.queue.enqueue(job_spec)

    def create(self, tenant_id: str, scope_path: str, profile: str, cron_expression: str) -> dict:
        sub_id = str(uuid4())
        sub = {
            "id": sub_id,
            "tenant_id": tenant_id,
            "scope_path": scope_path,
            "profile": profile,
            "cron_expression": cron_expression,
        }
        self.subscriptions[sub_id] = sub
        self._schedule_existing(sub_id, sub)
        self.save()
        return sub

    def list(self, tenant_id: str) -> list[dict]:
        return [s for s in self.subscriptions.values() if s["tenant_id"] == tenant_id]

    def delete(self, sub_id: str, tenant_id: str) -> bool:
        sub = self.subscriptions.get(sub_id)
        if not sub or sub["tenant_id"] != tenant_id:
            return False
        self.subscriptions.pop(sub_id)
        try:
            self.scheduler.remove_job(sub_id)
        except Exception:
            pass
        self.save()
        return True
