from django.shortcuts import redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET
from django_otp.plugins.otp_totp.models import TOTPDevice

@require_GET
@ensure_csrf_cookie
def home(request):
    if not request.user.is_authenticated:
        return redirect("login")
    if not request.user.is_verified():
        if TOTPDevice.objects.filter(user=request.user, confirmed=True).exists():
            return redirect("login")
        return redirect("totp_setup")
    return render(request, "index.html")
