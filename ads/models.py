from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from ads.choices import CONDITION_CHOICES, STATUS_CHOICES, STATUS_PENDING
from common.models import BaseModel

User = get_user_model()


# Create your models here.


class AdCategory(BaseModel):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to="category_images/", null=True)

    class Meta:
        verbose_name_plural = "Ad Categories"

    @property
    def category_image(self):
        if self.image is not None:
            return self.image.url
        return None

    def __str__(self):
        return str(self.title)


class AdSubCategory(BaseModel):
    category = models.ForeignKey(AdCategory, on_delete=models.CASCADE, null=True, related_name="sub_categories")
    title = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.category.title} ---- {self.title}"

    class Meta:
        verbose_name_plural = "Ad SubCategories"


class Ad(BaseModel):
    ad_creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="created_ads")
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    location = CountryField()
    category = models.ForeignKey(AdCategory, on_delete=models.CASCADE, null=True, related_name="ads")
    featured = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default=STATUS_PENDING, null=True)

    def __str__(self):
        return str(self.name)


class AdImage(BaseModel):
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, null=True, related_name="images")
    image = models.ImageField(upload_to="ad_images/", help_text=_("The image of a particular ad."))

    def __str__(self):
        return self.ad.name

    @property
    def ad_image(self):
        if self.image is not None:
            return self.image.url
        return None


class FavouriteAd(BaseModel):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="favourite_ads")
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, null=True, related_name="favourite_ads")

    def __str__(self):
        return f"{self.customer} --- {self.ad.name}"
