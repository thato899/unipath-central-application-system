import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
import applications.fields

class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="DataConsent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("policy_version", models.CharField(max_length=32)),
                ("purpose", models.CharField(max_length=80)),
                ("granted_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="data_consents", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="ApplicantProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("data", applications.fields.EncryptedJSONField(default=dict)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="applicant_profile", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Application",
            fields=[
                ("id", models.CharField(max_length=8, primary_key=True, serialize=False)),
                ("course_id", models.CharField(max_length=100)),
                ("course_name", models.CharField(max_length=180)),
                ("university_id", models.CharField(max_length=100)),
                ("university_name", models.CharField(max_length=180)),
                ("status", models.CharField(choices=[("offer_received", "Offer Received"), ("in_review", "In Review"), ("accepted", "Accepted"), ("rejected", "Rejected")], max_length=24)),
                ("decision", models.CharField(blank=True, max_length=16, null=True)),
                ("demo_response", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="applications", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-created_at",)},
        ),
        migrations.CreateModel(
            name="ResidenceApplication",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("preference", models.CharField(choices=[("On-campus residence", "On-campus residence"), ("Off-campus accommodation support", "Off-campus accommodation support"), ("Either option", "Either option")], max_length=48)),
                ("accommodation_needs", applications.fields.EncryptedTextField(blank=True, default="")),
                ("status", models.CharField(default="request_recorded_demo", max_length=32)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("application", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="residence_request", to="applications.application")),
            ],
        ),
        migrations.AddConstraint(
            model_name="application",
            constraint=models.UniqueConstraint(fields=("user", "course_id", "university_id"), name="unique_user_course_university"),
        ),
    ]
