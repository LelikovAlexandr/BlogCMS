# Generated by Django 3.0.6 on 2020-09-04 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_auto_20200525_1353'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='is_recurrent',
            field=models.BooleanField(default=False),
        ),
    ]
