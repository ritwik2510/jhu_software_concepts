# Module 6 — GradCafe Analysis Dashboard

A microservice dashboard that scrapes and analyzes graduate school applicant data using Flask, PostgreSQL, RabbitMQ, and Docker.

---

## Setup Instructions

1. **Install Docker Desktop**
   Download from https://www.docker.com/products/docker-desktop

2. **Start all services**
   ```
   docker compose up --build
   ```

3. **Load the database**
   ```
   docker compose exec worker python /app/db/load_data.py
   ```

4. **Open the dashboard**
   http://localhost:8080

5. **Open RabbitMQ UI** (optional)
   http://localhost:15672 — login: guest / guest

---

## Task Buttons

- **Scrape New Data** — fetches new applicant records from GradCafe in the background
- **Recompute Analysis** — refreshes all dashboard analytics without blocking the page

---

## Docker Hub

```
docker pull ritwik2510/module_6:web-v1
docker pull ritwik2510/module_6:worker-v1
```

https://hub.docker.com/r/ritwik2510/module_6

---

## GitHub

https://github.com/ritwik2510/jhu_software_concepts

---

## Notes

- All services run inside Docker — no local Python install needed
- Database resets if you run `docker compose down -v`
- Worker runs in the background automatically when the stack starts