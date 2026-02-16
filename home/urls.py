from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='home.index'),
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/", views.profile_view, name="profile"),
]