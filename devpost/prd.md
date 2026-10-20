---
doc: prd
status: draft
---

# UniPath (working title) — Product Requirements

One line: An accessible South African application portal for students applying to multiple universities using one profile and one marks record.
Source: `scope.md > The Unique Kernel`, `scope.md > Who It's For`, and `scope.md > The POC Boundary`.

## The Core Journey

1. A student enters a profile and marks. The app saves the profile in the browser for this local demo.
2. They browse courses grouped by faculty. Every course explains its subject and gives example careers.
3. They open a course to compare sample universities and course requirements. The app labels a match as meeting listed requirements or having an application path while the student is upgrading marks.
4. They select matching universities, review the destinations and shared profile, then confirm submission.
5. The application tracker shows sample university responses in one place. Sample offers can be accepted or rejected.
6. After accepting an offer, the student can record a residence preference for that university and view a funding-destination summary derived from the accepted offer and residence request.

Source: `scope.md > The Core Loop` and `scope.md > What "Working" Looks Like`.

## Screens and Layout

- **Profile and marks:** accessible form for a student's name, email, separately entered APS, seven NSC subject marks including compulsory Life Orientation, upgrading status, and optional marks-statement file selection.
- **Course explorer:** undergraduate programme cards grouped across all nine UP faculties, with career examples and a path to university matches. Programme names follow the UP 2026 Yearbook lists.
- **University matches:** requirements, the student's marks, eligibility/upgrading labels, and selectable application destinations.
- **Application review:** shared profile and chosen destinations shown before the student confirms.
- **Application tracker:** a readable list of university decisions with text labels as well as colors.
- **Offer response:** confirmation after accepting or rejecting an offer.
- **Residence and funding summary:** residence request is available only for the accepted university; the demo funding summary shows the accepted institution and residence preference without sending data to NSFAS.

## Look and Feel

The learner referenced Clinic Connect. For this first pass, the visual direction uses a calm, clear service layout, strong section labels, and prominent actions. The app name and exact visual traits remain provisional for learner correction.

Accessibility controls are clearly named: read aloud, text size, and high contrast. Interactive controls use visible labels. The layout should work with keyboard navigation and screen readers; application states remain available as text and are not conveyed through color alone. The app has no audio-only instructions or alerts.

## Features and Behavior

### Student profile and marks

- The student enters a name, email, APS, marks for seven subjects including Life Orientation, and whether they are upgrading marks. Mathematics and English are separately identified for course matching; four additional subjects are captured as subject 4–7 in this iteration.
- APS is entered separately and is not calculated from the seven marks because universities use institution and programme-specific APS rules. Life Orientation is included in the matric record; UP states that it is excluded from APS calculation for some programmes.
- The student can select a marks statement file for reference, but this proof of concept does not upload or parse it. Marks are entered manually.
- The profile is stored in browser local storage for the demo.

### Course discovery and university matching

- Courses are grouped by faculty and include a description and examples of careers.
- The app compares selected marks with illustrative demo thresholds for UP Yearbook programme entries and a demo institution. These values are not official admission requirements.
- The student sees the requirements and their marks together.
- If marks do not meet a requirement, an available upgrading pathway is shown where configured in sample data.
- Eligible universities are selected by default; students can include upgrading-path applications, remove selections, and review destinations before submitting.

### Application review, status, and offer response

- Before submission, the student sees the profile and marks that will be shared and each chosen university/course.
- Submission creates a sample application and simulated offer for every selected destination.
- The tracker shows textual status for every sample application.
- The student can accept or reject a simulated offer. The response is reflected in the tracker.
- The student can accept at most one offer in the demo. Accepting another requires declining the first.
- After acceptance, the student can record one residence preference for that university. The funding summary derives its destination from the accepted application and shows whether residence was requested.

### Accessibility

- Read aloud speaks the current page when supported by the browser.
- Text size controls adjust the interface scale.
- High contrast switches to a stronger black-and-yellow palette.
- Semantic headings, labeled form controls, visible keyboard focus, a skip link, and live status announcements support assistive technology.
- All application status, instructions, and action results remain visible in text for deaf and hard-of-hearing students.

## States and Boundaries

- **First visit:** profile setup is shown before course browsing.
- **Returning visit:** the browser-saved profile is restored and the course explorer opens.
- **No applications:** the tracker explains that none exist and links back to course discovery.
- **No current match:** the app says no listed requirement currently matches. If a configured upgrade path exists and the student is upgrading, the application can still be selected.
- **Sample response:** admissions outcomes are simulated and clearly labeled; they are not real university decisions.
- **File selection:** selecting a file only displays its name. The file is not uploaded or read.
- **Server restart:** application records are in memory and reset when the local server stops.

## Product Decisions

- The first prototype represents South African admissions and can be expanded to other countries later.
- Students choose a course, see career examples, review matching universities, and confirm before applications are sent.
- Students can apply through an upgrading pathway where sample course rules allow it.
- Blind and deaf students are core users; inclusive controls and visible status text are part of the main product.
- UP programme names follow the undergraduate lists in the Yearbook; the prototype is not affiliated with UP, and current offerings and rules must be checked in the Yearbook. Admission thresholds and outcomes are illustrative, not official UP requirements or decisions.
- Python is required for the implementation; the learner wants to set requirements while the agent builds.

## What We're Building

A local, responsive student application flow with profile and marks entry, faculty-grouped courses, career examples, sample eligibility matching, application review and submission, status tracking, and simulated offer acceptance or rejection. It includes visible accessibility controls and a small Python JSON API.

## Deferred From the POC

- Real university and NSFAS connections: the prototype has no credentials, integration agreements, or external data access.
- Uploading and extracting marks from a real statement: would require secure file handling and document parsing; the first demo uses manual marks.
- A national production admissions system: the first version only demonstrates fictional sample data.
- University administrator dashboards: the student journey is the only prototype surface.
- Authentication and production persistence: the profile is local to the browser and applications are held in server memory.
- Live residence applications: the prototype records a local demo request only; it does not send it to a university residence office.
- Real NSFAS allocation: the funding summary is not transmitted to NSFAS and does not determine funding eligibility.

## Possible Later Enhancements

Connect residence requests to university systems through approved partner APIs. Add an authorized NSFAS integration that uses accepted institution and residence details with student consent, and add country-specific admissions rules.

## Non-Goals

- Do not claim that sample matching predicts or guarantees admission; each university makes its own decision.
- Do not send real student data to an institution or NSFAS.
- Do not present illustrative demo thresholds as real university requirements.

## Open Questions

- Should marks-statement upload extract marks automatically, or should a student continue to enter them manually? The prototype currently supports manual entry and a non-uploading file selection. **Resolve before expanding file handling.**
- What Clinic Connect qualities should inform the next visual revision? The current visual interpretation is provisional and can be corrected during prototype review.
