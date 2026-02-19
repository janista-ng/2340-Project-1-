from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from datetime import datetime

@login_required
def inbox(request):
    threads = [
        {"id": 1, "title": "Recruiter", "preview": "Hey! Are you still interested in the role?", "updated_at": datetime.now()},
        {"id": 2, "title": "Hiring Team", "preview": "Thanks for applying — can you interview Friday?", "updated_at": datetime.now()},
        {"id": 3, "title": "Follow-up", "preview": "Follow up about your application.", "updated_at": datetime.now()},
    ]
    return render(request, "messaging/inbox.html", {"threads": threads})

@login_required
def thread_detail(request, thread_id):
    threads = {
        1: {"title": "Recruiter"},
        2: {"title": "Hiring Team"},
        3: {"title": "Follow-up"},
    }

    demo_messages = {
        1: [
            {"side": "them", "text": "Hey! Are you still interested in the role?", "time": "Today"},
            {"side": "me", "text": "Yes! I’d love to learn more.", "time": "Today"},
        ],
        2: [
            {"side": "them", "text": "Thanks for applying — can you interview Friday?", "time": "Today"},
            {"side": "me", "text": "Friday works. What time?", "time": "Today"},
        ],
        3: [
            {"side": "them", "text": "Follow up about your application.", "time": "Today"},
        ],
    }

    if request.method == "POST":
        return redirect("messaging:thread", thread_id=thread_id)

    thread_title = threads.get(thread_id, {}).get("title", "Conversation")
    messages = demo_messages.get(thread_id, [])
    return render(request, "messaging/thread.html", {
        "thread_id": thread_id,
        "thread_title": thread_title,
        "chat_messages": messages,
    })
