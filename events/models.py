from django.db import models

from common.models import BaseModel


# Create your models here.


class EventCategory(BaseModel):
    title = models.CharField(max_length=255)
    _image = models.ImageField(upload_to="categories", null=True)

    class Meta:
        verbose_name_plural = ("Event Categories",)

    @property
    def category_image(self):
        if self._image is not None:
            return self._image.url
        return None

    def __str__(self):
        return str(self.title)


class ProductCategory(BaseModel):
    title = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = ("Product Categories",)

    def __str__(self):
        return str(self.title)


class Product(BaseModel):
    title = models.CharField()
