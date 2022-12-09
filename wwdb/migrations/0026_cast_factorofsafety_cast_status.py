# Generated by Django 4.1.3 on 2022-12-07 17:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wwdb", "0025_remove_factorofsafety_datetime_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="cast",
            name="factorofsafety",
            field=models.FloatField(
                db_column="FactorofSafety", default=5.0, verbose_name="Factor of safety"
            ),
        ),
        migrations.AddField(
            model_name="cast",
            name="status",
            field=models.BooleanField(
                blank=True, db_column="Status", null=True, verbose_name="Status"
            ),
        ),
    ]
