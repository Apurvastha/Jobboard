# jobs/management/commands/seed_bulk_volume.py
"""
Seeds high-volume, low-effort job postings purely to test query performance,
index behavior, and cache-stampede protection under realistic data scale.

THIS IS NOT FOR THE RAG/EVAL CORPUS. seed_realistic_jobs.py already covers
that with a small, hand-labeled set. This command exists for a different
question entirely: "does my indexing and caching hold up at 20k+ rows, and
under concurrent load?" Cheap filler text is fine here — nobody is reading
or embedding these descriptions.

SAFETY GUARD — LOCAL ONLY, ON PURPOSE:
This command refuses to run if it detects a `DATABASE_URL` environment
variable. Per this project's own settings.py:

    DATABASE_URL set    -> Railway/production (dj_database_url.parse(...))
    DATABASE_URL unset  -> local Docker Compose (DB_HOST/DB_NAME/etc.)

That's a real, structural signal already present in this codebase — not a
guess. There is deliberately NO override flag. If you genuinely need to run
this against a non-local database, edit this file and remove the guard
yourself; that friction is intentional so it can't happen by accident.

Even with the guard, do not run this against Railway: 20-30k synthetic
postings would be visible to anyone browsing your live Swagger demo, which
is exactly what you don't want a recruiter to see.

PERFORMANCE NOTES (why this command looks different from seed_realistic_jobs.py):
- Tags are inserted via the M2M through-table directly
  (`JobListing.tags.through.objects.bulk_create(...)`), not via a per-row
  `.tags.set()` loop. At a few hundred rows a loop is invisible; at 20k+
  rows it's thousands of individual queries and becomes the actual
  bottleneck of running this command.
- `posted_at` is auto_now_add, so bulk_create always stamps it with "now"
  regardless of what you pass in — Django calls each field's pre_save()
  during the insert, and DateTimeField.pre_save() overrides auto_now_add
  fields unconditionally. To get a realistic spread of posting dates (useful
  for testing the `-posted_at` ordering/index), this command does a second
  pass with bulk_update(), which does NOT call pre_save() and so will
  actually accept the backdated value.

USAGE (local Docker Compose only):
    docker-compose exec web python manage.py seed_bulk_volume
    docker-compose exec web python manage.py seed_bulk_volume --count 30000
    docker-compose exec web python manage.py seed_bulk_volume --clear-existing
"""
import os
import random
from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from accounts.models import CompanyProfile
from jobs.models import Category, JobListing, Tag

TITLE_MARKER = "[BULK]"

ROLE_TITLES = [
    "Software Engineer", "Backend Developer", "Frontend Developer",
    "Data Analyst", "Data Engineer", "DevOps Engineer", "QA Engineer",
    "Product Manager", "Solutions Architect", "Site Reliability Engineer",
    "Mobile Developer", "Machine Learning Engineer", "UI/UX Designer",
    "Sales Representative", "Marketing Specialist", "Technical Writer",
    "Security Engineer", "Database Administrator", "Cloud Engineer",
    "Systems Analyst",
]

LEVEL_PREFIXES = ["Junior", "Mid-level", "Senior", "Lead", ""]

LOCATIONS = [
    "Tokyo", "Osaka", "Kyoto", "Fukuoka", "Nagoya", "Sapporo",
    "Yokohama", "Remote (Japan)", "Remote (Global)",
]

JOB_TYPES = ["full_time", "part_time", "contract", "internship"]
EXPERIENCE_LEVELS = ["junior", "mid", "senior"]

DESCRIPTION_FILLERS = [
    "Join our growing team and contribute to projects that scale.",
    "We're looking for someone who thrives in a fast-paced environment.",
    "This role involves close collaboration with cross-functional teams.",
    "You'll have the opportunity to work on high-impact projects.",
    "We value clear communication and ownership of your work.",
    "This position offers room for growth within the organization.",
]


