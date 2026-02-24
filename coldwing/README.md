# Coldwing Scanner Platform (CSP)

Piattaforma modulare per analisi di esposizione esterna su asset autorizzati con modalità on-demand, subscription ricorrenti e supporto SaaS multi-tenant.

## Features MVP
- Profili: Snapshot, Exposure, Advanced, Red Team.
- FastAPI multi-tenant con token per tenant.
- Queue adapter astratto (`QueueAdapter`) con implementazione RQ.
- Scheduler APScheduler con persistenza JSON.
- Report JSON + HTML e artifact su storage isolato tenant.
- Audit log JSONL, rate limit e timeout obbligatori.

## Setup WSL (Ubuntu)
```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv redis-server
```

## Setup venv
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .[dev]
```

## Avvio API (locale)
```bash
export COLDWING_INMEM_QUEUE=1
uvicorn coldwing.main:app --reload --host 0.0.0.0 --port 8000
```

## Run worker RQ
```bash
export REDIS_URL=redis://localhost:6379/0
python -m coldwing.worker.rq_worker
```

## Run CLI scan (esempio)
```bash
python - <<'PY'
from coldwing.service import run_scan
from coldwing.utils.config_loader import load_yaml
scope = load_yaml('examples/scope_example.yaml')
print(run_scan({'scope': scope, 'profile': 'snapshot', 'tenant_id': scope['tenant_id']}))
PY
```

## Docker Compose
```bash
cd docker
docker compose up --build
```

## Esempi curl
```bash
curl -X POST http://localhost:8000/v1/scans \
  -H 'Authorization: Bearer token-acme' \
  -H 'Content-Type: application/json' \
  -d '{"profile":"snapshot","scope":{"target":"example.com","allow_active_scan":true}}'

curl -H 'Authorization: Bearer token-acme' \
  http://localhost:8000/v1/scans/<scan_id>

curl -H 'Authorization: Bearer token-acme' \
  http://localhost:8000/v1/scans/<scan_id>/report
```

## Creare una subscription
```bash
curl -X POST http://localhost:8000/v1/subscriptions \
  -H 'Authorization: Bearer token-acme' \
  -H 'Content-Type: application/json' \
  -d '{"scope_path":"examples/scope_example.yaml","profile":"exposure","cron_expression":"*/10 * * * *"}'
```

## Note operative
- Opera solo su target in scope.
- Se `allow_active_scan=false`, i profili con exposure vengono bloccati.
- Se `allowed_ports` è definito, viene applicato come limite hard.
- Profilo Red Team richiede `redteam_approved=true` e `redteam_reference` non vuoto.
