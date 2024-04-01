# Generated by Django 4.1.3 on 2024-03-07 10:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("wwdb", "0074_alter_cast_deploymenttype_alter_cast_endoperator_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="TerminationType",
            fields=[
                (
                    "id",
                    models.AutoField(db_column="Id", primary_key=True, serialize=False),
                ),
                (
                    "name",
                    models.IntegerField(
                        blank=True, db_column="Name", verbose_name="Termination Type"
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "TerminationType",
                "db_table": "TerminationType",
                "managed": True,
            },
        ),
        migrations.AlterModelOptions(
            name="deploymenttype",
            options={
                "managed": True,
                "ordering": ["name"],
                "verbose_name_plural": "DeploymentType",
            },
        ),
        migrations.AlterModelOptions(
            name="location",
            options={
                "managed": True,
                "ordering": ["location"],
                "verbose_name_plural": "Location",
            },
        ),
        migrations.AlterModelOptions(
            name="winch",
            options={
                "managed": True,
                "ordering": ["name"],
                "verbose_name_plural": "Winch",
            },
        ),
        migrations.AlterModelOptions(
            name="winchoperator",
            options={
                "managed": True,
                "ordering": ["username"],
                "verbose_name_plural": "WinchOperator",
            },
        ),
        migrations.RemoveField(
            model_name="cruise",
            name="winch1",
        ),
        migrations.RemoveField(
            model_name="cruise",
            name="winch2",
        ),
        migrations.RemoveField(
            model_name="cruise",
            name="winch3",
        ),
        migrations.AddField(
            model_name="cutbackretermination",
            name="terminationtype",
            field=models.ForeignKey(
                blank=True,
                db_column="TerminationType",
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="wire_termination_type",
                to="wwdb.terminationtype",
                verbose_name="Termination Type",
            ),
        ),
    ]