class Command(BaseCommand):
    help = (
        "Seed a large volume of low-effort job postings for index/cache/"
        "concurrency load testing. LOCAL ONLY — refuses to run if "
        "DATABASE_URL is set (Railway/production signal)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--count", type=int, default=25_000,
            help="Number of bulk postings to generate. Default 25,000.",
        )
        parser.add_argument(
            "--clear-existing", action="store_true",
            help="Delete previously generated bulk postings before seeding.",
        )
        parser.add_argument(
            "--batch-size", type=int, default=2000,
            help="bulk_create/bulk_update batch size. Default 2000.",
        )

    def handle(self, *args, **options):
        self._guard_against_production()

        count = options["count"]
        batch_size = options["batch_size"]

        if options["clear_existing"]:
            with transaction.atomic():
                deleted, _ = JobListing.objects.filter(
                    title__startswith=TITLE_MARKER
                ).delete()
            self.stdout.write(self.style.WARNING(f"Removed {deleted} prior bulk postings."))

        companies = list(CompanyProfile.objects.all())
        if not companies:
            raise CommandError(
                "No CompanyProfile rows found. Run seed_data or "
                "seed_realistic_jobs first to create companies."
            )
        categories = list(Category.objects.all())
        tags = list(Tag.objects.all())
        if not categories or not tags:
            raise CommandError(
                "No categories/tags found. Run seed_data or "
                "seed_realistic_jobs first."
            )

        self.stdout.write(f"Generating {count} bulk postings (batch_size={batch_size})...")

        created_count = 0
        now = timezone.now()

        for batch_start in range(0, count, batch_size):
            batch_n = min(batch_size, count - batch_start)
            jobs = self._build_batch(batch_n, companies, categories)

            with transaction.atomic():
                JobListing.objects.bulk_create(jobs, batch_size=batch_size)

                # Backdate posted_at realistically. bulk_update() does NOT
                # call pre_save(), so — unlike bulk_create() — it will
                # actually accept this value instead of overwriting it with
                # auto_now_add's "now".
                for job in jobs:
                    job.posted_at = now - timedelta(
                        days=random.randint(0, 180),
                        hours=random.randint(0, 23),
                    )
                JobListing.objects.bulk_update(
                    jobs, ["posted_at"], batch_size=batch_size
                )

                self._bulk_assign_tags(jobs, tags, batch_size)

            created_count += batch_n
            self.stdout.write(f"  ...{created_count}/{count}")

        self.stdout.write(self.style.SUCCESS(f"\n=== Bulk volume seed complete ==="))
        self.stdout.write(f"  Postings created: {created_count}")
        self.stdout.write(
            "  Reminder: this data is for local index/cache/load testing only. "
            "Do not deploy this command's output to Railway."
        )
        self.stdout.write(self.style.SUCCESS("===================================="))

    # ------------------------------------------------------------------ #

    def _guard_against_production(self):
        if os.environ.get("DATABASE_URL"):
            raise CommandError(
                "Refusing to run: DATABASE_URL is set, which this project's "
                "settings.py treats as the signal for Railway/production "
                "(see jobboard/settings.py — local dev uses discrete "
                "DB_HOST/DB_NAME/etc. instead). This command generates "
                "20k+ synthetic postings and must never run against a "
                "deployed database. If you are certain this is local, "
                "unset DATABASE_URL, or edit this guard directly — there "
                "is no override flag on purpose."
            )

    def _build_batch(self, n, companies, categories):
        jobs = []
        for _ in range(n):
            level = random.choice(LEVEL_PREFIXES)
            role = random.choice(ROLE_TITLES)
            title = f"{TITLE_MARKER} {level} {role}".strip()
            description = (
                f"{role} position. " + " ".join(
                    random.sample(DESCRIPTION_FILLERS, k=2)
                )
            )
            sal_base = random.randint(3_500_000, 9_000_000)

            jobs.append(JobListing(
                title=title,
                description=description,
                company=random.choice(companies),
                category=random.choice(categories),
                job_type=random.choice(JOB_TYPES),
                experience_level=random.choice(EXPERIENCE_LEVELS),
                location=random.choice(LOCATIONS),
                is_remote=random.random() < 0.25,
                salary_min=sal_base,
                salary_max=sal_base + random.randint(1_000_000, 4_000_000),
                is_active=random.random() < 0.85,
            ))
        return jobs

    def _bulk_assign_tags(self, jobs, tags, batch_size):
        """
        Inserts directly into the M2M through-table instead of looping
        `.tags.set()` per job. At 25k rows, a per-row .set() call would be
        25k+ individual queries; this is a handful of bulk_create calls.
        """
        ThroughModel = JobListing.tags.through
        through_rows = []
        for job in jobs:
            job_tags = random.sample(tags, k=random.randint(1, min(3, len(tags))))
            for tag in job_tags:
                through_rows.append(ThroughModel(joblisting=job, tag=tag))
        ThroughModel.objects.bulk_create(
            through_rows, batch_size=batch_size, ignore_conflicts=True
        )