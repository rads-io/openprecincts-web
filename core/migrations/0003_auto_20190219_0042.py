# Generated by Django 2.1.7 on 2019-02-19 00:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("core", "0002_load_data")]

    operations = [
        migrations.RemoveField(model_name="state", name="precinct_plan"),
        migrations.AddField(
            model_name="state",
            name="task_collect",
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AddField(
            model_name="state",
            name="task_contact",
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AddField(
            model_name="state",
            name="task_digitization",
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AddField(
            model_name="state",
            name="task_files",
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AddField(
            model_name="state",
            name="task_published",
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AddField(
            model_name="state",
            name="task_verification",
            field=models.BooleanField(default=None, null=True),
        ),
    ]
