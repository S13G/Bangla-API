from django.contrib.auth import get_user_model
from django.db import models
from django_countries.fields import CountryField

from common.models import BaseModel
from core.choices import GENDER_CHOICES
from matrimonials.choices import CONNECTION_CHOICES, CONNECTION_PENDING, EDUCATION_CHOICES, RELIGION_CHOICES

User = get_user_model()


# Create your models here.

class MatrimonialProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="matrimonial_profile")
    short_bio = models.TextField(blank=True)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=255, choices=GENDER_CHOICES)
    height = models.CharField(max_length=255, blank=True)
    country = CountryField(null=True)
    city = models.CharField(max_length=255)
    religion = models.CharField(max_length=1, choices=RELIGION_CHOICES, null=True)
    birthday = models.DateField(blank=True)
    education = models.CharField(max_length=2, choices=EDUCATION_CHOICES, null=True)
    profession = models.CharField(max_length=255, blank=True)
    income = models.PositiveIntegerField(blank=True)

    class Meta:
        verbose_name_plural = "Matrimonial Profiles"

    def __str__(self):
        return self.user.full_name

    @property
    def email_address(self):
        return self.user.email_address

    @property
    def full_name(self):
        return self.user.full_name


class MatrimonialProfileImage(BaseModel):
    matrimonial_profile = models.ForeignKey(MatrimonialProfile, on_delete=models.CASCADE, related_name="images",
                                            null=True)
    image = models.ImageField(upload_to="matrimonial_images/", null=True)

    @property
    def matrimonial_image(self):
        if self.image is not None:
            return self.image.url
        return None

    def __str__(self):
        return str(self.matrimonial_profile.full_name)


class BookmarkedProfile(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="bookmarked_matrimonial_profile")
    profile = models.ForeignKey(MatrimonialProfile, on_delete=models.CASCADE, null=True,
                                related_name="bookmarked_profile")

    def __str__(self):
        return str(self.user.full_name)


class ConnectionRequest(BaseModel):
    sender = models.ForeignKey(MatrimonialProfile, on_delete=models.CASCADE, related_name="connection_requests_sender")
    receiver = models.ForeignKey(MatrimonialProfile, on_delete=models.CASCADE,
                                 related_name="connection_requests_receiver")
    status = models.CharField(max_length=1, choices=CONNECTION_CHOICES, default=CONNECTION_PENDING)

    def __str__(self):
        return f"{self.sender} --- {self.receiver} --- {self.status}"


class Conversation(BaseModel):
    initiator = models.ForeignKey(MatrimonialProfile, on_delete=models.CASCADE, related_name="conversations_initiator")
    receiver = models.ForeignKey(MatrimonialProfile, on_delete=models.CASCADE, related_name="conversations_receiver")


class Message(BaseModel):
    sender = models.ForeignKey(MatrimonialProfile, on_delete=models.CASCADE, related_name="message_sender")
    text = models.CharField(max_length=200, blank=True)
    attachment = models.FileField(blank=True)
    conversation_id = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
