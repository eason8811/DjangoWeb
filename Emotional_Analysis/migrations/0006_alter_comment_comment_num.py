# Generated by Django 4.2.11 on 2024-03-24 08:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Emotional_Analysis', '0005_alter_comment_comment_num'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='comment_num',
            field=models.IntegerField(max_length=20, primary_key=True, serialize=False),
        ),
    ]
