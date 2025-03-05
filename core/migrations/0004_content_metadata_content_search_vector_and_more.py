# Generated by Django 5.1.6 on 2025-03-05 05:50

import django.contrib.postgres.search
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_comment_is_approved'),
    ]

    operations = [
        migrations.AddField(
            model_name='content',
            name='metadata',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='content',
            name='search_vector',
            field=django.contrib.postgres.search.SearchVectorField(null=True),
        ),
        migrations.AlterField(
            model_name='content',
            name='title',
            field=models.CharField(db_index=True, max_length=200),
        ),
    ]
