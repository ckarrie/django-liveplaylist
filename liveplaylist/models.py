from __future__ import unicode_literals

import utils
import validators
from django.db import models


class Playlist(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey('auth.User')
    public = models.BooleanField(default=False)
    channel_naming = models.CharField(max_length=255, choices=(
        ('%(channel)s', '<Name Kanal>'),
        ('%(playlist)s - %(channel)s', '<Name Playlist> - <Name Kanal>'),
        ('%(scraper)s - %(channel)s', '<Name Scraper> - <Name Kanal>'),
        ('%(playlist)s - %(position)d', '<Name Playlist> - <Position Kanal>'),
        ('%(playlist)s - %(position)d - %(channel)s', '<Name Playlist> - <Position Kanal> - <Name Kanal>'),
        ('%(playlist)s - %(extra)s %(position)d - %(channel)s', '<Name Playlist> - <Extra> <Position Kanal> - <Name Kanal>'),
    ))
    channel_naming_extra = models.CharField(max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.name

    def get_m3u(self):
        return utils.get_m3u(self)

    @models.permalink
    def get_m3u_url(self):
        return ('pl_m3u', None, {'pk': self.pk},)

    class Meta:
        unique_together = ('name', 'owner')


class PlaylistChannel(models.Model):
    playlist = models.ForeignKey('liveplaylist.Playlist')
    livechannel = models.ForeignKey('liveplaylist.LiveChannel')
    position = models.PositiveIntegerField()

    def get_entry_name(self):
        scraper_display = self.livechannel.source.htmlscraper.display_name
        return self.playlist.channel_naming % {
            'playlist': self.playlist.name,
            'channel': self.livechannel.name,
            'position': self.position,
            'extra': self.playlist.channel_naming_extra,
            'scraper': scraper_display
        }

    def __unicode__(self):
        return u'%(pl)s #%(pos)d %(ch)s' % {'pl': self.playlist.name, 'pos': self.position, 'ch': self.livechannel.name}

    class Meta:
        unique_together = ('playlist', 'livechannel', 'position')
        ordering = ('playlist', 'position')


class LiveChannel(models.Model):
    name = models.CharField(max_length=255)
    source = models.ForeignKey('liveplaylist.LiveSource')

    def get_wrapped_stream_url(self):
        stream_url = self.source.stream_url
        wrapper_string = self.source.get_wrapper_string()
        return wrapper_string % {'stream_url': stream_url}

    def get_unwrapped_stream_url(self):
        stream_url = self.source.stream_url
        return stream_url

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'source')
        ordering = ('name',)


class LiveSource(models.Model):
    name = models.CharField(max_length=255)
    htmlscraper = models.ForeignKey('liveplaylist.HTMLScraper', null=True, blank=True)
    wrapper = models.ForeignKey('liveplaylist.SourceWrapper', null=True, blank=True)
    stream_url = models.CharField(max_length=255)
    last_updated = models.DateTimeField(auto_now=True)

    def get_wrapper_string(self):
        if self.wrapper_id:
            return self.wrapper.stream_url_wrap
        return '%(stream_url)s'

    def __unicode__(self):
        return self.name


class SourceWrapper(models.Model):
    name = models.CharField(max_length=255)
    stream_url_wrap = models.CharField(
        max_length=255, default='%(stream_url)s',
        validators=[validators.validate_wrapper_string]
    )

    def __unicode__(self):
        return self.name


class HTMLScraper(models.Model):
    name = models.CharField(max_length=255)
    display_name = models.CharField(max_length=100, default='')
    main_page_url = models.URLField()
    main_page_find_stream_xpath = models.CharField(max_length=255, null=True, blank=True)
    main_page_find_subpages_xpath = models.CharField(max_length=255, null=True, blank=True)
    subpage_find_stream_xpath = models.CharField(max_length=255, null=True, blank=True)
    title_xpaths = models.CharField(max_length=255, null=True, blank=True)
    filter_title_contains = models.CharField(max_length=255, null=True, blank=True)
    default_wrapper = models.ForeignKey(SourceWrapper, null=True, blank=True)

    def __unicode__(self):
        return self.name

    def scrape(self, **kwargs):
        return utils.process_scraper(scraper=self, **kwargs)

    class Meta:
        ordering = ('name', 'main_page_url',)


class PlaylistUpdate(models.Model):
    playlist = models.ForeignKey(Playlist)
    htmlscrapers = models.ManyToManyField(HTMLScraper)
    delete_obsolete_streams = models.BooleanField(default=True)
    livechannel_naming = models.IntegerField(choices=(
        (None, 'Full title_xpaths'),
        (0, 'First title_xpath'),
        (1, 'Second title_xpath'),
        (2, 'Third title_xpath'),
    ))

    def update_playlist(self):
        created_livechannels = []
        for scraper in self.htmlscrapers.all():
            scraper_results = scraper.scrape(
                livechannel_title_index=self.livechannel_naming,
                delete_obsolete_streams=self.delete_obsolete_streams
            )
            created_livechannels.extend(scraper_results['created_livechannels'])

        for lc in created_livechannels:
            new_pos = self.playlist.playlistchannel_set.aggregate(max_pos=models.Max('position')).get('max_pos', 0) + 1
            self.playlist.playlistchannel_set.create(
                livechannel=lc,
                position=new_pos
            )

        return created_livechannels



