from __future__ import annotations

import os
from uuid import uuid4

from redis import Redis
from rq import Queue
from rq.job import Job

from coldwing.queue.adapter import QueueAdapter
from coldwing.worker.rq_worker import execute_scan


class RQAdapter(QueueAdapter):
    def __init__(self) -> None:
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        self.redis = Redis.from_url(redis_url)
        self.queue = Queue("coldwing", connection=self.redis)

    def enqueue(self, job_spec: dict) -> str:
        job_id = job_spec.get("job_id") or str(uuid4())
        job_spec["job_id"] = job_id
        self.queue.enqueue(execute_scan, job_spec, job_id=job_id)
        return job_id

    def status(self, job_id: str) -> dict:
        job = Job.fetch(job_id, connection=self.redis)
        return {"job_id": job_id, "status": job.get_status(), "progress": job.meta.get("progress", 0)}

    def result(self, job_id: str) -> dict | None:
        job = Job.fetch(job_id, connection=self.redis)
        return job.result
