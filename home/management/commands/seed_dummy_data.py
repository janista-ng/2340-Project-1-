"""
Management command to populate the database with dummy data for testing.
Usage: python manage.py seed_dummy_data --clear

Mirrors the job form flow: State → City (from cities_light) → pin offset for lat/lng.
Requires: python manage.py cities_light
"""
import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from home.models import Profile
from jobs.models import Job, Application
from messaging.models import Thread, Message
from notifications.models import Notification


# (city_name, state_code) — matches cities_light. Use state to disambiguate (Austin TX not MN).
POPULAR_CITIES_LOOKUP = [
    ("San Francisco", "CA"), ("New York City", "NY"), ("Seattle", "WA"), ("Austin", "TX"), ("Boston", "MA"),
    ("Chicago", "IL"), ("Denver", "CO"), ("Los Angeles", "CA"), ("San Diego", "CA"), ("Atlanta", "GA"),
    ("Miami", "FL"), ("Philadelphia", "PA"), ("Phoenix", "AZ"), ("Portland", "OR"), ("Washington", "DC"),
    ("Dallas", "TX"), ("Houston", "TX"), ("Nashville", "TN"), ("Raleigh", "NC"), ("Minneapolis", "MN"),
    ("Salt Lake City", "UT"), ("Charlotte", "NC"), ("San Jose", "CA"), ("Columbus", "OH"), ("Tampa", "FL"),
]
# Weights: top 10 = 6, next 8 = 2, rest = 1 — jobs cluster in major hubs
CITY_WEIGHTS = [6] * 10 + [2] * 8 + [1] * 7

# Fallback when cities_light not populated: (name, state_code, lat, lng)
FALLBACK_CITIES = [
    ("San Francisco", "CA", 37.7749, -122.4194),
    ("New York", "NY", 40.7128, -74.0060),
    ("Seattle", "WA", 47.6062, -122.3321),
    ("Austin", "TX", 30.2672, -97.7431),
    ("Boston", "MA", 42.3601, -71.0589),
    ("Chicago", "IL", 41.8781, -87.6298),
    ("Denver", "CO", 39.7392, -104.9903),
    ("Los Angeles", "CA", 34.0522, -118.2437),
    ("San Diego", "CA", 32.7157, -117.1611),
    ("Atlanta", "GA", 33.7490, -84.3880),
    ("Miami", "FL", 25.7617, -80.1918),
    ("Philadelphia", "PA", 39.9526, -75.1652),
    ("Phoenix", "AZ", 33.4484, -112.0740),
    ("Portland", "OR", 45.5152, -122.6784),
    ("Washington", "DC", 38.9072, -77.0369),
    ("Dallas", "TX", 32.7767, -96.7970),
    ("Houston", "TX", 29.7604, -95.3698),
    ("Nashville", "TN", 36.1627, -86.7816),
    ("Raleigh", "NC", 35.7796, -78.6382),
    ("Minneapolis", "MN", 44.9778, -93.2650),
    ("Salt Lake City", "UT", 40.7608, -111.8910),
    ("Charlotte", "NC", 35.2271, -80.8431),
    ("San Jose", "CA", 37.3382, -121.8863),
    ("Columbus", "OH", 39.9612, -82.9988),
    ("Tampa", "FL", 27.9506, -82.4572),
]

# Pin offset: random from city center, up to ~5 miles (~0.073 deg at US latitudes)
LOCATION_OFFSET_DEG = 0.073


def _get_cities_from_cities_light():
    """Load popular US cities from cities_light (same source as job form). Cached. Uses (name, state) to disambiguate."""
    if not hasattr(_get_cities_from_cities_light, "_cache"):
        try:
            from cities_light.models import City
            cities = []
            for name, state in POPULAR_CITIES_LOOKUP:
                c = City.objects.filter(
                    country__code2='US',
                    name__iexact=name,
                    region__geoname_code__iexact=state
                ).exclude(latitude__isnull=True).exclude(longitude__isnull=True).select_related('region').first()
                if c:
                    cities.append(c)
            _get_cities_from_cities_light._cache = cities if cities else None
        except Exception:
            _get_cities_from_cities_light._cache = None
    return _get_cities_from_cities_light._cache


