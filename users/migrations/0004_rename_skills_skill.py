# Generated by Django 4.2.6 on 2023-10-28 06:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_profile_location_skills'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Skills',
            new_name='Skill',
        ),
    ]
