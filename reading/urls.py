from django.urls import path
from . import views

urlpatterns = [
    path("", views.reading_page, name="reading_page"),
    path("save-answer/", views.reading_save_answer, name="reading_save_answer"),
    path("submit/", views.reading_submit, name="reading_submit"),
    path("terminate/", views.reading_terminate, name="reading_terminate"),
]
