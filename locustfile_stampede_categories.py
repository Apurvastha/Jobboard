"""
Cache-stampede test — UNPROTECTED endpoint (/jobs/categories/, plain cache.set(),
no lock at all).

This is the control group for locustfile_stampede_detail.py. Same shape —
many concurrent users, one cold resource, immediate burst — but this
endpoint has no mutex protection. Comparing the two tells you whether the
lock in JobListingViewSet.retrieve() is actually doing anything, rather
than just assuming it is because the code exists.

USAGE:
    docker-compose exec redis redis-cli FLUSHALL
    locust -f locustfile_stampede_categories.py --headless -u 50 -r 50 --run-time 15s --host http://localhost:8000
"""
from locust import HttpUser, task, between, events
from locust.exception import StopUser

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


class StampedeHotCategoriesUser(HttpUser):
    wait_time = between(0, 0)
    host = "http://localhost:8000"

    def on_start(self):
        self.client.headers["Authorization"] = f"Bearer {shared_token['access']}"

    @task
    def hit_hot_categories(self):
        self.client.get("/api/v1/jobs/categories/", name="/api/v1/jobs/categories/[HOT]")
        raise StopUser()