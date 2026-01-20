from django.db import models
from mocks.models import MockSection

class WritingTest(models.Model):
    section = models.OneToOneField(
        MockSection,
        on_delete=models.CASCADE,
        related_name="writing_test",
        limit_choices_to={"section": "writing"},
    )
    title = models.CharField(max_length=120, blank=True)

class WritingTask(models.Model):
    test = models.ForeignKey(WritingTest, on_delete=models.CASCADE, related_name="tasks")
    task_number = models.PositiveSmallIntegerField()  # 1 or 2
    prompt = models.TextField()
    min_words = models.PositiveIntegerField(default=150)

    class Meta:
        unique_together = ("test", "task_number")
        ordering = ["task_number"]
