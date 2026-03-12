from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.db.models import Count
from .models import Thread, Message


@login_required
def inbox(request):
    threads = (
        Thread.objects
        .filter(participants=request.user)
        .prefetch_related("participants", "messages")
        .order_by("-updated_at")
    )

    thread_cards = []
    for thread in threads:
        other = thread.participants.exclude(id=request.user.id).first()
        thread_messages = list(thread.messages.all())
        last_message = thread_messages[-1] if thread_messages else None

        thread_cards.append({
            "id": thread.id,
            "title": other.username if other else "Conversation",
            "preview": last_message.body[:80] if last_message else "Click to open conversation",
            "updated_at": last_message.created_at if last_message else thread.updated_at,
        })

    return render(request, "messaging/inbox.html", {"threads": thread_cards})


@login_required
def thread_detail(request, thread_id):
    thread = get_object_or_404(
        Thread.objects.prefetch_related("participants", "messages__sender"),
        pk=thread_id,
    )

    if not thread.participants.filter(id=request.user.id).exists():
        return HttpResponseForbidden("Not allowed.")

    other_user = thread.participants.exclude(id=request.user.id).first()
    thread_title = other_user.username if other_user else "Conversation"

    if request.method == "POST":
        text = request.POST.get("body", "").strip()
        if text:
            Message.objects.create(thread=thread, sender=request.user, body=text)
            thread.save(update_fields=["updated_at"])
        return redirect("messaging:thread", thread_id=thread.id)

    return render(request, "messaging/thread.html", {
        "thread": thread,
        "thread_id": thread.id,
        "thread_title": thread_title,
        "chat_messages": thread.messages.select_related("sender").all(),
        "current_user_id": request.user.id,
    })


@login_required
def start_thread(request, user_id):
    other = get_object_or_404(User, pk=user_id)

    if other == request.user:
        return redirect("messaging:inbox")

    existing = (
        Thread.objects
        .annotate(num_participants=Count("participants"))
        .filter(num_participants=2, participants=request.user)
        .filter(participants=other)
        .first()
    )

    if existing:
        return redirect("messaging:thread", thread_id=existing.id)

    thread = Thread.objects.create()
    thread.participants.add(request.user, other)

    return redirect("messaging:thread", thread_id=thread.id)