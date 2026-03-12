# 2340-Project-2 - TalentSwarm

## Project Status

| | |
|---|---|
| **Current Phase** | Sprint 1 |
| **Preliminary demo** | Feb 17 |
| **Sprint 1 due** | Feb 19 |
| **Sprint 2 due** | Mar 12, 2026 |
| **Last Updated** | Mar 10, 2026 |

---

## Job Location Feature (django-cities-light)

When posting or editing a job, recruiters select **State** first, then **City** from cascading dropdowns. The data comes from [django-cities-light](https://github.com/yourlabs/django-cities-light), which imports GeoNames data (US cities with population > 15,000).

### What was implemented

- **State dropdown** → US regions from django-cities-light
- **City dropdown** → Loaded via AJAX when state is selected (`GET /jobs/cities/?region_id=X`)
- **Latitude/longitude** → Stored automatically when a city is selected (for future map features)

### Setup (first-time or new clone)

After `pip install` and `migrate`, populate the cities data:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py cities_light  
```

### Documentation

- [django-cities-light on GitHub](https://github.com/yourlabs/django-cities-light)
- [django-cities-light docs](https://django-cities-light.readthedocs.io/)
- [GeoNames](https://www.geonames.org/) – source of city/region data


- [sibtc/dependent-dropdown-example](https://github.com/sibtc/dependent-dropdown-example) – Django dependent dropdown tutorial
- [django-cities-light](https://github.com/yourlabs/django-cities-light) – Data source (Country, Region, City models)

---

## Context Description

Early-career job seekers often face challenges finding roles that match their skills, interests, and location preferences. At the same time, recruiters struggle to identify and evaluate applicants who are a good fit for their openings, especially when managing large pools of candidates.

Your team has been asked to design and build a web application that bridges this gap. The platform should serve as a meeting point between young professionals searching for opportunities and recruiters looking for talent. It should support creating and managing professional profiles, posting and exploring job opportunities, and enabling recruiters to search, track, and engage with applicants.

Because location plays a key role in employment, the platform should also integrate map-based features to help job seekers visualize opportunities geographically and recruiters understand applicant distribution.

This project is intended to challenge you to think about multiple perspectives (considering Job seekers, Recruiters, and Administrators) while practicing core software engineering skills such as requirements analysis, system design, team collaboration, and web development.

---

## User Stories

### Job Seeker Stories

- [ ] As a Job Seeker, I want to create a profile with my headline, skills, education, work experience, and links so recruiters can learn about me.
- [ ] As a Job Seeker, I want to search for jobs with filters (title, skills, location, salary range, remote/on-site, visa sponsorship) so I can find opportunities that match my needs.
- [ ] As a Job Seeker, I want to apply to a job with one click and include a tailored note so my application feels personalized.
- [ ] As a Job Seeker, I want to track the status of my applications (Applied ? Review ? Interview ? Offer ? Closed) so I know where I stand.
- [ ] As a Job Seeker, I want to set privacy options on my profile so I control what recruiters can see.
- [ ] As a Job Seeker, I want to receive recommendations for jobs based on my skills so I discover opportunities I might have missed.
- [ ] As a Job Seeker, I want to view job postings on an interactive map so I can see which ones are near me.
- [ ] As a Job Seeker, I want to filter jobs on the map by distance from my current location so I can prioritize nearby opportunities.
- [ ] As a Job Seeker, I want to set a preferred commute radius (e.g., 10 miles) on the map so I only see jobs within a reasonable travel distance.

### Recruiter Stories

- [ ] As a Recruiter, I want to post and edit job roles so candidates can apply to my openings.
- [ ] As a Recruiter, I want to search for candidates by skills, location, and projects so I can find talent that fits my positions.
- [ ] As a Recruiter, I want to organize applicants in a pipeline (e.g., a Kanban board) so I can easily manage hiring stages.
- [ ] As a Recruiter, I want to message candidates inside the platform so I can contact them without the use of personal emails.
- [ ] As a Recruiter, I want to email candidates through the platform so I can reach out to them through their personal emails.
- [ ] As a Recruiter, I want to save a candidate search and get notified about new matches so I don't have to repeat the same queries.
- [ ] As a Recruiter, I want to receive candidate recommendations for my job postings so I find qualified applicants faster.
- [ ] As a Recruiter, I want to pin my job posting's office location on a map so candidates know exactly where the job is based.
- [ ] As a Recruiter, I want to see clusters of applicants by location on a map so I understand where most candidates are coming from.

### Administrator Stories

- [ ] As an Administrator, I want to manage users and roles so the platform remains fair and safe.
- [ ] As an Administrator, I want to moderate or remove job posts so the platform stays free of spam or abuse.
- [ ] As an Administrator, I want to export data (CSV) for reporting purposes so stakeholders can analyze usage.

---

## Development Workflow

**Before you start** (first time only):

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
python manage.py migrate
python manage.py cities_light  # Populate US cities (optional, ~5–10 min)
```

**Each time you work:**

1. Pull latest changes:
   ```bash
   git pull origin main
   ```

2. Run migrations (if models changed):
   ```bash
   python manage.py migrate
   ```

3. Start the dev server and work at http://127.0.0.1:8000/:
   ```bash
   python manage.py runserver
   ```

4. If you added or changed models, create migrations before committing:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Commit and push when done:
   ```bash
   git add .
   git commit -m "Brief description of your changes"
   git push origin main
   ```

---

## Sprint 1 (Planned)

*To be filled after sprint completion.*

---

## Sprint 2 (Planned)

*To be filled after sprint completion.*

---

## Sprint Report Template

*Use this outline when recording sprint videos.*

1. **What was completed in this sprint?**
   - a. Which user stories were implemented
   - b. A brief demonstration of working functionality (on the deployed website)

2. **How was the work completed?**
   - a. Key technical decisions (architecture, tools, libraries, APIs)
   - b. How responsibilities were divided among team members
   - c. How Scrum practices were applied (planning, standups, reviews)

3. **What challenges did the team encounter and how were they resolved?**
   - a. Technical or design challenges
   - b. Process or coordination issues

4. **What is next?**
   - a. Remaining work or known limitations
   - b. Planned focus for the next sprint
