from __future__ import annotations

import os
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse

from coldwing.api.authz import require_tenant_token
from coldwing.api.schemas import ScanCreate, SubscriptionCreate
from coldwing.api.scheduler import SubscriptionManager
from coldwing.api.storage import scan_dir
from coldwing.api.tenants import Tenant
from coldwing.queue.adapter import QueueAdapter
from coldwing.queue.rq_adapter import RQAdapter
from coldwing.service import run_scan


class InMemoryQueueAdapter(QueueAdapter):
    def __init__(self) -> None:
        self.jobs: dict[str, dict] = {}

    def enqueue(self, job_spec: dict) -> str:
        job_id = job_spec.get("job_id") or str(uuid4())
        job_spec["job_id"] = job_id
        self.jobs[job_id] = {"status": "finished", "result": run_scan(job_spec), "progress": 100}
        return job_id

    def status(self, job_id: str) -> dict:
        if job_id not in self.jobs:
            raise KeyError(job_id)
        return {"job_id": job_id, "status": self.jobs[job_id]["status"], "progress": self.jobs[job_id]["progress"]}

    def result(self, job_id: str) -> dict | None:
        return self.jobs.get(job_id, {}).get("result")


def make_queue() -> QueueAdapter:
    if os.getenv("COLDWING_INMEM_QUEUE", "0") == "1":
        return InMemoryQueueAdapter()
    return RQAdapter()


app = FastAPI(title="Coldwing Scanner Platform", version="0.1.0")
queue = make_queue()
subs = SubscriptionManager(queue)


@app.on_event("startup")
def startup_event() -> None:
    subs.start()


@app.on_event("shutdown")
def shutdown_event() -> None:
    subs.stop()


@app.post("/v1/scans")
def create_scan(payload: ScanCreate, tenant: Tenant = Depends(require_tenant_token)) -> dict:
    spec = payload.model_dump()
    spec["tenant_id"] = tenant.tenant_id
    spec["scope"]["tenant_id"] = tenant.tenant_id
    job_id = queue.enqueue(spec)
    return {"id": job_id}


@app.get("/v1/scans/{scan_id}")
def get_scan(scan_id: str, tenant: Tenant = Depends(require_tenant_token)) -> dict:
    try:
        status = queue.status(scan_id)
    except Exception as exc:
        raise HTTPException(status_code=404, detail="Scan not found") from exc
    result = queue.result(scan_id)
    if result and result.get("tenant_id") != tenant.tenant_id:
        raise HTTPException(status_code=404, detail="Scan not found")
    return {"status": status, "summary": result}


@app.get("/v1/scans/{scan_id}/report")
def get_scan_report(scan_id: str, tenant: Tenant = Depends(require_tenant_token)):
    summary = queue.result(scan_id)
    if not summary or summary.get("tenant_id") != tenant.tenant_id:
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(summary["report_html"], media_type="text/html")


@app.get("/v1/scans/{scan_id}/report.json")
def get_scan_report_json(scan_id: str, tenant: Tenant = Depends(require_tenant_token)):
    summary = queue.result(scan_id)
    if not summary or summary.get("tenant_id") != tenant.tenant_id:
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(summary["report_json"], media_type="application/json")


@app.post("/v1/subscriptions")
def create_subscription(payload: SubscriptionCreate, tenant: Tenant = Depends(require_tenant_token)) -> dict:
    sub = subs.create(tenant.tenant_id, payload.scope_path, payload.profile, payload.cron_expression)
    return sub


@app.get("/v1/subscriptions")
def list_subscriptions(tenant: Tenant = Depends(require_tenant_token)) -> list[dict]:
    return subs.list(tenant.tenant_id)


@app.delete("/v1/subscriptions/{sub_id}")
def delete_subscription(sub_id: str, tenant: Tenant = Depends(require_tenant_token)) -> dict:
    ok = subs.delete(sub_id, tenant.tenant_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return {"deleted": True}
