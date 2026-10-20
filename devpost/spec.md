---
doc: spec
status: draft
---

# UniPath (working title) — Technical Specification

## How This Works, In Plain Language

Python serves the web pages and a small JSON API from one local process. The browser asks the API for courses and requirement matches, then sends chosen applications and offer decisions back to Python. The catalogue is based on undergraduate programme lists in the 2026 University of Pretoria Yearbook across all nine faculties, plus a demo institution. Admission thresholds and outcomes in the Python file are illustrative only, not official university requirements. The student's profile lives in browser storage; application records exist only while the demo server is running.

This is an agent-selected first implementation based on the learner's requirement to use Python and start building. The learner can revise the stack or behavior during review.

## Look and Feel

Implements `prd.md > Look and Feel`. Use the Figma prototype as the visual reference. Keep page backgrounds pale, text dark, buttons obvious, and accessibility controls labeled. Support readable text scaling, high-contrast mode, visible keyboard focus, and status text that does not depend on color.

## Where It Runs and How Someone Tries It

- Local desktop or laptop browser.
- Python 3.10 or later; no external packages are required.
- From the project folder run `python app.py`.
- Open `http://127.0.0.1:8000` in a browser. Stop with Ctrl+C.
- No deployment is included in the proof of concept.

## Components

### Local Python web server

Implements `prd.md > Student profile and marks`, `prd.md > Course discovery and university matching`, and `prd.md > Application review, status, and offer response`. `app.py` serves static files and JSON endpoints using Python's standard library. It binds to localhost only.

### Course and university catalogue

Implements `prd.md > Course discovery and university matching`. UP Yearbook programme entries and faculty groupings, example careers, one demo institution, and illustrative thresholds live in `app.py`. Verify current programmes with UP; use official university data agreements before using real admission requirements. The catalogue can later be replaced by an integration adapter after data contracts are agreed.

### Browser interface

Implements `prd.md > Screens and Layout` and `prd.md > Accessibility`. `static/index.html` contains semantic page sections and form labels; `static/style.css` provides responsive layout and accessibility presentation; `static/app.js` handles navigation, API calls, profile storage, eligibility display, submission, status, and offer response.

### Local JSON API

Implements `prd.md > Course discovery and university matching` and `prd.md > Application review, status, and offer response`.

- `GET /api/health`
- `GET /api/universities`
- `GET /api/courses`
- `GET /api/courses/{course_id}/matches` with APS, Mathematics, English, and upgrading query values
- `GET /api/applications`
- `POST /api/applications`
- `POST /api/applications/{application_id}/decision`
- `GET /api/residence`
- `POST /api/applications/{application_id}/residence` (accepted offer required)
- `GET /api/funding-plan` (derived destination summary; never sends data to NSFAS)

These endpoints define a local prototype contract, not a live university connection. They do not include real integration authentication, partner data, or NSFAS connectivity.

## Data and State

- Static course and university data: Python module constants in `app.py`.
- Student profile and marks: browser local storage.
- The form requires seven matric marks, including Life Orientation, and lets the student name four additional subjects. APS is separate and not derived from these marks.
- Application records: in-memory Python list, reset on server restart.
- Marks file input: filename only; file bytes are neither uploaded nor read.
- Sample responses: simulated by the application submission endpoint.

## File Structure

~~~text
build-with-ai-basics/
├── app.py                  # Local Python server, demo data, and API routes
├── README.md               # Setup and demo limits
├── static/
│   ├── index.html          # Accessible application screens
│   ├── style.css           # Responsive and accessibility styles
│   └── app.js              # Browser state and interactions
└── devpost/
    ├── learner-profile.md  # Personal learning context; ignored by Git
    ├── scope.md            # Approved project scope
    ├── prd.md              # Product behavior (draft)
    └── spec.md             # Technical plan (draft)
~~~

## Decisions and Open Issues

- Python standard library was selected for a dependency-free local proof of concept; this keeps setup simple but is not a production server architecture.
- No database or external service is used. Demo records reset when the server restarts.
- Real institution APIs, NSFAS, accounts, and mark-statement extraction are deferred.
- The Figma visual reference and the Clinic Connect interpretation are provisional.
- Verify accessibility behavior with assistive technology during review; the prototype has not been formally audited against an accessibility standard.
