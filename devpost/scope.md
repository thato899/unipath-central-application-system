---
doc: scope
status: approved
---

# Central University Application System (working title)

One line: An accessible South African application portal where a student applies to courses at multiple universities using one profile and tracks each decision in one place.

## The Unique Kernel
A student enters their profile and marks once, then reuses them across university applications. The system makes course requirements and application progress clear, including when a student can still apply while upgrading marks.

## Who It's For
South African students applying to courses at more than one university, including blind and deaf students who need accessible application and status information. Existing application habits have not yet been established.

## The Core Loop
A student reviews courses grouped by faculty, checks how their marks match the requirements, applies to multiple courses using one profile, follows application statuses, and responds to offers in one place.

## Inspiration & Identity
No visual references or aesthetic direction established yet. Accessibility is a core product requirement: support blind students with screen-reader and keyboard access, and deaf students with visual information and non-audio alternatives.

## Why This Matters to the Learner
The learner wants to build an agentic project from requirements they define, with the agent implementing the agreed plan. Personal motivation for this particular application problem is not established.

## What "Working" Looks Like
A student can enter a profile and seven matric subject marks, browse undergraduate programmes across all nine UP faculties, see illustrative eligibility matches and upgrading paths, submit to listed institutions, track sample statuses, receive offers, and accept or reject them. After accepting one offer, they can record a residence preference tied to that university and view a demo funding destination summary. The experience is designed to be usable with assistive technology and without relying on sound.

## The POC Boundary
- Student-facing flow only, using an illustrative University of Pretoria catalogue and a secondary demo institution.
- One reusable student profile with exactly seven matric subject marks, including Life Orientation, plus separately entered APS.
- Undergraduate programme entries based on the UP 2026 Yearbook lists, grouped by all nine faculties, with illustrative requirement checks and an upgrading-marks application path.
- Application status tracking and a sample offer that can be accepted or rejected.
- Residence preference request unlocked after accepting an offer, with a demo funding-destination summary based on the accepted institution and residence preference.
- Accessibility built into the prototype and working app from the start.
- A Figma prototype reviewed before implementation; Python included in the code implementation.

## Later
Live residence submission, NSFAS funding allocation based on acceptance and residence, institution-side course/requirement management, and integrations with university systems through APIs. The local demo records a residence preference and derives a funding-destination summary, but sends neither to an institution nor NSFAS. Keep the design expandable to other countries.

## Explicitly Cut
- Live connections to university systems or NSFAS: unavailable for a small proof of concept and not needed to demonstrate the student journey.
- A complete national or universal admissions platform: the first version demonstrates one South African student flow using sample institutions and data.

## Catalogue and marks clarification

UP's [2026 Yearbook](https://www.up.ac.za/yearbooks/home) lists nine faculties and separate undergraduate programmes within each. The prototype's catalogue is based on those Yearbook programme lists and is not affiliated with UP; confirm current offerings and rules in the Yearbook. Demo admission thresholds are illustrative and must not be presented as UP requirements. The profile requires seven NSC subjects including Life Orientation. APS remains a separate field because institutions calculate it using their own rules; UP's [BNurs programme page](https://www.up.ac.za/programmes/undergraduate/bachelor-of-nursing-science-bnurs/2026) states that Life Orientation is excluded from its APS calculation.

