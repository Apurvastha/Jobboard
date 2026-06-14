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
