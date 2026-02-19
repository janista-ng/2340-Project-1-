from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import Notification

@receiver(user_logged_in)
def create_login_notification(sender, request, user, **kwargs):
    ip = request.META.get("REMOTE_ADDR", "unknown IP")
    Notification.objects.create(
        recipient=user,
        notif_type="login",
        title="New login detected",
        body=f"Login from {ip}",
        url="/profile/",
    )
