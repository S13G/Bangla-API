from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from common.models import BaseModel
from core.validators import validate_phone_number
from .managers import CustomUserManager


class User(BaseModel, AbstractUser):
    username = None
    first_name = None
    last_name = None
    full_name = models.CharField(max_length=255, null=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, validators=[validate_phone_number], null=True)
    is_verified = models.BooleanField(
            default=False, help_text=_("Indicates whether the user's email is verified.")
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name", "phone_number"]

    objects = CustomUserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"


class Otp(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="otp",
                             help_text=_("The user associated with this OTP."))
    code = models.PositiveIntegerField(null=True, help_text=_("The OTP code."))
    expired = models.BooleanField(default=False, help_text=_("Indicates whether the OTP has expired."))
    expiry_date = models.DateTimeField(null=True, auto_now_add=True, editable=False,
                                       help_text=_("The date and time when the OTP will expire."))

    def __str__(self):
        return f"{self.user.full_name} ----- {self.code}"

    def save(self, *args, **kwargs):
        # Increase the expiry date of the OTP by 15 minutes
        self.expiry_date += timezone.timedelta(minutes=15)

        # Check if the current time is the same as the expiry date
        if timezone.now() == self.expiry_date:
            # If the OTP has expired, mark it as expired and delete it
            self.expired = True
            self.delete()

        # Save the OTP model
        super().save(*args, **kwargs)


class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile",
                                help_text=_("The user associated with this profile."))
    description = models.TextField(blank=True)
    country = CountryField(null=True)
    language = models.CharField(max_length=255)
    avatar = models.URLField(help_text=_("The avatar image of the user."), blank=True)

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __str__(self):
        return self.user.full_name

    @property
    def profile_avatar(self):
        if self.avatar is not None:
            return self.avatar
        return None

    @property
    def email_address(self):
        return self.user.email

    @property
    def full_name(self):
        return self.user.full_name
