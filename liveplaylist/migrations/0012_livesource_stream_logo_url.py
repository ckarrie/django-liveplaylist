# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-10 15:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('liveplaylist', '0011_auto_20160809_1129'),
    ]

    operations = [
        migrations.AddField(
            model_name='livesource',
            name='stream_logo_url',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
