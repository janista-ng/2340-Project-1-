from django.conf import settings
from django.db import models
from django.utils import timezone

class Notification(models.Model):
    TYPE_CHOICES = [
        ("message", "Message"),
        ("recommendation", "Recommendation"),
        ("login", "Login"),
        ("saved_search", "Saved Search"),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    notif_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=120)
    body = models.CharField(max_length=255, blank=True)
    url = models.CharField(max_length=255, blank=True)  # internal path like "/messages/t/3/"

    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    def mark_read(self):
        if not self.read_at:
            self.read_at = timezone.now()
            self.save(update_fields=["read_at"])

    @property
    def is_read(self):
        return self.read_at is not None

    class Meta:
        ordering = ["-created_at"]
