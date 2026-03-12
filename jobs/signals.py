from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Application, SavedCandidateSearch
from notifications.models import Notification


@receiver(post_save, sender=Application)
def notify_saved_search_matches(sender, instance, created, **kwargs):
    if not created:
        return

    searches = SavedCandidateSearch.objects.filter(
        recruiter=instance.job.recruiter,
        job=instance.job,
        notify_on_new_matches=True,
    )

    for search in searches:
        if not search.matches_application(instance):
            continue

        Notification.objects.create(
            recipient=search.recruiter,
            notif_type="saved_search",
            title=f"New match for saved search: {search.name}",
            body=f"{instance.applicant.username} matched your saved search for {instance.job.title}.",
            url=f"/jobs/{instance.job.pk}/applications/?{search.querystring()}",
        )