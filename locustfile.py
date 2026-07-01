from locust import HttpUser, task, between, events
import random

# Shared across all simulated users — logging in once, before the swarm
# starts, instead of once per user. Per-user login was hitting JobBoard's
# own 5/min throttle on the login endpoint almost immediately under load,
# which then cascaded into every other request going out unauthenticated
# and hitting the 100/day unauthenticated throttle too.
#
# This also matches real traffic more honestly: a real client logs in
# once and reuses the token for the rest of the session — it doesn't
# re-authenticate before every single page view.
shared_token = {"access": None}
active_job_ids = {"id": None}


@events.test_start.add_listener
def fetch_shared_token(environment, **kwargs):
    import requests
    response = requests.post(
        f"{environment.host}/api/v1/accounts/token/",
        data={"username": "apurva", "password": "testpass123"},
    )
    response.raise_for_status()
    shared_token["access"] = response.json()["access"]

@events.test_start.add_listener
def fetch_active_ids(environment, **kwargs):
    import requests
    response = requests.get(
        f"{environment.host}/api/v1/jobs?page_size=200",
    )
    response.raise_for_status()
    ids = response.json()['results']
    active_job_ids["id"] = [item['id'] for item in ids]
    print(active_job_ids)


class JobBoardUser(HttpUser):
    wait_time = between(0.1, 0.5)
    host = "http://localhost:8000"

    def on_start(self):
        # No HTTP call here anymore — just attach the token that was
        # already fetched once in fetch_shared_token() above.
        self.client.headers["Authorization"] = f"Bearer {shared_token['access']}"

    @task(5)
    def view_job_detail(self):
        # TODO: confirm this range matches real JobListing IDs in your
        # DB (check via Django shell — gaps from get_or_create skips in
        # seed_data.py mean not every ID 1-200 is guaranteed to exist,
        # which is the likely source of the 209 "404" entries in your
        # last run — separate issue from the throttle problem above).
        job_id = random.choice(active_job_ids['id'])
        self.client.get(f"/api/v1/jobs/{job_id}/", name="/api/v1/jobs/[id]/")

    @task(2)
    def view_categories(self):
        self.client.get("/api/v1/jobs/categories/")

    @task(1)
    def view_featured(self):
        self.client.get("/api/v1/jobs/featured/")
