# Generated by Django 4.1 on 2022-09-07 22:00

from django.db import migrations, models
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0002_answer_choice_answer_pub_date'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='answer',
            managers=[
                ('sessions', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AddField(
            model_name='answer',
            name='time',
            field=models.IntegerField(default=0),
        ),
    ]
