# EC2 Deployment Notes

## Instance
- Ubuntu 26.04 LTS (AWS's "22.04" quick-start option defaulted to this newer LTS)
- t3.micro
- Security group: 22 (SSH, my IP only), 8080 (app, my IP only) — 5432 and 15672 not exposed

## Setup steps
1. SSH in, installed Docker: `sudo apt-get install -y docker.io docker-compose-v2`
   (Note: on Ubuntu 26.04 the package is `docker-compose-v2`, not `docker-compose-plugin`)
2. Cloned the repo, `cd Module6`
3. Created `docker-compose.ec2.yml` — same services as local `docker-compose.yml`,
   but with 5432/15672 no longer published to the host
4. Brought the stack up: `docker compose -f docker-compose.ec2.yml up -d --build`
5. Loaded schema + data with a one-off container run of `src/db/load_data.py`
   against the EC2 Postgres (see command below)

## Troubleshooting encountered
- **`docker-compose-plugin` not found**: this AMI shipped Ubuntu 26.04, not 22.04;
  package is named `docker-compose-v2` there instead.
- **`relation "applicants" does not exist`**: fresh Postgres has no schema. Ran
  `src/db/load_data.py` as a one-off container against the `web` image to create
  the schema and load all 5,000 records.
- **Selenium `Cache folder (/.cache/selenium) cannot be created: Permission denied`**:
  worker runs as non-root (`USER 1000`) with no writable home dir. Fixed by adding
  `HOME=/tmp` to the worker's environment.
- **Worker logs appeared empty even after tasks were sent**: Python's stdout was
  buffered inside the container. Fixed by adding `PYTHONUNBUFFERED=1`.
- **`scrape_new_data` task fails**: `session not created: Chrome instance exited` —
  known headless-Chrome-in-Docker issue, likely `t3.micro`'s limited memory/`/dev/shm`
  size. Used `recompute_analytics` instead to verify the task pipeline end-to-end.
- **`recompute_analytics` failed with a SQL syntax error**: `REFRESH MATERIALIZED
  VIEW IF EXISTS` isn't valid Postgres syntax, and the view didn't exist yet. Created
  `applicant_summary` manually and fixed the `IF EXISTS` clause in `consumer.py`.

## Verification
- Dashboard reachable at http://<EC2_PUBLIC_IP>:8080
- `docker compose ps` shows all 4 services running/healthy
- Triggered `recompute_analytics` from the UI; worker logs show
  "Received task" → "Analytics recomputed" → "Task completed successfully"

## Shutdown
Both the SageMaker notebook and this EC2 instance were stopped after
verification to avoid ongoing charges.