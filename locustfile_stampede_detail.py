"""
Cache-stampede test — PROTECTED endpoint (/jobs/{id}/, uses cache.add() mutex lock).

Unlike the main locustfile.py, every simulated user here hits the SAME
job_id, not a random one. That's the point: the mutex lock in
JobListingViewSet.retrieve() only does anything meaningful when multiple
requests race for the same cold cache key. Spreading requests across ~99
different IDs (as the main locustfile does) almost never triggers real
lock contention.

USAGE:
    docker-compose exec redis redis-cli FLUSHALL
    locust -f locustfile_stampede_detail.py --headless -u 50 -r 50 --run-time 15s --host http://localhost:8000

Note --run-time is short on purpose — this test is about what happens in
the first cold-cache burst, not sustained load. -r 50 (ramp rate = user
count) spawns everyone at once, which is what actually creates a stampede;
a slow ramp would let the cache warm up before load gets heavy.

Set HOT_JOB_ID below to a real, active job ID in your DB.
"""
from locust import HttpUser, task, between, events
from locust.exception import StopUser

HOT_JOB_ID = 15416  # replace with a real active JobListing id from your DB

shared_token = {"access": None}


@events.test_start.add_listener
def fetch_shared_token(environment, **kwargs):
    import requests
    response = requests.post(
        f"{environment.host}/api/v1/accounts/token/",
        data={"username": "apurva", "password": "testpass123"},
    )
    response.raise_for_status()
    shared_token["access"] = response.json()["access"]


class StampedeHotDetailUser(HttpUser):
    wait_time = between(0, 0)
    host = "http://localhost:8000"

    def on_start(self):
        self.client.headers["Authorization"] = f"Bearer {shared_token['access']}"

    @task
    def hit_hot_job(self):
        self.client.get(f"/api/v1/jobs/{HOT_JOB_ID}/", name="/api/v1/jobs/[HOT_id]/")
        # Fire once, then stop — the whole point is measuring the FIRST
        # cold-cache burst, not a sustained loop. A sustained loop mixes
        # ~5 interesting cold requests in with ~1000+ boring warm ones,
        # which is exactly why the last run showed no real signal.
        raise StopUser()