from coldwing.api.scheduler import SubscriptionManager
from coldwing.queue.adapter import QueueAdapter


class DummyQueue(QueueAdapter):
    def enqueue(self, job_spec: dict) -> str:
        return "job-1"

    def status(self, job_id: str) -> dict:
        return {}

    def result(self, job_id: str):
        return None


def test_scheduler_creation(tmp_path):
    q = DummyQueue()
    manager = SubscriptionManager(q, path=tmp_path / "subs.json")
    manager.start()
    sub = manager.create("tenant_acme", "examples/scope_example.yaml", "snapshot", "*/5 * * * *")
    assert sub["id"]
    assert manager.list("tenant_acme")
    manager.stop()
