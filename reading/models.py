from django.db import models
from mocks.models import MockSection

class ReadingTest(models.Model):
    section = models.OneToOneField(
        MockSection,
        on_delete=models.CASCADE,
        related_name="reading_test",
        limit_choices_to={"section": "reading"},
    )
    title = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return f"Reading — {self.section.mock.title}"
