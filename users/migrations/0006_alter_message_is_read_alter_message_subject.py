# Generated by Django 4.2.6 on 2023-11-01 05:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_message'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='is_read',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AlterField(
            model_name='message',
            name='subject',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
