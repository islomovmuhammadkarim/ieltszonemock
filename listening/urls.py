from django.urls import path
from . import views

urlpatterns = [
    path("", views.listening_page, name="listening_page"),
    path("save-answer/", views.listening_save_answer, name="listening_save_answer"),
    path("submit/", views.listening_submit, name="listening_submit"),
    path("terminate/", views.listening_terminate, name="listening_terminate"),
]
