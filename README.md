# UniPath — local proof of concept

UniPath is a first-pass South African university application demo. A student enters one profile and seven matric subject marks (including Life Orientation), browses undergraduate programmes grouped across all nine UP faculties, compares illustrative thresholds, reviews applications, and responds to an offer.

The prototype includes controls for reading the current page aloud, changing text size, and enabling high contrast. It uses semantic headings, labeled fields, keyboard focus styles, and text labels for application states.

## Documentation

- [Product scope and decisions](devpost/scope.md)
- [Product requirements](devpost/prd.md)
- [Technical specification](devpost/spec.md)
- [Architecture and limitations](docs/architecture.md)
- [Local API contract](docs/api.md)
- [UP Yearbook catalogue notes](docs/catalogue.md)

## Run locally

Requires Python 3.10 or newer. No packages need to be installed.

~~~powershell
python app.py
~~~

Open http://127.0.0.1:8000 in a browser. Stop the server with Ctrl+C.

## Demo behavior and limits

- Programme names follow the undergraduate programme lists in the [UP Yearbook 2026](https://www.up.ac.za/yearbooks/home). The demo is not affiliated with UP; confirm current programme details in the Yearbook.
- Admission thresholds and outcomes are illustrative demo data, not official UP entry requirements or admission decisions. UP calculates APS using its own rules; Life Orientation may be required as a matric subject but is excluded from APS calculation for programmes such as BNurs. Always confirm course-specific requirements with the institution.
- The profile form requires seven subjects, including Life Orientation. APS is entered separately in this prototype; it is not calculated from marks.
- The profile is saved in the current browser's local storage.
- The marks statement input only selects a file name. This demo does not upload, read, or extract information from the file; marks are entered manually.
- Each submitted destination receives a simulated offer so the student can compare responses and accept or reject them. Only one offer can be accepted at a time in the single-student demo.
- Python serves a local JSON API for the course catalogue, eligibility matches, applications, and offer decisions. It does not connect to real university systems or NSFAS.
- Residence requests are recorded in the local demo only after an offer is accepted. The funding summary derives its university from that accepted offer and includes the residence preference; it does not contact NSFAS. Real NSFAS routing, institution-side course management, university APIs, authentication, and production data storage are future work.

## Local demo API

- GET /api/health
- GET /api/universities
- GET /api/courses
- GET /api/courses/{course_id}/matches?aps=36&mathematics=74&english=68&upgrading=false
- GET /api/applications
- POST /api/applications
- POST /api/applications/{application_id}/decision

The API is a local prototype contract for future institution integrations. No real institution is contacted.
