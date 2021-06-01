from django.urls import path

from . import views

app_name = "recommender"

urlpatterns = [
    path("", views.home, name="home"),
    path("recommender", views.recommender, name="recommender"),
    path("auto_complete", views.auto_complete, name="auto_complete"),
]
