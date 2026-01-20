from django.db import models
from mocks.models import MockSection

class ListeningTest(models.Model):
    section = models.OneToOneField(
        MockSection,
        on_delete=models.CASCADE,
        related_name="listening_test",
        limit_choices_to={"section": "listening"},
    )
    audio = models.FileField(upload_to="listening_audio/")
    title = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return f"Listening — {self.section.mock.title}"


class ListeningQuestion(models.Model):
    test = models.ForeignKey(ListeningTest, on_delete=models.CASCADE, related_name="questions")
    order = models.PositiveIntegerField()
    question_text = models.CharField(max_length=255)

    option_a = models.CharField(max_length=120)
    option_b = models.CharField(max_length=120)
    option_c = models.CharField(max_length=120)

    correct_answer = models.CharField(max_length=1)  # A/B/C

    class Meta:
        ordering = ["order"]
