# Local demo API

Base URL: `http://127.0.0.1:8000`

All responses are JSON unless an unknown GET path is being served as a static asset. The API is unauthenticated, local-only demo behavior. Sample responses include flags such as `sample_data` and `requirements_illustrative`.

## `GET /api/health`

Returns `{ "status": "ok", "demo": true }`.

## `GET /api/universities`

Returns `universities` and `sample_data`. The list contains the University of Pretoria (catalogue reference) and Central Demo University (sample institution). The endpoint does not contact either institution.

## `GET /api/courses`

Returns `courses`, `sample_data`, and `admission_thresholds_illustrative`. Each programme includes an ID, name, faculty, description, career examples, catalogue source note, and match count. Per-university match thresholds are omitted from this listing.

## `GET /api/courses/{course_id}/matches`

Query parameters:

- `aps`: integer, clamped to 0–100.
- `mathematics`: integer, clamped to 0–100.
- `english`: integer, clamped to 0–100.
- `upgrading`: `true` or `false`.

Returns the universities offering the selected sample course, illustrative requirements, and one of these statuses: `meets_requirements`, `apply_while_upgrading`, or `does_not_match`. Unknown course IDs return HTTP 404.

## `GET /api/applications`

Returns in-memory application records and `sample_data`. Records reset when the Python server stops.

## `POST /api/applications`

JSON request fields:

```json
{
  "course_id": "bcom-accounting",
  "university_ids": ["up"],
  "student_name": "Example Student",
  "upgrading": false,
  "marks": {
    "aps": 36,
    "mathematics": 70,
    "english": 65,
    "subjects": {
      "Home or First Additional Language": 70,
      "Mathematics": 70,
      "Life Orientation": 80,
      "Subject 4": 60,
      "Subject 5": 60,
      "Subject 6": 60,
      "Subject 7": 60
    }
  }
}
```

Requires a valid course, at least one valid university offering it, exactly seven named subject marks including `Life Orientation`, and either a matching threshold or an enabled upgrading path. Returns HTTP 201 with created applications. The first application in process memory gets a simulated offer; later applications get `in_review`.

## `POST /api/applications/{application_id}/decision`

JSON request: `{ "decision": "accept" }` or `{ "decision": "reject" }`. Updates a matching simulated offer. Invalid decisions or applications return HTTP 400 or 404.

## Error handling

Malformed or oversized JSON request bodies return HTTP 400. An invalid course selection, subject record, destination, or eligibility path returns an error object. This contract is for the local prototype only and is not a committed public university API.
