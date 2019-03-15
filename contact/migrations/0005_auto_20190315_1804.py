# Generated by Django 2.1.7 on 2019-03-15 18:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("contact", "0004_auto_20190315_1617")]

    operations = [
        migrations.AlterField(
            model_name="emailreply",
            name="reply_to",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="replies",
                to="contact.EmailMessageInstance",
            ),
        )
    ]
