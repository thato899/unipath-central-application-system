# Architecture and implementation notes

## Overview

UniPath is a local proof of concept with no external package dependencies. A Python standard-library HTTP server serves the static browser application and JSON API from the same process. The browser calls that API with `fetch`.

```text
Browser (static/index.html, style.css, app.js)
  ├─ localStorage: student profile and marks (demo only)
  └─ HTTP JSON ──> app.py (127.0.0.1:8000)
                    ├─ in-memory UP and demo university catalogue
                    └─ in-memory sample applications
```

## Main files

- `app.py`: programme and university sample data, eligibility matching, JSON endpoints, and static-file server.
- `static/index.html`: semantic page structure, profile form, course explorer, application tracker, and accessibility controls.
- `static/app.js`: browser navigation, profile storage, catalogue rendering, match requests, application submissions, and offer decisions.
- `static/style.css`: responsive presentation, focus styles, text scaling, and high-contrast theme.
- `devpost/scope.md`: approved product boundary and source notes.
- `devpost/prd.md`: product requirements and flow behavior.
- `devpost/spec.md`: technical implementation specification.
- `docs/api.md`: local API contract.
- `docs/catalogue.md`: catalogue coverage, sources, and limitations.

## Data flow

1. The student enters profile details, APS, and seven NSC subject marks. Life Orientation is mandatory. The prototype stores these values in the current browser's local storage.
2. The browser loads the programme list from `GET /api/courses` and university list from `GET /api/universities`.
3. For a selected programme, the browser requests illustrative matches using APS, Mathematics, English, and upgrading status.
4. On submission, the browser posts the selected university IDs and marks. The server checks the programme, destinations, seven-subject record, and demo eligibility path.
5. The server stores sample applications in process memory. The first created application receives a simulated offer; later records remain in review.
6. The student can post an accept/reject decision for a simulated offer.

## Current constraints

- `127.0.0.1` binding means this is intended for local demonstration only.
- Profile data is in browser local storage, not protected account storage.
- Application records are in memory and disappear when the server stops.
- The marks statement picker only shows a selected filename. It does not upload or parse the document.
- Admission thresholds, sample university matches, and outcomes are illustrative. They are not official University of Pretoria requirements or decisions.
- No authentication, authorization, audit logging, encryption-at-rest, production database, NSFAS connection, or real university integration is implemented.
- Do not enter real sensitive student information into this proof of concept.

## Future integration boundary

The local `/api` endpoints are a prototype contract, not a production integration. A production system needs university-authorized data feeds and agreements, identity and access controls, consent and privacy design, secure document handling, persistent records, audit trails, and institution-specific rules. NSFAS and residence flows are outside the current implementation.
