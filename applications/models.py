from django.db import models

# Create your models here.


class Application(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        REVIEWING = "reviewing", "Reviewing"
        REJECTED = "rejected", "Rejected"
        ACCEPTED = "accepted", "Accepted"

    candidate = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="applications"
    )
    job = models.ForeignKey(
        "jobs.JobListing", on_delete=models.CASCADE, related_name="applications"
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    cover_letter = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # one candidate can only apply to a job once
        constraints = [
            models.UniqueConstraint(
                fields=["candidate", "job"], name="unique_application_per_candidate"
            )
        ]
        ordering = ["-applied_at"]

    def __str__(self):
        return f"{self.candidate.email} -> {self.job.title}"
