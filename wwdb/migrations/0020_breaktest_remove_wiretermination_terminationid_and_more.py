# Generated by Django 4.0.6 on 2022-09-21 13:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wwdb', '0019_drumlocation_alter_factorofsafety_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Breaktest',
            fields=[
                ('id', models.AutoField(db_column='Id', primary_key=True, serialize=False)),
                ('testdate', models.DateTimeField(blank=True, db_column='TestDate', null=True)),
                ('testedbreakingload', models.IntegerField(blank=True, db_column='TestedBreakingLoad', null=True)),
                ('notes', models.TextField(blank=True, db_column='Notes', null=True)),
                ('wireid', models.ForeignKey(blank=True, db_column='WireId', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='wwdb.wire')),
            ],
            options={
                'verbose_name_plural': 'BreakTest',
                'db_table': 'BreakTest',
                'managed': True,
            },
        ),
        migrations.RemoveField(
            model_name='wiretermination',
            name='terminationid',
        ),
        migrations.RemoveField(
            model_name='wiretermination',
            name='wireid',
        ),
        migrations.RemoveField(
            model_name='cutbackretermination',
            name='terminationid',
        ),
        migrations.DeleteModel(
            name='Termination',
        ),
        migrations.DeleteModel(
            name='Wiretermination',
        ),
    ]
