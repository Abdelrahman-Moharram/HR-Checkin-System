# Generated by Django 5.0.6 on 2024-12-23 20:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hr', '0004_office_location_office_sq_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='office_location',
            unique_together={('office', 'is_present', 'location')},
        ),
    ]
