import pytest
from django.core.cache import cache
from rest_framework import status


@pytest.mark.django_db
class TestCategoryCache:
    def setup_method(self):
        """Clear cache before each test."""
        cache.clear()

    def test_categories_cached_after_first_request(self, api_client, category):
        """Second request hits cache, not DB."""
        # first request — cache miss
        response1 = api_client.get("/api/v1/jobs/categories/")
        assert response1.status_code == status.HTTP_200_OK

        # cache should now be set
        cached = cache.get("all_categories")
        assert cached is not None

    def test_cache_invalidated_on_category_save(self, api_client, category):
        """Saving a category clears the categories cache."""
        # populate cache
        api_client.get("/api/v1/jobs/categories/")
        assert cache.get("all_categories") is not None

        # update category — signal should invalidate cache
        category.name = "Updated Backend"
        category.save()

        # cache should be gone
        assert cache.get("all_categories") is None

    def test_job_detail_cached(self, api_client, job_listing):
        """Job detail is cached after first request."""
        cache.clear()
        response = api_client.get(f"/api/v1/jobs/{job_listing.id}/")
        assert response.status_code == status.HTTP_200_OK

        cache_key = f"job:{job_listing.id}"
        assert cache.get(cache_key) is not None

    def test_job_cache_invalidated_on_update(
        self, company_client, api_client, job_listing
    ):
        """Updating a job invalidates its cache entry."""
        # populate cache
        api_client.get(f"/api/v1/jobs/{job_listing.id}/")
        assert cache.get(f"job:{job_listing.id}") is not None

        # update job — signal should clear cache
        job_listing.salary_min = 9999999
        job_listing.save()

        assert cache.get(f"job:{job_listing.id}") is None

    def test_job_detail_waits_for_lock_and_returns_data(self, api_client, job_listing):
        """When the lock is already held (simulating a concurrent request
        currently populating the cache), a second request should fall
        through the retry loop and still return real job data — not
        crash (the old missing-.data bug) and not return stale/empty
        data. This is the scenario general load testing couldn't isolate;
        only a deliberately-forced lock state proves this path works."""
        cache_key = f"job:{job_listing.id}"
        lock_key = f"job_lock:{job_listing.id}"

        # Simulate another request already holding the lock. Because
        # cache.add() only succeeds if the key doesn't already exist,
        # this forces the view's own cache.add(lock_key, ...) call to
        # return False when our request comes in — i.e. it forces our
        # request into the `else` (retry loop) branch, not the
        # lock-winner branch.
        cache.add(lock_key, "1", timeout=10)

        response = api_client.get(f"/api/v1/jobs/{job_listing.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == job_listing.id

    def test_featured_waits_for_lock_and_returns_data(
        self, api_client, multiple_job_listings
    ):
        """Same scenario as above, applied to the featured() endpoint —
        which had the same fixed-sleep bug AND a second bug (silently
        returning an empty list instead of falling back to a fresh
        query) that only surfaced under the isolated stampede test."""
        cache_key = "featured_jobs"
        lock_key = "featured_jobs_lock"

        cache.add(lock_key, "1", timeout=10)

        response = api_client.get("/api/v1/jobs/featured/")

        assert response.status_code == status.HTTP_200_OK
        # Before the fix, a slow lock-holder meant this would return an
        # empty list ([]) — silently — instead of falling back to a
        # fresh query. Asserting real data here is the actual regression
        # check for that bug.
        assert len(response.data) > 0