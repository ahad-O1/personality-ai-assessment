import random
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class EmailOTP(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="email_otp"
    )
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_valid(self):
        """Check if OTP is not expired."""
        return timezone.now() <= self.expires_at

    @classmethod
    def create_or_update_otp(cls, user):
        """Generate a 6-digit OTP valid for 10 minutes."""
        otp_code = f"{random.randint(100000, 999999)}"
        expires_at = timezone.now() + timedelta(minutes=10)

        otp_obj, created = cls.objects.get_or_create(
            user=user,
            defaults={"otp_code": otp_code, "expires_at": expires_at}
        )

        if not created:
            otp_obj.otp_code = otp_code
            otp_obj.expires_at = expires_at
            otp_obj.save()

        return otp_obj

    def __str__(self):
        return f"OTP for {self.user.username}: {self.otp_code}"
