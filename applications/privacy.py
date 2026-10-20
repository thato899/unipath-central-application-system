import json
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET, require_POST
from .api import otp_api, read_json
from .models import ApplicantProfile, Application, DataConsent, ResidenceApplication

@require_GET
@otp_api
def export_data(request):
    profile = ApplicantProfile.objects.filter(user=request.user).first()
    payload = {
        "account": {"email": request.user.email, "created_at": request.user.date_joined.isoformat()},
        "profile": profile.data if profile else None,
        "applications": [{"id": item.id, "course": item.course_name, "university": item.university_name, "status": item.status, "created_at": item.created_at.isoformat()} for item in Application.objects.filter(user=request.user)],
        "residence_requests": [{"application_id": item.application_id, "preference": item.preference, "accommodation_needs": item.accommodation_needs, "status": item.status} for item in ResidenceApplication.objects.filter(application__user=request.user).select_related("application")],
        "consent_history": [{"policy_version": item.policy_version, "purpose": item.purpose, "granted_at": item.granted_at.isoformat()} for item in DataConsent.objects.filter(user=request.user)],
    }
    response = HttpResponse(json.dumps(payload, ensure_ascii=False, indent=2), content_type="application/json")
    response["Content-Disposition"] = 'attachment; filename="unipath-personal-data.json"'
    response["Cache-Control"] = "no-store"
    return response

@require_POST
@otp_api
def delete_account(request):
    body, error = read_json(request)
    if error:
        return error
    if not request.user.check_password(str(body.get("password", ""))):
        return JsonResponse({"error": "Password confirmation failed."}, status=403)
    device = getattr(request.user, "otp_device", None)
    if device is None or not device.verify_token(str(body.get("otp_token", ""))):
        return JsonResponse({"error": "Enter a current authenticator code to confirm deletion."}, status=403)
    user = request.user
    logout(request)
    user.delete()
    return JsonResponse({"deleted": True})
