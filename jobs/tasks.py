# jobs/tasks.py
import logging
import sentry_sdk
from sentry_sdk.crons import monitor
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)



@shared_task(bind=True, max_retries=3)
def deactivate_expired_jobs(self):
    """
    Runs every night at midnight.
    Finds all job listings where deadline has passed
    and is_active=True, then deactivates them.
    """
    try:
        from django.core.cache import cache

        from .models import JobListing

        today = timezone.now().date()

        # find all jobs past their deadline that are still active
        expired_jobs = JobListing.objects.filter(
            is_active=True,
            deadline__lt=today,
            deadline__isnull=False,  # only jobs with deadline set
        )

        count = expired_jobs.count()

        if count == 0:
            logger.info("No expired jobs found.")
            return "No expired jobs to deactivate."

        # collect IDs before update for cache invalidation
        expired_ids = list(expired_jobs.values_list("id", flat=True))

        # bult update - one SQL query regardless of count
        expired_jobs.update(is_active=False)

        # invalidate cache for each deactivated job
        for job_id in expired_ids:
            cache.delete(f"job:{job_id}")
        cache.delete("featured_jobs")

        logger.info(f"Deactivated {count} expired job listings: {expired_ids}")
        return f"Deactivated {count} expired jobs."

    except Exception as exc:
        logger.error(f"Failed to deactivate expired jobs: {exc}")
        raise self.retry(exc=exc, countdown=300)  # retry in 5 minutes


@shared_task(bind=True, max_retires=3)
def send_weekly_job_digest(self):
    """
    Runs every Sunday at 9 am.
    Sends a weekly digest of new jobs to all active candidates.
    """
    try:
        import time

        from django.conf import settings
        from django.core.mail import send_mail

        from accounts.models import CandidateProfile, User

        from .models import JobListing

        # get jobs posted in the last 7 days
        one_week_ago = timezone.now() - timezone.timedelta(days=7)
        new_jobs = (
            JobListing.objects.filter(
                is_active=True,
                posted_at__gte=one_week_ago,
            )
            .select_related("company", "category")
            .order_by("-posted_at")[:10]
        )

        if not new_jobs:
            logger.info("No new jobs this week - skipping digest.")
            return "No new job to digest."

        # build the job list text
        job_lines = []
        for job in new_jobs:
            salary = ""
            if job.salary_min and job.salary_max:
                salary = f" | ¥{job.salary_min:,} - ¥{job.salary_max:,}"
            job_lines.append(
                f"• {job.title} at {job.company.name}({job.location}){salary}"
            )

        job_list_text = "\n".join(job_lines)

        # get all active candidates
        candidates = User.objects.filter(
            role=User.Role.CANDIDATE,
            is_active=True,
        )
        total_candidates = candidates.count()
        sent_count = 0
        for candidate in candidates:
            try:
                emails_sent = send_mail(
                    subject=f"Weekly Job Digest - {len(new_jobs)} new  positions",
                    message=f"""
Hi {candidate.username},

Here are the latest job oppurtunities posted this week:

{job_list_text}

Visit JobBoard to see full details and apply.

Best regards,
    JobBoard Team
                    """.strip(),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[candidate.email],
                    fail_silently=False,  # so that one failed email doesnot fail the entire task
                )
                if emails_sent:
                    sent_count += 1
                else:
                    logger.warning(
                        f"Mailtrap did not accept email for {candidate.email}"
                    )

                time.sleep(2)

            except Exception as e:
                logger.warning(f"Failed to send digest to {candidate.email}: {e}")

        logger.info(f"Weekly digest complete. Sent: {sent_count}/{total_candidates}")
        return f"Digest sent to {sent_count}/{total_candidates} candidates."

    except Exception as exc:
        logger.error(f"Weekly digest task failed: {exc}")
        raise self.retry(exc=exc, countdown=300)


@shared_task
@monitor(monitor_slug='cleanup_cache')
def cleanup_stale_cache():
    """
    Runs every hour.
    Sentry monitors this task and alerts if it stops running.
    """
    from django.core.cache import cache

    # clear the featured jobs cache so it rebuilds fresh every hour
    cache.delete("featured_jobs")
    logger.info("Stale cache cleaned up.")
    return "Cache cleanup complete."
