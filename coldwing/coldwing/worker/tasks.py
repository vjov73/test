from __future__ import annotations

from typing import Any, Dict, Optional

from rq.job import get_current_job

def execute_scan(job_spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Task entrypoint eseguita dal worker RQ.
    Deve essere importabile senza side-effect (non avviare worker, non leggere env in import).
    """
    job = get_current_job()
    # Se il tuo service supporta progress_cb, qui puoi aggiornare job.meta e salvarlo.
    # Esempio: job.meta["progress"] = {"pct": 10, "step": "init"}; job.save_meta()

    # Import qui (lazy) per evitare import circolari all'import-time
    from coldwing.service import run_scan

    result = run_scan(job_spec)
    return result

