from django.contrib import admin
from .models import Mock, MockSection, MockAccess


class MockSectionInline(admin.TabularInline):
    model = MockSection
    extra = 0


@admin.register(Mock)
class MockAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_active", "is_free", "price_uzs", "estimated_minutes")
    list_filter = ("is_active", "is_free")
    search_fields = ("title",)
    prepopulated_fields = {"slug": ("title",)}
    inlines = [MockSectionInline]


@admin.register(MockAccess)
class MockAccessAdmin(admin.ModelAdmin):
    list_display = ("user", "mock", "granted_at", "expires_at")
    list_filter = ("mock",)
