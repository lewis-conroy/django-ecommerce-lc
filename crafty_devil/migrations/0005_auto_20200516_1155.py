# Generated by Django 3.0.3 on 2020-05-16 10:55

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crafty_devil', '0004_auto_20200515_2308'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='date',
            field=models.DateField(default=datetime.datetime(2020, 5, 16, 11, 55, 6, 782191)),
        ),
    ]
