import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("otp_totp", "0001_initial"),
        ("applications", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="MobileSession",
            fields=[
                ("token_digest", models.CharField(max_length=64, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("expires_at", models.DateTimeField(db_index=True)),
                ("revoked_at", models.DateTimeField(blank=True, null=True)),
                ("otp_device", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="mobile_sessions", to="otp_totp.totpdevice")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="mobile_sessions", to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
