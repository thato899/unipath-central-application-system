from django.conf import settings
from django.db import models
from django_otp.plugins.otp_totp.models import TOTPDevice
from .fields import EncryptedJSONField, EncryptedTextField

class DataConsent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="data_consents")
    policy_version = models.CharField(max_length=32)
    purpose = models.CharField(max_length=80)
    granted_at = models.DateTimeField(auto_now_add=True)

class ApplicantProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="applicant_profile")
    data = EncryptedJSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)

class Application(models.Model):
    STATUS_CHOICES = [(value, value.replace("_", " ").title()) for value in ("offer_received", "in_review", "accepted", "rejected")]
    id = models.CharField(primary_key=True, max_length=8)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="applications")
    course_id = models.CharField(max_length=100)
    course_name = models.CharField(max_length=180)
    university_id = models.CharField(max_length=100)
    university_name = models.CharField(max_length=180)
    status = models.CharField(max_length=24, choices=STATUS_CHOICES)
    decision = models.CharField(max_length=16, null=True, blank=True)
    demo_response = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("user", "course_id", "university_id"), name="unique_user_course_university")]
        ordering = ("-created_at",)

class ResidenceApplication(models.Model):
    PREFERENCES = [(value, value) for value in ("On-campus residence", "Off-campus accommodation support", "Either option")]
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name="residence_request")
    preference = models.CharField(max_length=48, choices=PREFERENCES)
    accommodation_needs = EncryptedTextField(blank=True, default="")
    status = models.CharField(max_length=32, default="request_recorded_demo")
    created_at = models.DateTimeField(auto_now_add=True)

class MobileSession(models.Model):
    """Hashed bearer credential tied to a confirmed TOTP device."""
    token_digest = models.CharField(max_length=64, primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mobile_sessions")
    otp_device = models.ForeignKey(TOTPDevice, on_delete=models.CASCADE, related_name="mobile_sessions")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(db_index=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
