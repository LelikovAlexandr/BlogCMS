# Generated by Django 3.1.2 on 2020-10-05 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0018_price_hidden'),
    ]

    operations = [
        migrations.CreateModel(
            name='Promocode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(default='', max_length=50)),
                ('discount', models.IntegerField()),
                ('owner', models.CharField(default='', max_length=50)),
            ],
        ),
    ]