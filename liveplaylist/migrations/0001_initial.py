# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-04 15:17
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import liveplaylist.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='HTMLScraper',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('main_page_url', models.URLField()),
                ('main_page_find_subpages_xpath', models.CharField(max_length=255)),
                ('subpage_find_stream_xpath', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='LiveChannel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='LiveSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('stream_url', models.CharField(max_length=255)),
                ('htmlscraper', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='liveplaylist.HTMLScraper')),
            ],
        ),
        migrations.CreateModel(
            name='Playlist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('public', models.BooleanField(default=False)),
                ('channel_naming', models.CharField(choices=[('%(playlist)s - %(channel)s', '<Name Playlist> - <Name Kanal>'), ('%(playlist)s - %(position)d', '<Name Playlist> - <Position Kanal>'), ('%(playlist)s - %(position)d - %(channel)s', '<Name Playlist> - <Position Kanal> - <Name Kanal>')], max_length=255)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PlaylistChannel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.PositiveIntegerField()),
                ('livechannel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='liveplaylist.LiveChannel')),
                ('playlist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='liveplaylist.Playlist')),
            ],
            options={
                'ordering': ('playlist', 'position'),
            },
        ),
        migrations.CreateModel(
            name='SourceWrapper',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('stream_url_wrap', models.CharField(default='%(stream_url)s', max_length=255, validators=[liveplaylist.validators.validate_wrapper_string])),
            ],
        ),
        migrations.AddField(
            model_name='livesource',
            name='wrapper',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='liveplaylist.SourceWrapper'),
        ),
        migrations.AddField(
            model_name='livechannel',
            name='source',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='liveplaylist.LiveSource'),
        ),
        migrations.AlterUniqueTogether(
            name='playlistchannel',
            unique_together=set([('playlist', 'livechannel', 'position')]),
        ),
        migrations.AlterUniqueTogether(
            name='playlist',
            unique_together=set([('name', 'owner')]),
        ),
        migrations.AlterUniqueTogether(
            name='livechannel',
            unique_together=set([('name', 'source')]),
        ),
    ]
