from django.db import models

class Mock(models.Model):
    title = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True)
    is_active = models.BooleanField(default=True)

    estimated_minutes = models.PositiveIntegerField(default=165)

    def __str__(self):
        return self.title


class MockSection(models.Model):
    SECTION_CHOICES = [
        ("listening", "Listening"),
        ("reading", "Reading"),
        ("writing", "Writing"),
        ("speaking", "Speaking"),
    ]

    mock = models.ForeignKey(Mock, on_delete=models.CASCADE, related_name="sections")
    section = models.CharField(max_length=20, choices=SECTION_CHOICES)
    order = models.PositiveSmallIntegerField()          # 1..4
    duration_seconds = models.PositiveIntegerField()    # masalan Listening 2400

    class Meta:
        unique_together = ("mock", "section")
        ordering = ["order"]

    def __str__(self):
        return f"{self.mock.title} — {self.section}"