def _pick_location(weights=None, for_jobs=False):
    """
    Pick city + lat/lng. Mirrors form flow: State → City (cities_light) → pin offset.
    Uses cities_light when available (same source as job form); else fallback.
    Applies pin-style offset so markers spread within city.
    Returns (city_name, state_code, lat, lng).
    """
    cities_light = _get_cities_from_cities_light()
    if cities_light:
        if for_jobs and weights:
            # Build weighted list: match by (name, state), use CITY_WEIGHTS
            pairs = []
            for c in cities_light:
                state = c.region.geoname_code or "" if c.region else ""
                try:
                    idx = next(i for i, (n, s) in enumerate(POPULAR_CITIES_LOOKUP) if n == c.name and s == state)
                    w = weights[min(idx, len(weights) - 1)]
                except (StopIteration, IndexError):
                    w = 1
                pairs.append((c, w))
            chosen = random.choices([p[0] for p in pairs], weights=[p[1] for p in pairs], k=1)[0]
        else:
            chosen = random.choice(cities_light)
        lat, lng = float(chosen.latitude), float(chosen.longitude)
        state = chosen.region.geoname_code or (chosen.region.name if chosen.region else "")
        city_name, state_code = chosen.name, state
    else:
        w = weights if for_jobs and weights else [1] * len(FALLBACK_CITIES)
        idx = random.choices(range(len(FALLBACK_CITIES)), weights=w[:len(FALLBACK_CITIES)], k=1)[0]
        city_name, state_code, lat, lng = FALLBACK_CITIES[idx]
    lat, lng = _apply_offset(lat, lng)
    return city_name, state_code, lat, lng


def _apply_offset(lat, lng, offset_deg=LOCATION_OFFSET_DEG):
    """Simulate pin drag: random offset from city center, up to ~5 miles."""
    lat += random.uniform(-offset_deg, offset_deg)
    lng += random.uniform(-offset_deg, offset_deg)
    return round(lat, 6), round(lng, 6)


# Dummy data constants
COMPANIES = [
    "TechCorp", "DataDriven Inc", "CloudNine", "Nexus Labs", "CodeForge",
    "InnovateSoft", "ByteWorks", "DevHub", "StartupXYZ", "FutureTech",
    "Alpha Systems", "Beta Solutions", "Gamma Corp", "Delta Digital", "Epsilon Labs",
    "Stripe", "Square", "Notion", "Figma", "Linear", "Vercel", "Supabase",
    "Mercury Bank", "Plaid", "Brex", "Ramp", "Gusto", "Deel", "Remote",
]

JOB_TITLES = [
    "Software Engineer", "Backend Developer", "Frontend Developer", "Full Stack Engineer",
    "Data Scientist", "Machine Learning Engineer", "DevOps Engineer", "Product Manager",
    "UX Designer", "QA Engineer", "Security Analyst", "Cloud Architect",
    "Junior Developer", "Senior Software Engineer", "Engineering Intern",
    "iOS Developer", "Android Developer", "Site Reliability Engineer", "Data Engineer",
    "Technical Lead", "Solutions Architect", "Platform Engineer", "MLOps Engineer",
]

SKILLS_POOL = [
    "Python", "Java", "JavaScript", "React", "Django", "Node.js", "SQL", "AWS",
    "Docker", "Kubernetes", "Git", "REST APIs", "TypeScript", "PostgreSQL",
    "MongoDB", "Redis", "GraphQL", "CI/CD", "Linux", "Agile", "Scrum",
    "FastAPI", "Vue.js", "React Native", "Swift", "Kotlin", "Go", "Rust",
    "TensorFlow", "PyTorch", "Pandas", "Spark", "Terraform", "Ansible",
]

FIRST_NAMES = [
    "Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Avery", "Quinn",
    "Sam", "Jamie", "Drew", "Blake", "Cameron", "Skyler", "Parker",
    "Emma", "Noah", "Olivia", "Liam", "Sophia", "Mason", "Isabella", "Ethan",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore",
    "Jackson", "Clark", "Lewis", "Walker", "Hall", "Allen", "Young", "King",
]

