# FIXES DOCUMENTATION

## 1. Redis connection issue in Docker

- File: api/main.py, worker.py
- Problem: Redis was configured as "localhost"
- Cause: Inside Docker containers, "localhost" refers to the container itself, not the Redis service
- Fix: Changed Redis host to "redis" (Docker service name in docker-compose network)

## 2. Docker Compose version mismatch
- Issue: legacy docker-compose caused KeyError
- Fix: migrated to Docker Compose v2

## 3. Port conflict (6379)
- Issue: local Redis service conflicted with container
- Fix: stopped system Redis or used Docker-only Redis

## 4. Worker crash
- Issue: worker connecting to localhost Redis
- Fix: updated to redis host "redis"

## 5. Missing production readiness
- Added healthchecks, restart policies, resource limits
