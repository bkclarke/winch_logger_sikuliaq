# Generated by Django 4.1.3 on 2022-12-31 20:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wwdb", "0039_remove_drumlocation_datetime"),
    ]

    operations = [
        migrations.AddField(
            model_name="drumlocation",
            name="date",
            field=models.DateField(
                blank=True, db_column="Date", null=True, verbose_name="Date"
            ),
        ),
    ]
