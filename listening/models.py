from django.db import models
from django.core.exceptions import ValidationError
from mocks.models import MockSection


class ListeningTest(models.Model):
    """
    MockSection(listening) ga OneToOne ulangan: bitta audio + savollar.
    """
    section = models.OneToOneField(
        MockSection,
        on_delete=models.CASCADE,
        related_name="listening_test",
        limit_choices_to={"section": "listening"},
    )
    title = models.CharField(max_length=120, blank=True)
    audio = models.FileField(upload_to="listening_audio/")
    duration_seconds = models.PositiveIntegerField(default=1800)  # 30 min

    def __str__(self):
        return f"Listening — {self.section.mock.title}"


class ListeningQuestionGroup(models.Model):
    """
    Group: bitta blok (notes/form/table/map) + ichida ko'p savol.
    Masalan Q1–Q5 notes, Q6–Q10 TFNG, Q11–Q15 map...
    """
    GROUP_TYPE = [
        ("none", "None"),
        ("notes", "Notes/Form/Flow-chart (Gap-fill)"),
        ("tfng", "True/False/Not Given block"),
        ("table", "Table"),
        ("map", "Map/Plan/Diagram"),
        ("matching", "Matching block"),
        ("mcq", "MCQ block"),
    ]

    test = models.ForeignKey(ListeningTest, on_delete=models.CASCADE, related_name="groups")
    part = models.PositiveSmallIntegerField(default=1)  # 1..4 (UI uchun)
    order = models.PositiveSmallIntegerField(default=1)  # group tartibi (1..n)
    title = models.CharField(max_length=120, blank=True)
    group_type = models.CharField(max_length=20, choices=GROUP_TYPE, default="none")
    instructions = models.CharField(max_length=255, blank=True)

    # ✅ map/diagram uchun bitta rasm (ixtiyoriy)
    image = models.ImageField(upload_to="listening_images/", null=True, blank=True)

    # group config: labels, max_words default, etc.
    data = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ("test", "order")
        ordering = ["order"]

    def __str__(self):
        name = self.title or self.get_group_type_display()
        return f"Group {self.order} — Part {self.part} — {name}"

    def clean(self):
        if self.part not in (1, 2, 3, 4):
            raise ValidationError("part 1..4 bo'lishi kerak.")


class ListeningQuestion(models.Model):
    """
    Universal savol: turiga qarab options/answer_key ishlaydi.
    """
    TYPE = [
        ("short", "Short answer / Gap fill"),
        ("tfng", "True/False/Not Given"),
        ("mcq_single", "Multiple choice (single)"),
        ("mcq_multi", "Multiple choice (multiple)"),
        ("matching", "Matching (A–E)"),
        ("map", "Map/Plan label"),
    ]

    test = models.ForeignKey(ListeningTest, on_delete=models.CASCADE, related_name="questions")

    # ✅ Group bog'lash: Q1–Q5 bitta group, Q6–Q10 boshqa group
    group = models.ForeignKey(
        ListeningQuestionGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="questions",
        help_text="Agar savol block ichida bo'lsa, shu yerda group tanlang."
    )

    order = models.PositiveSmallIntegerField()  # 1..30
    part = models.PositiveSmallIntegerField(default=1)  # 1..4 (UI uchun)
    qtype = models.CharField(max_length=20, choices=TYPE)

    prompt = models.TextField()
    instructions = models.CharField(max_length=255, blank=True)

    # Question-specific config:
    # short: {"max_words": 2}
    # matching/map: {"pool": ["A","B","C","D"]}
    data = models.JSONField(default=dict, blank=True)

    # Correct answer universal JSON:
    # short: {"values":["johnson"], "case_sensitive": false, "max_words": 1}
    # tfng: {"value":"True"}
    # mcq_single: {"value":"B"}
    # mcq_multi: {"values":["A","C"]}
    # matching/map: {"value":"D"}
    answer_key = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ("test", "order")
        ordering = ["order"]

    def __str__(self):
        return f"Q{self.order} ({self.qtype})"

    def clean(self):
        if self.part not in (1, 2, 3, 4):
            raise ValidationError("part 1..4 bo'lishi kerak.")
        if self.order < 1:
            raise ValidationError("order 1 dan boshlansin.")
        # Optional: group part bilan question part mos bo'lsin
        if self.group and self.group.part != self.part:
            raise ValidationError("Savol part'i group part'iga mos bo'lishi kerak.")


class ListeningOption(models.Model):
    """
    MCQ uchun variantlar (A/B/C/D).
    """
    question = models.ForeignKey(ListeningQuestion, on_delete=models.CASCADE, related_name="options")
    key = models.CharField(max_length=8)  # A, B, C, D ...
    text = models.CharField(max_length=255)

    class Meta:
        unique_together = ("question", "key")
        ordering = ["key"]

    def __str__(self):
        return f"Q{self.question.order}:{self.key}"

from attempts.models import Attempt

class ListeningAttemptAnswer(models.Model):
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name="listening_answers")
    question = models.ForeignKey("ListeningQuestion", on_delete=models.CASCADE, related_name="attempt_answers")
    response = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("attempt", "question")

    def __str__(self):
        return f"Attempt {self.attempt_id} — Q{self.question.order}"
