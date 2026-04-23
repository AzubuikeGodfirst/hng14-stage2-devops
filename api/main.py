from fastapi import FastAPI, HTTPException
import redis
import uuid
import os

app = FastAPI()

# ------------------------------------
# TEST MODE CHECK
# ------------------------------------
TEST_MODE = os.getenv("TEST_MODE", "false") == "true"


def get_redis():
    if TEST_MODE:
        return FakeRedis()
    return redis.Redis(
        host=os.getenv("REDIS_HOST", "redis"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        decode_responses=True
    )


# ------------------------------------
# FAKE REDIS (FOR TESTS ONLY)
# ------------------------------------
class FakeRedis:
    def __init__(self):
        self.store = {}

    def lpush(self, key, value):
        self.store.setdefault(key, []).append(value)

    def hset(self, key, mapping):
        self.store[key] = mapping

    def hget(self, key, field):
        return self.store.get(key, {}).get(field)

    def ping(self):
        return True


# ------------------------------------
# ENDPOINTS
# ------------------------------------
@app.get("/health")
def health():
    try:
        r = get_redis()
        r.ping()
        return {"status": "ok"}
    except Exception:
        raise HTTPException(status_code=500, detail="Redis unavailable")


@app.post("/jobs")
def create_job():
    r = get_redis()

    job_id = str(uuid.uuid4())

    r.lpush("jobs", job_id)
    r.hset(f"job:{job_id}", mapping={"status": "queued"})

    return {"job_id": job_id, "status": "queued"}


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    r = get_redis()

    status = r.hget(f"job:{job_id}", "status")

    if not status:
        return {"job_id": job_id, "status": "not found"}

    return {"job_id": job_id, "status": status}
