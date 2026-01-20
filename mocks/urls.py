from django.urls import path
from . import views

urlpatterns = [
    path("", views.mock_list, name="mock_list"),
    path("<slug:slug>/", views.mock_detail, name="mock_detail"),
    path("<slug:slug>/start/", views.mock_start, name="mock_start"),
]
