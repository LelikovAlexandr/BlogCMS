# Generated by Django 3.0.6 on 2020-06-01 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_init_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='init_password',
            field=models.CharField(default='a6lJ7biY', max_length=10),
        ),
    ]
