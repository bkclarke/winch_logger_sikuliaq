# Generated by Django 4.1.3 on 2024-07-26 03:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wwdb", "0085_alter_wire_dateacquired_alter_wire_wirerope"),
    ]

    operations = [
        migrations.AddField(
            model_name="cast",
            name="factorofsafety",
            field=models.FloatField(
                db_column="FactorofSafety", null=True, verbose_name="Factor of safety"
            ),
        ),
        migrations.AddField(
            model_name="cast",
            name="safeworkingtension",
            field=models.FloatField(
                db_column="SafeWorkingTension",
                null=True,
                verbose_name="Safe Working tension",
            ),
        ),
        migrations.AddField(
            model_name="cast",
            name="wirelength",
            field=models.IntegerField(
                blank=True,
                db_column="WireLength",
                null=True,
                verbose_name="Wire length",
            ),
        ),
    ]