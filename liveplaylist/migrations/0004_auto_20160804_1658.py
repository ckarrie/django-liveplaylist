# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-04 16:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('liveplaylist', '0003_auto_20160804_1631'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='livechannel',
            options={'ordering': ('name',)},
        ),
        migrations.AddField(
            model_name='livesource',
            name='last_updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
