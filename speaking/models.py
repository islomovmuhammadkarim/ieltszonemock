from django.db import models
from mocks.models import MockSection

class SpeakingTest(models.Model):
    section = models.OneToOneField(
        MockSection,
        on_delete=models.CASCADE,
        related_name="speaking_test",
        limit_choices_to={"section": "speaking"},
    )
    title = models.CharField(max_length=120, blank=True)

class SpeakingPart(models.Model):
    test = models.ForeignKey(SpeakingTest, on_delete=models.CASCADE, related_name="parts")
    part_number = models.PositiveSmallIntegerField()  # 1/2/3
    prompt = models.TextField()
    time_limit_seconds = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["part_number"]
