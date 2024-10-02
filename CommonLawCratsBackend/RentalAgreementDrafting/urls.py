from django.urls import path
from . import views

urlpatterns = [
    # Define your URL patterns here
    path('home/', views.home, name='home')
]
