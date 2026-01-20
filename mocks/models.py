from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Mock(models.Model):
    title = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.CharField(max_length=255, blank=True)

    is_active = models.BooleanField(default=True)
    is_free = models.BooleanField(default=False)
    price_uzs = models.PositiveIntegerField(default=0)
    estimated_minutes = models.PositiveIntegerField(default=165)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

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
    order = models.PositiveSmallIntegerField()
    duration_seconds = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("mock", "section")
        ordering = ["order"]

    def __str__(self):
        return f"{self.mock.title} — {self.section}"


class MockAccess(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mock_access")
    mock = models.ForeignKey(Mock, on_delete=models.CASCADE, related_name="access_list")

    granted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "mock")

    def __str__(self):
        return f"{self.user} -> {self.mock}"
