"""Short-lived bearer sessions for the native mobile client."""
import hashlib
import secrets
from datetime import timedelta

from django.core.cache import cache
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django_otp.plugins.otp_totp.models import TOTPDevice

from .api import otp_api, read_json
from .models import MobileSession


@require_POST
@csrf_exempt
def mobile_login(request):
    body, error = read_json(request)
    if error:
        return error
    email = str(body.get("email", "")).strip().lower()
    password = str(body.get("password", ""))
    token = str(body.get("otp_token", "")).strip()
    rate_key = "mobile-login:" + hashlib.sha256(f"{request.META.get('REMOTE_ADDR', '')}:{email}".encode("utf-8")).hexdigest()
    if cache.get(rate_key, 0) >= 5:
        return JsonResponse({"error": "Too many sign-in attempts. Wait 15 minutes, then try again."}, status=429)
    user = authenticate(request, username=email, password=password)
    if not user or not user.is_active:
        cache.add(rate_key, 0, timeout=900)
        cache.incr(rate_key)
        return JsonResponse({"error": "Email or password was not accepted."}, status=401)
    devices = TOTPDevice.objects.filter(user=user, confirmed=True)
    verified_device = next((device for device in devices if device.verify_token(token)), None)
    if verified_device is None:
        cache.add(rate_key, 0, timeout=900)
        cache.incr(rate_key)
        return JsonResponse({"error": "Authenticator code was not accepted."}, status=401)
    cache.delete(rate_key)

    MobileSession.objects.filter(expires_at__lte=timezone.now()).delete()
    raw_token = secrets.token_urlsafe(32)
    expires_at = timezone.now() + timedelta(hours=8)
    MobileSession.objects.create(
        token_digest=hashlib.sha256(raw_token.encode("utf-8")).hexdigest(),
        user=user,
        otp_device=verified_device,
        expires_at=expires_at,
    )
    response = JsonResponse({
        "access_token": raw_token,
        "token_type": "Bearer",
        "expires_at": expires_at.isoformat(),
        "email": user.email,
    })
    response["Cache-Control"] = "no-store"
    return response


@require_POST
@otp_api
def mobile_logout(request):
    current = getattr(request, "mobile_session", None)
    if current is not None:
        current.revoked_at = timezone.now()
        current.save(update_fields=["revoked_at"])
    return JsonResponse({"logged_out": True})
