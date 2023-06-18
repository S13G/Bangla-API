# Generated by Django 4.1.7 on 2023-06-18 00:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("ads", "0004_alter_adcategory_options_alter_adsubcategory_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ad",
            name="sub_category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="ads",
                to="ads.adsubcategory",
            ),
        ),
    ]
