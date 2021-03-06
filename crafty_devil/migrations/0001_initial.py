# Generated by Django 3.0.3 on 2020-05-14 11:41

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstname', models.CharField(max_length=30)),
                ('lastname', models.CharField(max_length=30)),
                ('password', models.CharField(max_length=30)),
                ('role', models.CharField(max_length=20)),
                ('address_line1', models.CharField(max_length=30)),
                ('address_line2', models.CharField(max_length=30)),
                ('post_code', models.CharField(max_length=8)),
                ('city', models.CharField(max_length=20)),
                ('email', models.CharField(max_length=30)),
            ],
            options={
                'db_table': 'Customers',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.datetime(2020, 5, 14, 12, 41, 50, 440497))),
                ('total', models.FloatField(default=0)),
                ('status', models.CharField(default='in basket', max_length=12)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crafty_devil.Customer')),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cardholder_name', models.CharField(max_length=30)),
                ('card_number', models.CharField(max_length=16)),
                ('expiry_date', models.CharField(max_length=7)),
                ('security_number', models.CharField(max_length=3)),
            ],
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstname', models.CharField(max_length=30)),
                ('lastname', models.CharField(max_length=30)),
                ('password', models.CharField(max_length=30)),
                ('role', models.CharField(max_length=30)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
                ('address_1', models.CharField(max_length=30, verbose_name='Address Line 1')),
                ('address_2', models.CharField(max_length=30, verbose_name='Address Line 2')),
                ('post_code', models.CharField(max_length=7, verbose_name='Post Code')),
                ('city', models.CharField(max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('desc', models.CharField(max_length=200)),
                ('stock_level', models.IntegerField()),
                ('price', models.FloatField()),
                ('image_path', models.CharField(default='product_soon.jpg', max_length=50, null=True)),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crafty_devil.Supplier')),
            ],
        ),
        migrations.CreateModel(
            name='OrderLine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('line_total', models.FloatField()),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crafty_devil.Order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crafty_devil.Product')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='payment',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='crafty_devil.Payment'),
        ),
        migrations.AddField(
            model_name='order',
            name='staff',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='crafty_devil.Staff'),
        ),
    ]
