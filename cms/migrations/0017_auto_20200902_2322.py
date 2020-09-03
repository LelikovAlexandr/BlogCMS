# Generated by Django 3.0.6 on 2020-09-02 23:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0016_auto_20200902_2240'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='category', to='cms.ArticleCategory'),
        ),
        migrations.AlterField(
            model_name='articlecategory',
            name='name',
            field=models.CharField(max_length=150),
        ),
    ]
