# Architecture and implementation notes

## Overview

UniPath is a local Django proof of concept. Django serves the accessible browser interface and JSON API; authenticated records are stored in SQLite. Students must verify a password and a TOTP authenticator code before entering the application.

```text
Browser (static/index.html, app.js, style.css)
  └─ CSRF-protected JSON ──> Django (127.0.0.1:8000)
       ├─ django-otp password + TOTP authentication
       ├─ SQLite account/application records
       ├─ Fernet-encrypted profile/marks and residence notes
       └─ in-memory catalogue from app.py (illustrative UP and demo data)
```

## Data flow

1. Registration records the accepted privacy notice version and requires TOTP enrollment.
2. A verified session loads courses and the signed-in student's saved profile from the API.
3. Profile updates are validated and encrypted before storage. Exactly seven unique subjects are required, including Life Orientation.
4. Application submission requires explicit destination-sharing consent. Server-side validation checks selected course/university eligibility, duplicate submissions, and the upgrading path.
5. Each application receives a simulated offer. A student can accept one offer, then record a residence preference; the funding summary derives its destination from that offer.
6. Profile users can export their data or delete their account after password and fresh authenticator-code confirmation.

## Main files

- `app.py`: illustrative catalogue plus local Django development-server entry point.
- `unipath_project/settings.py`: Django, session, CSRF, OTP, cookie, and local database settings.
- `applications/`: account flows, models, encrypted fields, API validation, privacy export/deletion, and URL routing.
- `static/`: accessible application UI, JavaScript client, CSS, and authentication templates.
- `docs/privacy-security.md`: POPIA-informed controls, limits, and real deployment requirements.

## Current constraints

- Localhost only, SQLite only, fictional data only. Do not enter real student data.
- Profile and residence text fields are encrypted with a local Fernet key, while authentication identifiers and application routing fields remain queryable in SQLite. TOTP device secrets are stored in the local database and require protected storage.
- No configured retention/deletion schedule, operational audit and alerting, breach response function, Information Officer, real institution integration, NSFAS connection, or verified legal compliance assessment exists.
- Enrollment recovery is not implemented. Production must design an accessible, identity-verified recovery route.
- Catalogue and admission results remain illustrative; application and offer states are simulated.
