# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-04 16:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('liveplaylist', '0002_htmlscraper_title_xpaths'),
    ]

    operations = [
        migrations.AddField(
            model_name='htmlscraper',
            name='default_wrapper',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='liveplaylist.SourceWrapper'),
        ),
        migrations.AddField(
            model_name='htmlscraper',
            name='filter_title_contains',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
