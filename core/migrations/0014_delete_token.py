# Generated by Django 4.1.7 on 2023-05-21 13:13

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0013_token"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Token",
        ),
    ]
