from django.contrib import admin
from .models import (
    ListeningTest,
    ListeningQuestionGroup,
    ListeningQuestion,
    ListeningOption,
)


class ListeningOptionInline(admin.TabularInline):
    model = ListeningOption
    extra = 0


@admin.register(ListeningQuestion)
class ListeningQuestionAdmin(admin.ModelAdmin):
    list_display = ("test", "order", "part", "qtype", "group")
    list_filter = ("qtype", "part", "test")
    search_fields = ("prompt",)
    inlines = [ListeningOptionInline]
    fields = (
        "test",
        "group",
        "order",
        "part",
        "qtype",
        "prompt",
        "instructions",
        "data",
        "answer_key",
    )


@admin.register(ListeningQuestionGroup)
class ListeningQuestionGroupAdmin(admin.ModelAdmin):
    list_display = ("test", "order", "part", "group_type", "title")
    list_filter = ("group_type", "part", "test")
    search_fields = ("title", "instructions")
    fields = (
        "test",
        "order",
        "part",
        "group_type",
        "title",
        "instructions",
        "image",
        "data",
    )


@admin.register(ListeningTest)
class ListeningTestAdmin(admin.ModelAdmin):
    list_display = ("section", "title", "duration_seconds")
    list_filter = ("section__mock",)
