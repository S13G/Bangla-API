# Generated by Django 4.1.7 on 2023-06-12 14:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("ads", "0002_rename_adimages_adimage_ad_category_ad_condition_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="ad",
            name="ad_creator",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="created_ads",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="favouritead",
            name="customer",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="favourite_ads",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
