from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4

from coldwing.core import (
    api_integrations,
    baseline,
    dns_analysis,
    email_security,
    exposure_check,
    hosting_info,
    profiles,
    scope as scope_mod,
    ssl_analysis,
    subdomain_enum,
    tech_fingerprint,
)
from coldwing.core.redteam import content_discovery, deep_fingerprint, exposure_plus
from coldwing.report.report_html import build_html_report
from coldwing.report.report_json import build_json_report
from coldwing.utils.logger import get_logger
from coldwing.utils.rate_limit import RateLimiter
from coldwing.utils.timeutil import utc_now_iso

ProgressCb = Callable[[str, int], None]
LOGGER = get_logger(__name__)
DATA_ROOT = Path("/data")


def _audit_write(scan_dir: Path, event: dict[str, Any]) -> None:
    with open(scan_dir / "audit.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")


def run_scan(job_spec: dict, progress_cb: ProgressCb | None = None) -> dict:
    job_id = job_spec.get("job_id") or str(uuid4())
    tenant_id = job_spec.get("tenant_id")
    if not tenant_id:
        raise ValueError("tenant_id is required")
    profile_name = job_spec.get("profile", "snapshot")
    profile = profiles.load_profile(profile_name)
    scope = scope_mod.validate_scope(job_spec["scope"])
    scope_mod.enforce_redteam(scope, profile.get("redteam", False))

    scan_dir = DATA_ROOT / "tenants" / tenant_id / "scans" / job_id
    scan_dir.mkdir(parents=True, exist_ok=True)
    limiter = RateLimiter(float(job_spec.get("rate_limit", 5)))
    timeout_s = int(job_spec.get("timeout_s", 120))

    def step(name: str, pct: int) -> None:
        limiter.wait()
        _audit_write(scan_dir, {"timestamp": utc_now_iso(), "event": name, "progress": pct})
        if progress_cb:
            progress_cb(name, pct)

    target = scope["target"]
    results: dict[str, Any] = {
        "job_id": job_id,
        "tenant_id": tenant_id,
        "profile": profile_name,
        "target": target,
        "started_at": utc_now_iso(),
        "timeout_s": timeout_s,
    }

    step("dns_analysis", 10)
    results["dns"] = dns_analysis.run(target)
    step("hosting_info", 20)
    results["hosting"] = hosting_info.run(target)
    step("ssl_analysis", 30)
    results["ssl"] = ssl_analysis.run(target)
    step("email_security", 40)
    results["email_security"] = email_security.run(target)

    sub_limit = int(profile.get("subdomain_limit", 5))
    step("subdomain_enum", 50)
    results["subdomains"] = subdomain_enum.run(target, sub_limit)

    tech_deep = bool(profile.get("tech_deep", False))
    step("tech_fingerprint", 60)
    results["tech"] = tech_fingerprint.run(target, tech_deep)

    if profile.get("exposure", False):
        if not scope.get("allow_active_scan", False):
            raise PermissionError("Profile requires active scan, but allow_active_scan is false")
        ports = scope.get("allowed_ports") or profile.get("ports", [])
        if scope.get("allowed_ports"):
            ports = [p for p in profile.get("ports", []) if p in set(scope["allowed_ports"]) ]
        step("exposure_check", 75)
        results["exposure"] = exposure_check.run(target, ports)

    if profile.get("baseline", False):
        step("baseline", 82)
        results["baseline"] = baseline.run(target)

    results["api_integrations"] = api_integrations.run_shodan(target, bool(job_spec.get("api_shodan", False)))

    if profile.get("redteam", False):
        step("deep_fingerprint", 88)
        results["deep_fingerprint"] = deep_fingerprint.run(target)
        ports = scope.get("allowed_ports") or profile.get("ports", [])
        step("exposure_plus", 92)
        results["exposure_plus"] = exposure_plus.run(target, ports)
        step("content_discovery", 95)
        results["content_discovery"] = content_discovery.run(target)

    results["completed_at"] = utc_now_iso()
    results["status"] = "completed"

    json_report = build_json_report(results)
    html_report = build_html_report(results)
    (scan_dir / "report.json").write_text(json.dumps(json_report, indent=2), encoding="utf-8")
    (scan_dir / "report.html").write_text(html_report, encoding="utf-8")

    summary = {
        "job_id": job_id,
        "tenant_id": tenant_id,
        "status": "completed",
        "target": target,
        "profile": profile_name,
        "report_json": str(scan_dir / "report.json"),
        "report_html": str(scan_dir / "report.html"),
    }
    (scan_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    step("completed", 100)
    LOGGER.info("Scan completed: %s", job_id)
    return summary
