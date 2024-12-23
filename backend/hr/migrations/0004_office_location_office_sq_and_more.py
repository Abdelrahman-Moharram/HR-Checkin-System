# Generated by Django 5.0.6 on 2024-12-23 17:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hr', '0003_alter_office_location_location_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='office_location',
            name='office_sq',
            field=models.FloatField(default=0),
        ),
        migrations.AlterUniqueTogether(
            name='location',
            unique_together={('latitude', 'longitude')},
        ),
    ]
