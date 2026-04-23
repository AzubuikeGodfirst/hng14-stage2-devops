import os
from fastapi.testclient import TestClient
from api.main import app

os.environ["TEST_MODE"] = "true"

client = TestClient(app)


def test_create_job():
    res = client.post("/jobs")
    assert res.status_code == 200
    assert "job_id" in res.json()


def test_get_job():
    res = client.post("/jobs")
    job_id = res.json()["job_id"]

    res2 = client.get(f"/jobs/{job_id}")
    assert res2.status_code == 200


def test_invalid_job():
    res = client.get("/jobs/invalid")
    assert res.status_code in [200, 404]
