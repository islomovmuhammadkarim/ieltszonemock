from django.db import models
from django.core.exceptions import ValidationError
from mocks.models import MockSection


class ReadingTest(models.Model):
    section = models.OneToOneField(
        MockSection,
        on_delete=models.CASCADE,
        related_name="reading_test",
        limit_choices_to={"section": "reading"},
    )
    title = models.CharField(max_length=120, blank=True)
    duration_seconds = models.PositiveIntegerField(default=3600)  # 60 min

    def __str__(self):
        return f"Reading — {self.section.mock.title}"


class ReadingPassage(models.Model):
    """
    IELTS'dagi Passage 1/2/3.
    Matn (paragraphlar) shu yerda.
    """
    test = models.ForeignKey(ReadingTest, on_delete=models.CASCADE, related_name="passages")
    order = models.PositiveSmallIntegerField()  # 1..3
    title = models.CharField(max_length=200, blank=True)

    # HTML yoki plain text saqlashingiz mumkin (siz frontend qilasiz)
    content = models.TextField(help_text="Passage text (you can store HTML here)")

    class Meta:
        unique_together = ("test", "order")
        ordering = ["order"]

    def __str__(self):
        return f"Passage {self.order} — {self.test}"


class ReadingQuestionGroup(models.Model):
    """
    Passage ichida blok: Headings, TFNG, Matching, Summary, MCQ, Gap-fill...
    """
    GROUP_TYPE = [
        ("none", "None"),
        ("tfng", "True/False/Not Given"),
        ("mcq", "Multiple choice"),
        ("mcq_multi", "Multiple choice (multiple)"),
        ("short", "Short answer / Gap fill"),
        ("headings", "Matching headings"),
        ("matching", "Matching (A–E / names / statements)"),
        ("summary", "Summary completion"),
    ]

    passage = models.ForeignKey(ReadingPassage, on_delete=models.CASCADE, related_name="groups")
    order = models.PositiveSmallIntegerField(default=1)  # passage ichida group tartibi
    title = models.CharField(max_length=200, blank=True)
    group_type = models.CharField(max_length=20, choices=GROUP_TYPE, default="none")
    instructions = models.CharField(max_length=255, blank=True)

    # Group config: headings list, people list, paragraph labels, etc.
    # examples:
    # headings: {"headings":["i ...","ii ..."], "paragraphs":["A","B","C","D"]}
    # matching: {"pool":["A","B","C","D","E"]}
    data = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ("passage", "order")
        ordering = ["order"]

    def __str__(self):
        name = self.title or self.get_group_type_display()
        return f"Group {self.order} — Passage {self.passage.order} — {name}"


class ReadingQuestion(models.Model):
    """
    Universal savol (IELTS reading uchun).
    """
    QTYPE = [
        ("tfng", "True/False/Not Given"),
        ("yesno", "Yes/No/Not Given"),
        ("mcq_single", "MCQ (single)"),
        ("mcq_multi", "MCQ (multiple)"),
        ("short", "Short answer / Gap fill"),
        ("heading", "Heading match (choose i-x)"),
        ("matching", "Matching (choose A-E / names / statements)"),
    ]

    test = models.ForeignKey(ReadingTest, on_delete=models.CASCADE, related_name="questions")
    passage = models.ForeignKey(ReadingPassage, on_delete=models.CASCADE, related_name="questions")
    group = models.ForeignKey(
        ReadingQuestionGroup,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="questions",
    )

    order = models.PositiveSmallIntegerField()  # 1..40 (IELTS reading 40 ta)
    passage_order = models.PositiveSmallIntegerField(default=1)  # 1..3 (UI uchun)
    qtype = models.CharField(max_length=20, choices=QTYPE)

    prompt = models.TextField()
    instructions = models.CharField(max_length=255, blank=True)

    # Question config:
    # short: {"max_words":2}
    # matching: {"pool":["A","B","C","D","E"]}
    data = models.JSONField(default=dict, blank=True)

    # Correct answer:
    # tfng: {"value":"True"}
    # short: {"values":["..."], "case_sensitive": false, "max_words": 2}
    # mcq_single: {"value":"B"}
    # mcq_multi: {"values":["A","C"]}
    # heading/matching: {"value":"iv"} or {"value":"C"}
    answer_key = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ("test", "order")
        ordering = ["order"]

    def clean(self):
        if self.passage_order not in (1, 2, 3):
            raise ValidationError("passage_order 1..3 bo'lsin.")

    def __str__(self):
        return f"Q{self.order} ({self.qtype})"


class ReadingOption(models.Model):
    """
    MCQ savollar uchun variantlar.
    """
    question = models.ForeignKey(ReadingQuestion, on_delete=models.CASCADE, related_name="options")
    key = models.CharField(max_length=10)  # A, B, C ... yoki i, ii...
    text = models.CharField(max_length=255)

    class Meta:
        unique_together = ("question", "key")
        ordering = ["key"]

    def __str__(self):
        return f"Q{self.question.order}:{self.key}"

from attempts.models import Attempt

class ReadingAttemptAnswer(models.Model):
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name="reading_answers")
    question = models.ForeignKey(ReadingQuestion, on_delete=models.CASCADE, related_name="attempt_answers")
    response = models.JSONField(default=dict, blank=True)  # {"value":...} or {"values":[...]} or {"text":...}
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("attempt", "question")
