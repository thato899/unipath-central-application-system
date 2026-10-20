# Privacy and security design

UniPath is a local proof of concept with account login, mandatory TOTP two-factor authentication, and basic privacy controls. These safeguards help demonstrate a responsible design; they do not establish or certify POPIA compliance. The operator must determine the lawful basis and purposes, appoint and register an Information Officer where required, give an accurate privacy notice, set retention periods, manage operators and contracts, assess risks, handle data-subject requests, and notify security compromises as required.

## POPIA principles represented in the prototype

- **Purpose and notice:** registration explains the account and application-demo purposes, policy version, and that no real institution or NSFAS receives data. Consent to the notice is recorded. Separate affirmative consent is required before creating demo applications for chosen destinations.
- **Minimality:** only email, a student profile/marks, chosen applications, and optional residence preference/needs are collected. The marks-statement picker is not uploaded or parsed.
- **Security safeguards:** passwords use Django's password hashers and validators; sign-in requires password plus TOTP; session and CSRF protections are enabled; mutation APIs require CSRF and verified login; profile/marks and accommodation notes use authenticated Fernet encryption at the application field level; error responses avoid exposing stored records.
- **Access and correction:** students can review and update their profile and download a JSON copy of account and application data.
- **Deletion:** students can delete their account and related demo data after password and fresh TOTP confirmation. Backups, operational logs, legal retention duties, and external processors need separate deletion policies in a real deployment.
- **Retention and breach response:** not yet operationally configured. A real operator must set and enforce a retention schedule, monitor access, maintain incident procedures, and notify the Information Regulator and affected people as soon as reasonably possible where the statutory threshold is met.
- **Children's information:** this prototype has no approved process for processing children's personal information. Before use with school learners, the responsible institution must assess POPIA's special rules for children's information and identify the applicable authorization and safeguards.

## Current boundaries and deployment requirements

- Use fictional data only. This prototype has not been assessed by an Information Officer or privacy/legal professional and is not ready for real applicants, especially children.
- TOTP is required for every account. A user must keep the authenticator setup secret safe; self-service recovery is not implemented. The django-otp device secret is stored in the local database and should be protected with encrypted storage and strict filesystem access. Production deployment must use managed secret storage and encrypt database volumes/backups.
- The Fernet key and Django signing key are generated per local installation by `python scripts/setup_local.py` and stored in ignored `.env`. Back up keys separately and securely; key loss prevents reading encrypted fields. Do not commit `.env` or use local keys in production.
- The local database is SQLite and the server binds only to `127.0.0.1`. Production needs a supported managed database, HTTPS, key rotation and recovery, secure backups, monitoring/audit trails, abuse controls/rate limits at the edge, vulnerability review, and operational incident response.
- Sample courses, eligibility rules, offers, applications, residence requests, and funding summaries are illustrative. No university, residence office, or NSFAS is contacted.
- Accessibility preferences do not replace an accessible security process. Provide an alternative support channel for applicants who cannot use a phone authenticator, with identity verification and equivalent protections, before real-world use.

## Reference law and guidance

- [Protection of Personal Information Act 4 of 2013](https://www.justice.gov.za/legislation/acts/2013-004.pdf), including conditions for lawful processing and sections 19–22 on security safeguards and compromises.
- [Information Regulator POPIA guidance and forms](https://inforegulator.org.za/popia/).
- [Information Regulator fact sheet on handling security compromises](https://inforegulator.org.za/2025/08/19/fact-sheet-handling-of-security-compromises/).