HEADLINES = [
    "CS grad seeking SWE role", "Full-stack developer | React & Python",
    "Aspiring ML engineer", "Backend specialist | APIs & databases",
    "Frontend enthusiast | Clean UI", "DevOps & cloud infrastructure",
    "Senior engineer | 5+ years in fintech", "New grad | Georgia Tech 2025",
    "Full-stack | React, Node, PostgreSQL", "Data engineer | Python & Spark",
    "Mobile developer | iOS & Android", "Security-focused backend engineer",
]

EDUCATION_SAMPLES = [
    "Georgia Tech — BS Computer Science (2025)",
    "MIT — MS Data Science (2024)",
    "Stanford — BS Software Engineering (2026)",
    "UC Berkeley — BA Computer Science (2025)",
    "Carnegie Mellon — MS Software Engineering (2024)",
    "University of Washington — BS Computer Science (2025)",
    "UT Austin — BS Computer Science (2026)",
    "Northwestern — MS Data Science (2024)",
    "Duke — BS Computer Science (2025)",
]

WORK_SAMPLES = [
    "Software Intern — BigTech (Summer 2024)\n- Built REST APIs\n- Wrote unit tests",
    "Dev Intern — StartupCo (2023)\n- Frontend development\n- Bug fixes",
    "Software Engineer — Mid-size SaaS (2022–present)\n- Led migration to microservices\n- Mentored 2 interns",
    "Backend Engineer — Fintech startup (2021–2023)\n- Designed payment APIs\n- Implemented caching layer",
    "Data Science Intern — Fortune 500 (Summer 2023)\n- Built ML pipelines\n- A/B testing framework",
]

JOB_DESCRIPTIONS = [
    "We are looking for a talented {title} to join our team at {company}. "
    "You'll work on scalable systems, collaborate with cross-functional teams, and help shape our product. "
    "Great benefits, remote-friendly options, and growth opportunities.",
    "Join {company} as a {title} and help us build the future. "
    "We value ownership, curiosity, and strong engineering practices. "
    "Competitive salary, equity, and comprehensive health benefits.",
    "{company} is hiring a {title} to join our growing engineering team. "
    "You'll work on challenging problems, ship features that matter, and learn from talented peers. "
    "Flexible remote work and professional development budget.",
    "We're seeking a {title} to help scale our platform at {company}. "
    "You'll design APIs, improve performance, and contribute to our engineering culture. "
    "401k match, unlimited PTO, and wellness stipend.",
]

COVER_NOTES = [
    "I'm very interested in this role! My experience with {skills} aligns well with your requirements.",
    "Excited to apply. I've been working with similar technologies and would love to contribute to your team.",
    "I'm a strong fit for this position — my background in {skills} matches what you're looking for.",
    "Looking forward to the opportunity. I'd love to discuss how I can add value to {company}.",
    "I've applied to similar roles and believe my skills would be a great match. Happy to chat anytime.",
]


