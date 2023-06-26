# Generated by Django 4.1.7 on 2023-06-26 15:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ads", "0011_rename_is_active_ad_is_approved"),
    ]

    operations = [
        migrations.AlterField(
            model_name="adimage",
            name="image",
            field=models.FileField(
                help_text="The image of a particular ad.",
                upload_to="ad_images/",
            ),
        ),
    ]
