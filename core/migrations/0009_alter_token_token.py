# Generated by Django 4.1.7 on 2023-05-20 21:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0008_token_user_tokens"),
    ]

    operations = [
        migrations.AlterField(
            model_name="token",
            name="token",
            field=models.CharField(max_length=500, unique=True),
        ),
    ]
