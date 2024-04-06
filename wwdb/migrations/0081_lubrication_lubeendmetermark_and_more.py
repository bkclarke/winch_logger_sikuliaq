# Generated by Django 4.1.3 on 2024-04-05 02:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wwdb", "0080_remove_wire_winch_alter_wire_dateacquired"),
    ]

    operations = [
        migrations.AddField(
            model_name="lubrication",
            name="lubeendmetermark",
            field=models.IntegerField(
                blank=True,
                db_column="LubeEndMeterMark",
                null=True,
                verbose_name="End meter mark",
            ),
        ),
        migrations.AddField(
            model_name="lubrication",
            name="lubestartmetermark",
            field=models.IntegerField(
                blank=True,
                db_column="LubeStartMeterMark",
                null=True,
                verbose_name="Start meter mark",
            ),
        ),
    ]