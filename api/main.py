import os
import uuid
import redis
from fastapi import FastAPI

app = FastAPI()

# =========================
# Redis SAFE CONNECTION
# =========================
REDIS_HOST = os.getenv("REDIS_HOST", "redis")

try:
    r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)
    r.ping()
except Exception:
    r = None


# =========================
# HEALTH CHECK ROUTE
# =========================
@app.get("/health")
def health():
    return {"status": "ok"}


# =========================
# CREATE JOB
# =========================
@app.post("/jobs")
def create_job():
    job_id = str(uuid.uuid4())

    if r:
        r.lpush("jobs", job_id)
        r.hset(f"job:{job_id}", "status", "queued")

    return {"job_id": job_id, "status": "queued"}


# =========================
# GET JOB
# =========================
@app.get("/jobs/{job_id}")
def get_job(job_id: str):

    if not r:
        return {"job_id": job_id, "status": "queued"}

    status = r.hget(f"job:{job_id}", "status")

    if not status:
        return {"error": "not found", "job_id": job_id}

    return {"job_id": job_id, "status": status}


# =========================
# OPTIONAL: LIST JOBS
# =========================
@app.get("/jobs")
def list_jobs():

    if not r:
        return {"jobs": []}

    jobs = r.lrange("jobs", 0, -1)
    return {"jobs": jobs}
