# Generated by Django 4.1.3 on 2023-03-05 21:58

import datetime
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wwdb", "0059_alter_cast_startdate"),
    ]

    operations = [
        migrations.AlterField(
            model_name="breaktest",
            name="date",
            field=models.DateTimeField(
                blank=True,
                db_column="Date",
                null=True,
                validators=[
                    django.core.validators.MaxValueValidator(
                        limit_value=datetime.datetime.today
                    )
                ],
                verbose_name="Date",
            ),
        ),
        migrations.AlterField(
            model_name="calibrationmeta",
            name="date",
            field=models.DateField(
                blank=True,
                db_column="Date",
                null=True,
                validators=[
                    django.core.validators.MaxValueValidator(
                        limit_value=datetime.date.today
                    )
                ],
                verbose_name="Date",
            ),
        ),
        migrations.AlterField(
            model_name="cruise",
            name="startdate",
            field=models.DateField(
                blank=True,
                db_column="StartDate",
                null=True,
                validators=[
                    django.core.validators.MaxValueValidator(
                        limit_value=datetime.date.today
                    )
                ],
                verbose_name="Start date",
            ),
        ),
        migrations.AlterField(
            model_name="cutbackretermination",
            name="date",
            field=models.DateField(
                blank=True,
                db_column="Date",
                null=True,
                validators=[
                    django.core.validators.MaxValueValidator(
                        limit_value=datetime.date.today
                    )
                ],
                verbose_name="Date",
            ),
        ),
        migrations.AlterField(
            model_name="drumlocation",
            name="date",
            field=models.DateField(
                blank=True,
                db_column="Date",
                null=True,
                validators=[
                    django.core.validators.MaxValueValidator(
                        limit_value=datetime.date.today
                    )
                ],
                verbose_name="Date",
            ),
        ),
        migrations.AlterField(
            model_name="lubrication",
            name="date",
            field=models.DateField(
                blank=True,
                db_column="Date",
                null=True,
                validators=[
                    django.core.validators.MaxValueValidator(
                        limit_value=datetime.date.today
                    )
                ],
                verbose_name="Date",
            ),
        ),
        migrations.AlterField(
            model_name="wire",
            name="dateacquired",
            field=models.DateTimeField(
                blank=True,
                db_column="DateAcquired",
                null=True,
                validators=[
                    django.core.validators.MaxValueValidator(
                        limit_value=datetime.datetime.today
                    )
                ],
                verbose_name="Date Acquired",
            ),
        ),
        migrations.AlterField(
            model_name="wiredrum",
            name="date",
            field=models.DateField(
                blank=True,
                db_column="Date",
                null=True,
                validators=[
                    django.core.validators.MaxValueValidator(
                        limit_value=datetime.date.today
                    )
                ],
                verbose_name="Date",
            ),
        ),
    ]
