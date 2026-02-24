from __future__ import annotations

import os

from redis import Redis

from rq import Worker, Queue
from rq.job import get_current_job

from coldwing.service import run_scan


redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
redis_conn = Redis.from_url(redis_url)


def execute_scan(job_spec: dict) -> dict:
    job = get_current_job()

    def progress_cb(step: str, pct: int) -> None:
        if job:
            job.meta["step"] = step
            job.meta["progress"] = pct
            job.save_meta()

    return run_scan(job_spec, progress_cb=progress_cb)


def run_worker() -> None:
    q = Queue("coldwing", connection=redis_conn)
    worker = Worker([q], connection=redis_conn)
    worker.work()


if __name__ == "__main__":
    run_worker()
