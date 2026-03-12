# TalentSwarm (Nexora)

Job board for job seekers and recruiters. Built with Django.

## Quick Start

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
python manage.py migrate
python manage.py cities_light  # Populate US cities (~5–10 min)
python manage.py seed_dummy_data --clear  # Test data (password: testpass123)
python manage.py runserver
```

Open http://127.0.0.1:8000/

## User Stories

**15 of 21 completed**

### Job Seeker
- [x] Create profile (headline, skills, education, work experience, links)
- [x] Search jobs (title, skills, location, salary, remote, visa)
- [x] Apply with one click + optional note
- [x] Track application status (Applied → Review → Interview → Offer → Closed)
- [x] Set profile privacy options
- [x] Receive job recommendations based on skills
- [x] View jobs on interactive map with clustering
- [ ] Filter map by distance from my location
- [ ] Set commute radius on map

### Recruiter
- [x] Post and edit job roles
- [x] Search candidates by skills, location, projects
- [x] Organize applicants in pipeline (Kanban)
- [x] Message candidates in-app
- [x] Receive candidate recommendations for jobs
- [x] Pin job location on map (State/City + optional pin-drop)
- [ ] See clusters of applicants by location on map
- [ ] Email candidates through platform
- [ ] Save searches and get notified about new matches

### Administrator
- [x] Manage users and roles
- [x] Moderate or remove job posts
- [ ] Export data (CSV)

## Features

- **Location**: State/City dropdowns (django-cities-light), lat/lng stored for maps
- **Pin-drop**: Fine-tune location on map when creating/editing jobs or profiles (seed mimics this with random offsets)
- **Map**: Job seeker home page shows jobs on Leaflet map with marker clustering
- **Map API**: `GET /jobs/map-markers/` — jobs + applicants (when `?job_id=X`)

## Development

```bash
git pull origin main
python manage.py migrate
python manage.py runserver
```


TODO: As seeker: filter map by distance from location: commute distance (pin to pin as the crow flies)
TODO: use map and bubble to set this commute distance filter

TODO from the recruiter page, see similar map of seekers