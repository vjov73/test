# Coldwing Scanner Platform (CSP)

Repository:
https://github.com/vjov73/test

Branch principale:
main

Ultimo stato stabile:
- Docker Compose funzionante
- API + Redis + Worker operativi
- Report HTML in stile corporate
- Packaging sistemato
- RQ compatibile con versione attuale
- COLDWING_DATA_DIR configurabile
- SSH Git configurato

------------------------------------------
ARCHITETTURA ATTUALE
------------------------------------------

Componenti:

1) API
   FastAPI
   Entry point:
   uvicorn coldwing.api.app:app

2) Queue
   RQ + Redis

3) Worker
   coldwing.worker.rq_worker
   Task:
   coldwing.worker.tasks.execute_scan

4) Scheduler
   APScheduler
   Gestione subscriptions via JSON

5) Core Scanner
   coldwing.service.run_scan(job_spec)

6) Report
   Template Jinja2:
   coldwing/report/templates/report.html.j2
   Stile corporate
   Nessun dump JSON

------------------------------------------
AMBIENTE LOCALE (NO DOCKER)
------------------------------------------

Prerequisiti:
- Python 3.11
- Redis installato

Setup:

cd ~/coldwing/coldwing
python3.11 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e ".[dev]"

Avvio locale:

Terminale 1:
redis-server

Terminale 2:
export REDIS_URL="redis://127.0.0.1:6379/0"
python -m coldwing.worker.rq_worker

Terminale 3:
export REDIS_URL="redis://127.0.0.1:6379/0"
export COLDWING_DATA_DIR="$(pwd)/data"
export COLDWING_API_TOKEN="token-acme"
uvicorn coldwing.api.app:app --host 0.0.0.0 --port 8000

------------------------------------------
AMBIENTE DOCKER (REPLICABILE SENZA SBATTI)
------------------------------------------

Prerequisiti:
- Docker Desktop con WSL integration attiva

Avvio:

cd ~/coldwing/coldwing
docker compose -f docker/docker-compose.yml up --build

Container:
- redis
- api
- worker

Mount attuale:
./data:/data

Report generati in:
./data/tenants/<tenant>/scans/<job_id>/

------------------------------------------
REGOLE CRITICHE (NON ROMPERE)
------------------------------------------

1) Non usare Path("/data") hardcoded.
   Sempre:
   Path(os.getenv("COLDWING_DATA_DIR", "./data"))

2) Non usare rq.Connection.
   Usare:
   Queue(..., connection=redis_conn)
   Worker(..., connection=redis_conn)

3) Entry point API:
   uvicorn coldwing.api.app:app

4) Packaging:
   pyproject.toml deve includere:

   [tool.setuptools.packages.find]
   include = ["coldwing*"]

5) Python richiesto:
   requires-python = ">=3.11"

6) Non committare:
   - .venv
   - data/
   - dump.rdb
   - __pycache__

------------------------------------------
FLUSSO DI SVILUPPO CORRETTO
------------------------------------------

Micro-fix:
- Modifica locale
- pytest -q
- git add
- git commit
- git push

Feature grosse:
- Task a Codex
- PR
- Review
- Merge

------------------------------------------
CHECK PRE-FLIGHT PRIMA DI INSTALLARE
------------------------------------------

python3.11 --version
git pull
pip install -e ".[dev]"
pytest -q

------------------------------------------
ROADMAP PROSSIMA
------------------------------------------

- Severity scoring nel report
- KPI cards con colori corporate
- Export PDF
- Alerting su subscription
- Dashboard front-end
- Auth reale multi-tenant
- Hardening sicurezza API

------------------------------------------
STATO ATTUALE VALIDATO
------------------------------------------

Docker compose:
Funzionante

API:
Funzionante

Worker:
Funzionante

Redis:
Funzionante

Report corporate:
Attivo

------------------------------------------
OBIETTIVO
------------------------------------------

Rendere Coldwing:
- Replicabile
- Professionale
- Vendibile
- Scalabile
