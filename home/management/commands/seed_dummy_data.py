"""
Management command to populate the database with dummy data for testing.
Usage: python manage.py seed_dummy_data

Requires cities_light data: python manage.py cities_light
"""
import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from home.models import Profile
from jobs.models import Job, Application
from messaging.models import Thread, Message
from notifications.models import Notification


def _get_random_us_city():
    """Return a random US city from cities_light with lat/long, or None if no data."""
    try:
        from cities_light.models import City
        cities = list(City.objects.filter(country__code2='US').exclude(
            latitude__isnull=True
        ).exclude(
            longitude__isnull=True
        ).order_by('?')[:1])
        return cities[0] if cities else None
    except Exception:
        return None


# Dummy data constants
COMPANIES = [
    "TechCorp", "DataDriven Inc", "CloudNine", "Nexus Labs", "CodeForge",
    "InnovateSoft", "ByteWorks", "DevHub", "StartupXYZ", "FutureTech",
    "Alpha Systems", "Beta Solutions", "Gamma Corp", "Delta Digital", "Epsilon Labs",
]

JOB_TITLES = [
    "Software Engineer", "Backend Developer", "Frontend Developer", "Full Stack Engineer",
    "Data Scientist", "Machine Learning Engineer", "DevOps Engineer", "Product Manager",
    "UX Designer", "QA Engineer", "Security Analyst", "Cloud Architect",
    "Junior Developer", "Senior Software Engineer", "Engineering Intern",
]

SKILLS_POOL = [
    "Python", "Java", "JavaScript", "React", "Django", "Node.js", "SQL", "AWS",
    "Docker", "Kubernetes", "Git", "REST APIs", "TypeScript", "PostgreSQL",
    "MongoDB", "Redis", "GraphQL", "CI/CD", "Linux", "Agile",
]

LOCATIONS = [
    "Atlanta, GA", "New York, NY", "San Francisco, CA", "Austin, TX", "Seattle, WA",
    "Boston, MA", "Chicago, IL", "Denver, CO", "Los Angeles, CA", "Miami, FL",
    "Philadelphia, PA", "Phoenix, AZ", "Portland, OR", "Washington, DC",
]

FIRST_NAMES = [
    "Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Avery", "Quinn",
    "Sam", "Jamie", "Drew", "Blake", "Cameron", "Skyler", "Parker",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore",
]

HEADLINES = [
    "CS grad seeking SWE role", "Full-stack developer | React & Python",
    "Aspiring ML engineer", "Backend specialist | APIs & databases",
    "Frontend enthusiast | Clean UI", "DevOps & cloud infrastructure",
]

EDUCATION_SAMPLES = [
    "Georgia Tech — BS Computer Science (2025)",
    "MIT — MS Data Science (2024)",
    "Stanford — BS Software Engineering (2026)",
    "UC Berkeley — BA Computer Science (2025)",
]

WORK_SAMPLES = [
    "Software Intern — BigTech (Summer 2024)\n- Built REST APIs\n- Wrote unit tests",
    "Dev Intern — StartupCo (2023)\n- Frontend development\n- Bug fixes",
]


