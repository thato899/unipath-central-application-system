# UniPath — local proof of concept

UniPath demonstrates a central South African university application journey: create a student profile with seven matric subjects including Life Orientation, explore programmes across nine University of Pretoria faculties, compare illustrative requirements, apply to selected institutions, respond to simulated offers, and request residence after accepting an offer. It also includes accessibility controls and a local funding-destination summary.

## Run locally

Requires Python 3.10 or newer.

~~~powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/setup_local.py
python manage.py migrate
python app.py
~~~

Open http://127.0.0.1:8000. Create an account, then enroll an authenticator app by scanning the setup link or entering its key. Future sign-ins require the account password and a current six-digit authenticator code. Keep the generated `.env` and its encryption key backed up securely; `.env` is ignored by Git.

On macOS/Linux, activate the virtual environment with `source .venv/bin/activate`.

## Mobile app

The native Android/iOS client is in [`mobile/`](mobile/README.md). It uses Expo and connects to this Django API; no marks or profile are cached on the phone. Mobile setup, API address, simulator, and device instructions are in its README.

## Privacy and security

The prototype requires two-factor sign-in, uses CSRF-protected state changes, encrypts profile/marks and accommodation notes in the database, records the privacy-notice version, requests explicit destination consent, and offers personal-data export and password-plus-2FA account deletion. Read [privacy and security design](docs/privacy-security.md) for the limits and production requirements. Use fictional information only; this prototype does not certify POPIA compliance and is not approved for real student records.

## Demo boundaries

- Programme names and faculties are based on the [UP Yearbook](https://www.up.ac.za/yearbooks/home). UniPath is not affiliated with UP.
- Admission thresholds and eligibility results are illustrative, not official entry requirements or decisions. APS is entered separately and is not calculated from marks.
- The profile requires seven unique subject marks including Life Orientation. The statement-of-results picker only displays a selected filename; it does not upload or parse the file.
- Each chosen institution receives a simulated offer in the demo. No real university system, residence office, or NSFAS is contacted. Funding output is a local summary and is not a funding decision.
- The local Django server binds to `127.0.0.1`, uses SQLite, and is for demonstration only.

## Documentation

- [Product scope](devpost/scope.md) · [Requirements](devpost/prd.md) · [Technical specification](devpost/spec.md)
- [Architecture](docs/architecture.md) · [API contract](docs/api.md) · [Privacy and security](docs/privacy-security.md) · [Catalogue notes](docs/catalogue.md)
