from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Thread, Message
from datetime import datetime
from django.http import HttpResponseForbidden

@login_required
def inbox(request):
    threads = (
        Thread.objects
        .filter(participants=request.user)
        .order_by("-updated_at")
        .prefetch_related("participants", "messages")
    )

    thread_cards = []
    for t in threads:
        other = t.participants.exclude(id=request.user.id).first()
        last = t.messages.last()
        thread_cards.append({
            "id": t.id,
            "title": other.username if other else "Conversation",
            "preview": last.body[:80] if last else "",
            "updated_at": t.updated_at,
        })

    return render(request, "messaging/inbox.html", {"threads": thread_cards})

@login_required
def thread_detail(request, thread_id):
    thread = get_object_or_404(Thread, pk=thread_id)

    if not thread.participants.filter(id=request.user.id).exists():
        return HttpResponseForbidden("Not allowed.")

    other_user = thread.participants.exclude(id=request.user.id).first()
    thread_title = other_user.username if other_user else "Conversation"

    if request.method == "POST":
        text = request.POST.get("body", "").strip()
        if text:
            Message.objects.create(thread=thread, sender=request.user, body=text)
        return redirect("messaging:thread", thread_id=thread.id)

    return render(request, "messaging/thread.html", {
        "thread": thread,
        "thread_id": thread.id,
        "thread_title": thread_title,
        "chat_messages": thread.messages.all(),
    })
@login_required
def start_thread(request, user_id):
    other = get_object_or_404(User, pk=user_id)
    if other == request.user:
        return redirect("messaging:inbox")

    existing = (
        Thread.objects
        .filter(participants=request.user)
        .filter(participants=other)
        .distinct()
        .first()
    )
    if existing:
        return redirect("messaging:thread", thread_id=existing.id)

    thread = Thread.objects.create()
    thread.participants.add(request.user, other)
    thread.save()

    return redirect("messaging:thread", thread_id=thread.id)