class Command(BaseCommand):
    help = "Populate database with dummy users, jobs, applications, messages, and notifications"

    def add_arguments(self, parser):
        parser.add_argument(
            "--seekers", type=int, default=25,
            help="Number of job seeker users to create",
        )
        parser.add_argument(
            "--recruiters", type=int, default=8,
            help="Number of recruiter users to create",
        )
        parser.add_argument(
            "--jobs", type=int, default=40,
            help="Number of jobs to create",
        )
        parser.add_argument(
            "--clear", action="store_true",
            help="Clear existing data before seeding (keeps superuser)",
        )

    def handle(self, *args, **options):
        n_seekers = options["seekers"]
        n_recruiters = options["recruiters"]
        n_jobs = options["jobs"]
        clear_first = options["clear"]

        if clear_first:
            self._clear_data()

        self.stdout.write("Creating users and profiles...")
        seekers = self._create_seekers(n_seekers)
        recruiters = self._create_recruiters(n_recruiters)

        self.stdout.write("Creating jobs...")
        jobs = self._create_jobs(recruiters, n_jobs)

        self.stdout.write("Creating applications...")
        self._create_applications(seekers, jobs)

        self.stdout.write("Creating messages and notifications...")
        self._create_messages(seekers, recruiters)
        self._create_notifications(seekers, recruiters)

        self.stdout.write(self.style.SUCCESS(
            f"Done! Created {len(seekers)} seekers, {len(recruiters)} recruiters, "
            f"{len(jobs)} jobs, plus applications, messages, and notifications."
        ))
        self.stdout.write("\nTest accounts (password: testpass123):")
        if seekers:
            self.stdout.write(f"  Seeker: {seekers[0].user.username}")
        if recruiters:
            self.stdout.write(f"  Recruiter: {recruiters[0].user.username}")

    def _clear_data(self):
        Notification.objects.all().delete()
        Message.objects.all().delete()
        Thread.objects.all().delete()
        Application.objects.all().delete()
        Job.objects.all().delete()
        Profile.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write("Cleared existing data.")

    def _random_skills(self, count=5):
        return ", ".join(random.sample(SKILLS_POOL, min(count, len(SKILLS_POOL))))

    def _create_seekers(self, n):
        created = []
        for i in range(n):
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            username = f"seeker_{first.lower()}{last.lower()}_{i}"
            if User.objects.filter(username=username).exists():
                continue
            user = User.objects.create_user(
                username=username,
                email=f"{username}@example.com",
                password="testpass123",
                first_name=first,
                last_name=last,
            )
            city_obj = _get_random_us_city()
            if city_obj:
                loc = f"{city_obj.name}, {city_obj.region.geoname_code or city_obj.region.name}" if city_obj.region else city_obj.name
                profile = Profile.objects.create(
                    user=user,
                    role="job_seeker",
                    display_name=f"{first} {last}",
                    headline=random.choice(HEADLINES),
                    city=city_obj.name,
                    state=city_obj.region.geoname_code or (city_obj.region.name if city_obj.region else ""),
                    location=loc,
                    latitude=city_obj.latitude,
                    longitude=city_obj.longitude,
                    skills=self._random_skills(random.randint(3, 7)),
                    education=random.choice(EDUCATION_SAMPLES),
                    work_experience=random.choice(WORK_SAMPLES),
                    about_me="Passionate about software development and eager to learn.",
                    contact_email=f"{username}@example.com",
                )
            else:
                loc = random.choice(LOCATIONS)
                profile = Profile.objects.create(
                    user=user,
                    role="job_seeker",
                    display_name=f"{first} {last}",
                    headline=random.choice(HEADLINES),
                    location=loc,
                    skills=self._random_skills(random.randint(3, 7)),
                    education=random.choice(EDUCATION_SAMPLES),
                    work_experience=random.choice(WORK_SAMPLES),
                    about_me="Passionate about software development and eager to learn.",
                    contact_email=f"{username}@example.com",
                )
            created.append(profile)
        return created

    def _create_recruiters(self, n):
        created = []
        for i in range(n):
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            username = f"recruiter_{first.lower()}{last.lower()}_{i}"
            if User.objects.filter(username=username).exists():
                continue
            user = User.objects.create_user(
                username=username,
                email=f"{username}@example.com",
                password="testpass123",
                first_name=first,
                last_name=last,
            )
            city_obj = _get_random_us_city()
            if city_obj:
                loc = f"{city_obj.name}, {city_obj.region.geoname_code or city_obj.region.name}" if city_obj.region else city_obj.name
                Profile.objects.create(
                    user=user,
                    role="recruiter",
                    display_name=f"{first} {last}",
                    headline=f"Talent Acquisition at {random.choice(COMPANIES)}",
                    city=city_obj.name,
                    state=city_obj.region.geoname_code or (city_obj.region.name if city_obj.region else ""),
                    location=loc,
                    latitude=city_obj.latitude,
                    longitude=city_obj.longitude,
                    about_me="Hiring great talent for our team.",
                )
            else:
                Profile.objects.create(
                    user=user,
                    role="recruiter",
                    display_name=f"{first} {last}",
                    headline=f"Talent Acquisition at {random.choice(COMPANIES)}",
                    location=random.choice(LOCATIONS),
                    about_me="Hiring great talent for our team.",
                )
            created.append(Profile.objects.get(user=user))
        return created

    def _create_jobs(self, recruiters, n):
        if not recruiters:
            return []
        created = []
        for i in range(n):
            recruiter = random.choice(recruiters).user
            company = random.choice(COMPANIES)
            title = random.choice(JOB_TITLES)
            city_obj = _get_random_us_city()
            if city_obj:
                loc = f"{city_obj.name}, {city_obj.region.geoname_code or city_obj.region.name}" if city_obj.region else city_obj.name
                job = Job.objects.create(
                    title=title,
                    company=company,
                    recruiter=recruiter,
                    description=f"We are looking for a talented {title} to join our team at {company}. "
                                f"Great benefits and growth opportunities.",
                    skills=self._random_skills(random.randint(3, 6)),
                    salary=random.choice([60000, 75000, 85000, 95000, 110000, 125000, 140000, None]),
                    city=city_obj.name,
                    state=city_obj.region.geoname_code or (city_obj.region.name if city_obj.region else ""),
                    location=loc,
                    latitude=city_obj.latitude,
                    longitude=city_obj.longitude,
                    remote=random.choice(["remote", "on_site", "hybrid"]),
                    visa_sponsorship=random.choice(["yes", "no"]),
                    is_active=True,
                )
            else:
                loc = random.choice(LOCATIONS)
                parts = loc.split(", ")
                city = parts[0] if parts else ""
                state = parts[1] if len(parts) > 1 else ""
                job = Job.objects.create(
                    title=title,
                    company=company,
                    recruiter=recruiter,
                    description=f"We are looking for a talented {title} to join our team at {company}. "
                                f"Great benefits and growth opportunities.",
                    skills=self._random_skills(random.randint(3, 6)),
                    salary=random.choice([60000, 75000, 85000, 95000, 110000, 125000, 140000, None]),
                    city=city,
                    state=state,
                    location=loc,
                    remote=random.choice(["remote", "on_site", "hybrid"]),
                    visa_sponsorship=random.choice(["yes", "no"]),
                    is_active=True,
                )
            created.append(job)
        return created

    def _create_applications(self, seekers, jobs):
        app_statuses = ["applied", "review", "interview", "offer", "closed"]
        for _ in range(min(120, len(seekers) * len(jobs) // 3)):
            seeker = random.choice(seekers).user
            job = random.choice(jobs)
            if Application.objects.filter(applicant=seeker, job=job).exists():
                continue
            Application.objects.create(
                applicant=seeker,
                job=job,
                cover_note=random.choice([
                    "I'm very interested in this role!",
                    "My experience aligns well with your requirements.",
                    "Excited to apply. Looking forward to hearing from you.",
                    "",
                ]),
                status=random.choice(app_statuses),
            )

    def _create_messages(self, seekers, recruiters):
        for _ in range(30):
            seeker = random.choice(seekers).user
            recruiter = random.choice(recruiters).user
            thread = Thread.objects.create()
            thread.participants.add(seeker, recruiter)
            for j in range(random.randint(2, 6)):
                sender = seeker if j % 2 == 0 else recruiter
                Message.objects.create(
                    thread=thread,
                    sender=sender,
                    body=random.choice([
                        "Thanks for reaching out! I'd love to learn more.",
                        "When would be a good time to chat?",
                        "I've applied to the role. Looking forward to hearing back.",
                        "Can we schedule a call this week?",
                    ]),
                )

    def _create_notifications(self, seekers, recruiters):
        all_users = [s.user for s in seekers] + [r.user for r in recruiters]
        for _ in range(50):
            user = random.choice(all_users)
            ntype = random.choice(["message", "recommendation", "login"])
            Notification.objects.create(
                recipient=user,
                notif_type=ntype,
                title=random.choice([
                    "New message", "Job recommendation", "Welcome back",
                    "Application update", "New match",
                ]),
                body="You have a new notification.",
                url=random.choice(["/jobs/", "/messages/", "/recommendations/", ""]),
            )
