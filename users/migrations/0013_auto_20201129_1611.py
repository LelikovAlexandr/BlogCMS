# Generated by Django 3.1.2 on 2020-11-29 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_auto_20201129_1555'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='name_for_refund',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='ФИО'),
        ),
        migrations.AlterField(
            model_name='user',
            name='card_number',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Номер карты'),
        ),
    ]