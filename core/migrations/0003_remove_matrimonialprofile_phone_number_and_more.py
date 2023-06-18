# Generated by Django 4.1.7 on 2023-06-14 17:53

import core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_rename_short_bio_profile_description_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="matrimonialprofile",
            name="phone_number",
        ),
        migrations.RemoveField(
            model_name="profile",
            name="phone_number",
        ),
        migrations.AddField(
            model_name="user",
            name="is_verified",
            field=models.BooleanField(
                default=False,
                help_text="Indicates whether the user's email is verified.",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="phone_number",
            field=models.CharField(
                max_length=20,
                null=True,
                validators=[core.validators.validate_phone_number],
            ),
        ),
    ]