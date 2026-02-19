from django.urls import path
from . import views

app_name = "notifications"

urlpatterns = [
    path("", views.notification_list, name="list"),
    path("open/<int:pk>/", views.open_notification, name="open"),
    path("read-all/", views.read_all, name="read_all"),
]
