from fastapi import FastAPI
import redis
import uuid
import os

app = FastAPI()


# GLOBAL STORE (persists across calls)
mock_store = {}


def mock_redis():
    class MockRedis:
        def lpush(self, key, value):
            mock_store.setdefault(key, []).append(value)

        def hset(self, key, mapping):
            mock_store.setdefault(key, {}).update(mapping)

        def hget(self, key, field):
            return mock_store.get(key, {}).get(field)

    return MockRedis()


# Redis connection
def get_redis():
    if os.getenv("TEST_MODE") == "true":
        return mock_redis()

    return redis.Redis(
        host=os.getenv("REDIS_HOST", "redis"),
        port=6379,
        decode_responses=True
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/jobs")
def create_job():
    r = get_redis()
    job_id = str(uuid.uuid4())

    r.lpush("jobs", job_id)
    r.hset(f"job:{job_id}", {"status": "queued"})

    return {"job_id": job_id, "status": "queued"}


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    r = get_redis()
    status = r.hget(f"job:{job_id}", "status")

    if not status:
        return {"error": "not found"}

    return {"job_id": job_id, "status": status}
