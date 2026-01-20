from django.db import models
from django.utils import timezone
from mocks.models import Mock

class Attempt(models.Model):
    STATUS = [
        ("in_progress", "In Progress"),
        ("submitted", "Submitted"),
        ("terminated", "Terminated"),
    ]

    mock = models.ForeignKey(Mock, on_delete=models.PROTECT, related_name="attempts")
    status = models.CharField(max_length=20, choices=STATUS, default="in_progress")
    current_section = models.CharField(max_length=20, default="listening")  # flow uchun

    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    def terminate(self):
        if self.status == "in_progress":
            self.status = "terminated"
            self.finished_at = timezone.now()
            self.save(update_fields=["status", "finished_at"])
