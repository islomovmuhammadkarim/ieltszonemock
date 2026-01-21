from django.contrib import admin
from .models import (
    ReadingTest, ReadingPassage, ReadingQuestionGroup,
    ReadingQuestion, ReadingOption
)

class ReadingOptionInline(admin.TabularInline):
    model = ReadingOption
    extra = 0

@admin.register(ReadingTest)
class ReadingTestAdmin(admin.ModelAdmin):
    list_display = ("section", "title", "duration_seconds")

@admin.register(ReadingPassage)
class ReadingPassageAdmin(admin.ModelAdmin):
    list_display = ("test", "order", "title")
    list_filter = ("test",)

@admin.register(ReadingQuestionGroup)
class ReadingQuestionGroupAdmin(admin.ModelAdmin):
    list_display = ("passage", "order", "group_type", "title")
    list_filter = ("group_type", "passage__test")

@admin.register(ReadingQuestion)
class ReadingQuestionAdmin(admin.ModelAdmin):
    list_display = ("test", "order", "passage_order", "qtype", "group")
    list_filter = ("qtype", "passage_order", "test")
    search_fields = ("prompt",)
    inlines = [ReadingOptionInline]
