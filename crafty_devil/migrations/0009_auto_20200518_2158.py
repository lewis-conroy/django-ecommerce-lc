# Generated by Django 3.0.3 on 2020-05-18 20:58

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('crafty_devil', '0008_auto_20200518_1407'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crafty_devil.Customer'),
        ),
        migrations.AlterField(
            model_name='order',
            name='date',
            field=models.DateField(default=datetime.datetime(2020, 5, 18, 21, 58, 8, 152387)),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='crafty_devil.Payment'),
        ),
        migrations.AlterField(
            model_name='order',
            name='staff',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='crafty_devil.Staff'),
        ),
        migrations.AlterField(
            model_name='orderline',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crafty_devil.Product'),
        ),
        migrations.AlterField(
            model_name='product',
            name='supplier',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crafty_devil.Supplier'),
        ),
    ]