class Command(BaseCommand):
    help = "Populate database with dummy users, jobs, applications, messages, and notifications"

    def add_arguments(self, parser):
        parser.add_argument(
            "--seekers", type=int, default=150,
            help="Number of job seeker users to create",
        )
        parser.add_argument(
            "--recruiters", type=int, default=40,
            help="Number of recruiter users to create",
        )
        parser.add_argument(
            "--jobs", type=int, default=800,
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
            city_name, state_code, lat, lng = _pick_location()
            loc = f"{city_name}, {state_code}"
            desc = f"Passionate about software development. {random.choice(['Eager to learn and grow.', 'Love building things that matter.', 'Focused on clean code and user experience.'])}"
            skills_str = self._random_skills(random.randint(3, 7))
            linkedin = f"https://linkedin.com/in/{username}" if random.random() > 0.3 else ""
            github = f"https://github.com/{username}" if random.random() > 0.4 else ""
            profile = Profile.objects.create(
                user=user,
                role="job_seeker",
                display_name=f"{first} {last}",
                headline=random.choice(HEADLINES),
                city=city_name,
                state=state_code,
                location=loc,
                latitude=Decimal(str(lat)),
                longitude=Decimal(str(lng)),
                skills=skills_str,
                education=random.choice(EDUCATION_SAMPLES),
                work_experience=random.choice(WORK_SAMPLES),
                about_me=desc,
                contact_email=f"{username}@example.com",
                linkedin_url=linkedin,
                github_url=github,
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
            city_name, state_code, lat, lng = _pick_location()
            loc = f"{city_name}, {state_code}"
            Profile.objects.create(
                user=user,
                role="recruiter",
                display_name=f"{first} {last}",
                headline=f"Talent Acquisition at {random.choice(COMPANIES)}",
                city=city_name,
                state=state_code,
                location=loc,
                latitude=Decimal(str(lat)),
                longitude=Decimal(str(lng)),
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
            city_name, state_code, lat, lng = _pick_location(weights=CITY_WEIGHTS, for_jobs=True)
            lat, lng = _apply_offset(lat, lng)
            loc = f"{city_name}, {state_code}"
            skills_str = self._random_skills(random.randint(3, 6))
            desc_template = random.choice(JOB_DESCRIPTIONS)
            description = desc_template.format(title=title, company=company)
            salary = random.choice([60000, 75000, 85000, 95000, 110000, 125000, 140000, 160000, None])
            job = Job.objects.create(
                title=title,
                company=company,
                recruiter=recruiter,
                description=description,
                skills=skills_str,
                salary=salary,
                city=city_name,
                state=state_code,
                location=loc,
                latitude=Decimal(str(lat)),
                longitude=Decimal(str(lng)),
                remote=random.choice(["remote", "on_site", "hybrid"]),
                visa_sponsorship=random.choice(["yes", "no"]),
                is_active=True,
            )
            created.append(job)
        return created

    def _create_applications(self, seekers, jobs):
        app_statuses = ["applied", "review", "interview", "offer", "closed"]
        max_apps = min(2000, len(seekers) * len(jobs) // 2)
        for _ in range(max_apps):
            seeker = random.choice(seekers).user
            job = random.choice(jobs)
            if Application.objects.filter(applicant=seeker, job=job).exists():
                continue
            skills_snippet = job.skills.split(",")[0].strip() if job.skills else "your tech stack"
            note_template = random.choice(COVER_NOTES)
            note = note_template.format(skills=skills_snippet, company=job.company) if "{skills}" in note_template or "{company}" in note_template else note_template
            if random.random() < 0.15:
                note = ""
            Application.objects.create(
                applicant=seeker,
                job=job,
                cover_note=note,
                status=random.choice(app_statuses),
            )

    def _create_messages(self, seekers, recruiters):
        MESSAGES = [
            "Thanks for reaching out! I'd love to learn more about the role.",
            "When would be a good time to chat? I'm flexible this week.",
            "I've applied to the role. Looking forward to hearing back.",
            "Can we schedule a call this week? I'm available Tue–Thu afternoon.",
            "Great to connect! I'm very interested in the opportunity.",
            "I'd be happy to discuss my background. Does Thursday work?",
            "Thanks for the message. I've reviewed the job description — it looks like a great fit.",
            "Would love to learn more about the team and day-to-day responsibilities.",
        ]
        for _ in range(50):
            seeker = random.choice(seekers).user
            recruiter = random.choice(recruiters).user
            thread = Thread.objects.create()
            thread.participants.add(seeker, recruiter)
            for j in range(random.randint(2, 8)):
                sender = seeker if j % 2 == 0 else recruiter
                Message.objects.create(
                    thread=thread,
                    sender=sender,
                    body=random.choice(MESSAGES),
                )

    def _create_notifications(self, seekers, recruiters):
        all_users = [s.user for s in seekers] + [r.user for r in recruiters]
        NOTIFS = [
            ("message", "New message", "Someone sent you a message.", "/messages/"),
            ("recommendation", "Job recommendation", "We found 3 jobs matching your skills.", "/recommendations/"),
            ("login", "Welcome back", "You're all caught up.", ""),
            ("message", "Application update", "Your application status has been updated.", "/jobs/my-applications/"),
            ("recommendation", "New match", "A recruiter viewed your profile.", "/profile/"),
        ]
        for _ in range(200):
            user = random.choice(all_users)
            ntype, title, body, url = random.choice(NOTIFS)
            Notification.objects.create(
                recipient=user,
                notif_type=ntype,
                title=title,
                body=body,
                url=url,
            )
