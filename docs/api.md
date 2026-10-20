# Local API contract

Base URL: `http://127.0.0.1:8000/api/`. Every API endpoint requires an authenticated session with verified TOTP. POST requests require Django CSRF token in `X-CSRFToken`. JSON request bodies are capped at 100 KB. Responses are prototype data and do not contact partner institutions.

| Method | Path | Purpose |
|---|---|---|
| GET | `/auth/status` | Verified session status |
| GET / POST | `/profile` / `/profile/update` | Read and save the signed-in profile |
| GET | `/universities` | Sample institution catalogue |
| GET | `/courses` | Sample programme catalogue |
| GET | `/courses/{course_id}/matches` | Compare saved marks with illustrative requirements |
| GET | `/applications` | List the signed-in student's applications |
| POST | `/applications/create` | Create demo submissions with explicit destination consent |
| POST | `/applications/{id}/decision` | Accept or reject a simulated offer |
| GET | `/residence` | List demo residence requests |
| POST | `/applications/{id}/residence` | Record residence preference after accepting an offer |
| GET | `/funding-plan` | Summarize accepted university and residence preference; never sends to NSFAS |
| GET | `/privacy/export` | Download personal data as JSON |
| POST | `/privacy/delete-account` | Delete account and associated demo records after password + current TOTP |

Unauthenticated or unverified requests receive HTTP 401. Invalid data returns an error object and suitable 4xx status. Applications, offers, eligibility thresholds, residence outcomes, and funding summaries are simulated. See [privacy and security design](privacy-security.md) before using or deploying the prototype.
