from django.contrib import admin
from .models import HousePrediction, Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("name", "rating", "message", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("name", "message")
    ordering = ("-created_at",)


admin.site.register(HousePrediction)