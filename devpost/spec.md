---
doc: spec
status: draft
---

# UniPath — Technical Specification

## Overview

UniPath is a local South African university-application proof of concept. Python/Django provides the accessible student interface and JSON API. The sample catalogue follows programme and faculty groupings from the 2026 University of Pretoria Yearbook; eligibility and offer outcomes are illustrative.

## Run locally

- Python 3.10 or later; install dependencies from `requirements.txt`.
- Generate local secrets with `python scripts/setup_local.py`, then initialize with `python manage.py migrate`.
- Start using `python app.py`; browse to `http://127.0.0.1:8000`.
- Registration requires privacy-notice acknowledgement and authenticator enrollment. Every sign-in uses password and a current six-digit TOTP code.

## Components

- `app.py`: course and university sample data plus Django local-server entry point.
- `unipath_project/`: Django settings, URL routing, WSGI, and ASGI configuration.
- `applications/`: authentication, profile/application models, encrypted fields, validated API, and privacy actions.
- `static/`: accessible student interface, CSS/JavaScript, and auth templates.
- `docs/privacy-security.md`: POPIA-informed safeguards and production boundaries.

## Data flow and privacy controls

Student profile and marks are encrypted using the per-installation Fernet key. Residence notes are encrypted as well. Server-side APIs require authenticated TOTP-verified sessions and CSRF protection for state changes. Destination application submissions require explicit consent. Students can review/correct profiles, export JSON, and delete their account after confirming password and a fresh TOTP code. The local database also stores authentication identifiers, application routing/status, and TOTP device records.

This setup is a prototype, not a claim of POPIA compliance. It runs on local SQLite, has no production retention schedule, monitoring, breach operations, recovery flow, or legal review. Use fictional information only; before real applicant data, especially children's information, the responsible institution must determine the lawful basis and safeguards, provide notices, establish an Information Officer and data-subject processes, and complete security/privacy assessment.

## Functional API

The authenticated API includes course/university catalogue and match retrieval, profile read/update, application creation and offer decisions, residence requests following an accepted offer, funding-destination summary, privacy export, and account deletion. See `docs/api.md` for methods, paths, and boundaries. No external institution, residence office, or NSFAS is contacted.

## Accessibility

The interface includes semantic structure, keyboard focus, labeled forms, text scaling, contrast adjustment, and read-aloud support. Authentication uses a phone authenticator; this prototype does not yet include an equivalent recovery path for people who cannot use one, so real deployment requires accessible, identity-verified alternatives.
