# Generated by Django 4.1.7 on 2023-07-10 15:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0005_rename__avatar_profile_avatar"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="avatar",
            field=models.URLField(
                blank=True, help_text="The avatar image of the user."
            ),
        ),
    ]
