from django.urls import path
from .views import faq, index

urlpatterns = [
    path('', index, name='home'),
    path('faq/', faq, name='faq'),
]
