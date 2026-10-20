import json
import uuid
import hashlib
from functools import wraps
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django_otp.plugins.otp_totp.models import TOTPDevice
from app import COURSES, UNIVERSITIES, course_for, match_status, university_for
from .models import ApplicantProfile, Application, ResidenceApplication
from .models import MobileSession

def otp_api(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_verified():
            scheme, _, token = request.headers.get("Authorization", "").partition(" ")
            if scheme.lower() == "bearer" and token:
                digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
                mobile_session = MobileSession.objects.select_related("user", "otp_device").filter(
                    token_digest=digest, revoked_at__isnull=True, expires_at__gt=timezone.now()
                ).first()
                if mobile_session and mobile_session.otp_device.confirmed and mobile_session.user.is_active:
                    verified_user = mobile_session.user
                    verified_user.otp_device = mobile_session.otp_device
                    verified_user.is_verified = lambda: verified_user.otp_device is not None
                    request.user = verified_user
                    request.mobile_session = mobile_session
            if not request.user.is_authenticated or not request.user.is_verified():
                return JsonResponse({"error": "Sign in with your password and two-factor code first."}, status=401)
        return view(request, *args, **kwargs)
    return wrapped

def read_json(request):
    try:
        if len(request.body) > 100_000:
            return None, JsonResponse({"error": "Request body exceeds 100 KB."}, status=413)
        body = json.loads(request.body.decode("utf-8"))
        if not isinstance(body, dict):
            raise ValueError
        return body, None
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
        return None, JsonResponse({"error": "Send a valid JSON object."}, status=400)

def valid_profile(profile):
    if not isinstance(profile, dict) or not isinstance(profile.get("marks"), dict) or not isinstance(profile.get("name"), str):
        return False
    marks = profile["marks"]
    subjects = marks.get("subjects")
    if not isinstance(subjects, dict) or len(subjects) != 7 or "Life Orientation" not in subjects:
        return False
    if len({str(key).strip().casefold() for key in subjects}) != 7:
        return False
    try:
        aps = int(marks["aps"])
        mathematics, english = int(marks["mathematics"]), int(marks["english"])
        scores = [int(score) for score in subjects.values()]
    except (KeyError, TypeError, ValueError):
        return False
    return len(profile["name"].strip()) <= 120 and 0 <= aps <= 50 and all(0 <= n <= 100 for n in [mathematics, english, *scores])

@require_GET
@otp_api
def auth_status(request):
    return JsonResponse({"authenticated": True, "two_factor_verified": True, "email": request.user.email})

@require_GET
@otp_api
def profile_detail(request):
    record = ApplicantProfile.objects.filter(user=request.user).first()
    profile = record.data if record else None
    if profile is not None:
        profile["email"] = request.user.email
    return JsonResponse({"profile": profile, "account_email": request.user.email})

@require_POST
@otp_api
def profile_update(request):
    body, error = read_json(request)
    if error:
        return error
    profile = body.get("profile")
    if not valid_profile(profile):
        return JsonResponse({"error": "Enter a name, APS, and exactly seven unique subject marks including Life Orientation."}, status=400)
    email = str(profile.get("email", "")).strip().lower()
    if email != request.user.email.lower():
        return JsonResponse({"error": "The account email is changed through account settings, not the marks form."}, status=400)
    profile = dict(profile)
    profile.pop("email", None)
    ApplicantProfile.objects.update_or_create(user=request.user, defaults={"data": profile})
    return JsonResponse({"profile": {**profile, "email": request.user.email}, "saved": True})

@require_GET
@otp_api
def universities(request):
    return JsonResponse({"universities": UNIVERSITIES, "sample_data": True})

@require_GET
@otp_api
def courses(request):
    data = [{k: v for k, v in course.items() if k != "matches"} | {"match_count": len(course["matches"])} for course in COURSES]
    return JsonResponse({"courses": data, "sample_data": True, "admission_thresholds_illustrative": True})

@require_GET
@otp_api
def course_matches(request, course_id):
    course = course_for(course_id)
    profile = ApplicantProfile.objects.filter(user=request.user).first()
    if not course or not profile:
        return JsonResponse({"error": "Course or saved profile not found."}, status=404)
    marks = profile.data["marks"]
    results = []
    for requirement in course["matches"]:
        uni = university_for(requirement["university_id"])
        if uni:
            results.append({"university": uni, "requirements": {k: requirement[k] for k in ("aps", "mathematics", "english")}, "status": match_status(requirement, marks, bool(profile.data.get("upgrading"))), "requirements_illustrative": True})
    return JsonResponse({"course_id": course["id"], "matches": results, "marks_used": {k: marks[k] for k in ("aps", "mathematics", "english")}, "sample_data": True})

def application_json(application):
    return {"id": application.id, "course_id": application.course_id, "course_name": application.course_name,
            "university_id": application.university_id, "university_name": application.university_name,
            "status": application.status, "decision": application.decision, "demo_response": application.demo_response,
            "sample_data": True}

@require_GET
@otp_api
def applications(request):
    return JsonResponse({"applications": [application_json(app) for app in Application.objects.filter(user=request.user)], "sample_data": True})

@require_POST
@otp_api
def create_applications(request):
    body, error = read_json(request)
    if error:
        return error
    course = course_for(str(body.get("course_id", "")))
    profile_record = ApplicantProfile.objects.filter(user=request.user).first()
    if not course or not profile_record:
        return JsonResponse({"error": "Save your profile and choose a valid course first."}, status=400)
    if body.get("consent_to_share") is not True:
        return JsonResponse({"error": "Confirm which selected universities may receive your application details."}, status=400)
    ids = body.get("university_ids")
    if not isinstance(ids, list) or not ids or len(ids) != len(set(map(str, ids))):
        return JsonResponse({"error": "Select one or more unique university destinations."}, status=400)
    allowed = {match["university_id"]: match for match in course["matches"]}
    profile = profile_record.data
    destinations = []
    for raw_id in ids:
        university_id = str(raw_id)
        requirement = allowed.get(university_id)
        university = university_for(university_id)
        if not requirement or not university:
            return JsonResponse({"error": "A selected institution does not offer this course in the demo."}, status=400)
        if match_status(requirement, profile["marks"], bool(profile.get("upgrading"))) == "does_not_match":
            return JsonResponse({"error": "A selected destination is outside the listed match or upgrading path."}, status=400)
        if Application.objects.filter(user=request.user, course_id=course["id"], university_id=university_id).exists():
            return JsonResponse({"error": "An application for this course and institution already exists."}, status=409)
        destinations.append(university)
    created = []
    for university in destinations:
        application = Application.objects.create(
            id=uuid.uuid4().hex[:8], user=request.user, course_id=course["id"], course_name=course["short_name"],
            university_id=university["id"], university_name=university["name"], status="offer_received",
        )
        created.append(application_json(application))
    return JsonResponse({"applications": created, "sample_data": True}, status=201)

@require_POST
@otp_api
def application_decision(request, application_id):
    body, error = read_json(request)
    if error:
        return error
    decision = body.get("decision")
    if decision not in {"accepted", "rejected"}:
        return JsonResponse({"error": "Choose accepted or rejected."}, status=400)
    application = Application.objects.filter(user=request.user, id=application_id).first()
    if not application or application.status != "offer_received":
        return JsonResponse({"error": "This offer is unavailable."}, status=404)
    if decision == "accepted" and Application.objects.filter(user=request.user, status="accepted").exists():
        return JsonResponse({"error": "Only one offer can be accepted at a time."}, status=409)
    application.status = decision
    application.decision = decision
    application.save(update_fields=["status", "decision"])
    return JsonResponse({"application": application_json(application), "sample_data": True})

@require_GET
@otp_api
def residence_applications(request):
    return JsonResponse({"residence_applications": [
        {"application_id": item.application_id, "university_name": item.application.university_name,
         "preference": item.preference, "status": item.status, "sample_data": True}
        for item in ResidenceApplication.objects.filter(application__user=request.user).select_related("application")
    ], "sample_data": True})

@require_POST
@otp_api
def create_residence_application(request, application_id):
    body, error = read_json(request)
    if error:
        return error
    application = Application.objects.filter(user=request.user, id=application_id, status="accepted").first()
    if not application:
        return JsonResponse({"error": "Accept an offer before applying for residence."}, status=409)
    if ResidenceApplication.objects.filter(application=application).exists():
        return JsonResponse({"error": "A residence request already exists for this offer."}, status=409)
    preference = body.get("preference")
    if preference not in {value for value, _ in ResidenceApplication.PREFERENCES}:
        return JsonResponse({"error": "Choose a residence preference."}, status=400)
    notes = str(body.get("accommodation_needs", "")).strip()
    if len(notes) > 500:
        return JsonResponse({"error": "Accommodation notes must be 500 characters or fewer."}, status=400)
    residence = ResidenceApplication.objects.create(application=application, preference=preference, accommodation_needs=notes)
    return JsonResponse({"residence_application": {
        "id": residence.pk, "application_id": application.id, "university_name": application.university_name,
        "course_name": application.course_name, "preference": residence.preference,
        "status": residence.status, "sample_data": True,
    }}, status=201)

@require_GET
@otp_api
def funding_plan(request):
    accepted = Application.objects.filter(user=request.user, status="accepted").first()
    if not accepted:
        return JsonResponse({"status": "no_accepted_offer", "sent_to_nsfas": False, "sample_data": True})
    residence = ResidenceApplication.objects.filter(application=accepted).first()
    return JsonResponse({
        "status": "summary_ready_demo" if residence else "waiting_for_residence",
        "university_name": accepted.university_name, "course_name": accepted.course_name,
        "application_id": accepted.id, "residence_status": residence.status if residence else "not_submitted",
        "residence_preference": residence.preference if residence else None,
        "sent_to_nsfas": False, "sample_data": True,
    })
