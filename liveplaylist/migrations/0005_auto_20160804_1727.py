# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-04 17:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('liveplaylist', '0004_auto_20160804_1658'),
    ]

    operations = [
        migrations.AddField(
            model_name='playlist',
            name='channel_naming_extra',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='playlist',
            name='channel_naming',
            field=models.CharField(choices=[('%(playlist)s - %(channel)s', '<Name Playlist> - <Name Kanal>'), ('%(playlist)s - %(position)d', '<Name Playlist> - <Position Kanal>'), ('%(playlist)s - %(position)d - %(channel)s', '<Name Playlist> - <Position Kanal> - <Name Kanal>'), ('%(playlist)s - %(extra)s %(position)d - %(channel)s', '<Name Playlist> - <Position Kanal> - <Name Kanal>')], max_length=255),
        ),
    ]
