from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='home.index'),
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("privacy/", views.privacy_view, name="privacy"),
    path("profiles/<int:user_id>/", views.public_profile_view, name="public_profile"),
    path("load-more-jobs/", views.load_more_jobs, name="load_more_jobs"),
]