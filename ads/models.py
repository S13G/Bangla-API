from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from ads.choices import CONDITION_CHOICES
from common.models import BaseModel

User = get_user_model()


# Create your models here.


class AdCategory(BaseModel):
    title = models.CharField(max_length=255)
    _image = models.ImageField(upload_to="category_images/", null=True)

    class Meta:
        verbose_name_plural = ("Ads Categories",)

    @property
    def category_image(self):
        if self._image is not None:
            return self._image.url
        return None

    def __str__(self):
        return str(self.title)


class AdSubCategory(BaseModel):
    category = models.ForeignKey(AdCategory, on_delete=models.CASCADE, null=True, related_name="sub_categories")
    title = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.category.title} ---- {self.title}"


class Ad(BaseModel):
    ad_creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="created_ads")
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    location = models.CharField(max_length=255)
    category = models.ForeignKey(AdCategory, on_delete=models.CASCADE, null=True, related_name="ads")
    sub_category = models.ForeignKey(AdSubCategory, on_delete=models.CASCADE, null=True, related_name="ads")
    date_and_time = models.DateTimeField(blank=True)
    condition = models.CharField(choices=CONDITION_CHOICES, max_length=1, blank=True)
    featured = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name)


class AdImage(BaseModel):
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, null=True, related_name="images")
    _image = models.ImageField(upload_to="ad_images/", help_text=_("The image of a particular ad."))

    def __str__(self):
        return self.ad.name

    @property
    def image(self):
        if self._image is not None:
            return self._image.url
        return None


class FavouriteAd(BaseModel):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="favourite_ads")
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, null=True, related_name="favourite_ads")

    def __str__(self):
        return f"{self.customer} --- {self.ad.name}"
