# Generated by Django 4.2.11 on 2024-03-21 14:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Emotional_Analysis', '0002_confirmstring_user_delete_userinfo_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={},
        ),
        migrations.RemoveField(
            model_name='user',
            name='c_time',
        ),
        migrations.RemoveField(
            model_name='user',
            name='email',
        ),
        migrations.RemoveField(
            model_name='user',
            name='has_confirmed',
        ),
        migrations.DeleteModel(
            name='ConfirmString',
        ),
    ]
