from __future__ import unicode_literals

import utils
import validators
from django.db import models
from django.utils import timezone
import datetime


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

    def get_current_playlistchannels(self, wrapper=None):
        plcs = self.playlistchannel_set.filter(
            models.Q(livechannel__source__end_dt__isnull=True) |
            models.Q(
                livechannel__source__end_dt__gte=timezone.now() - datetime.timedelta(minutes=10),
                livechannel__source__start_dt__lte=timezone.now() + datetime.timedelta(minutes=10)
            )
        )
        for plc in plcs:
            wrapped_stream_url = plc.livechannel.get_wrapped_stream_url(wrapper=wrapper)
            plc.wrapped_stream_url = wrapped_stream_url
        return plcs

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
        naming = self.playlist.channel_naming
        try:
            scraper_display = self.livechannel.source.htmlscraper.display_name
        except AttributeError:
            scraper_display = ''
            if '%(scraper)s' in naming:
                naming = naming.replace('%(scraper)s - ', '')

        return naming % {
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

    def get_wrapped_stream_url(self, wrapper=None):
        stream_url = self.source.stream_url
        wrapper_string = self.source.get_wrapper_string(wrapper=wrapper)
        return wrapper_string % {'stream_url': stream_url, 'logo_url': self.source.stream_logo_url}

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
    stream_logo_url = models.CharField(max_length=500, null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    start_dt = models.DateTimeField(null=True, blank=True)
    end_dt = models.DateTimeField(null=True, blank=True)

    def currently_live(self):
        if self.start_dt and self.end_dt:
            start = self.start_dt
            end = self.end_dt
            return start <= timezone.now() <= end

    def get_wrapper_string(self, wrapper=None):
        if wrapper:
            return wrapper.stream_url_wrap
        if self.wrapper_id:
            return self.wrapper.stream_url_wrap
        return '%(stream_url)s'

    def __unicode__(self):
        return self.name


class SourceWrapper(models.Model):
    name = models.CharField(max_length=500)
    stream_url_wrap = models.CharField(
        max_length=500, default='%(stream_url)s',
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
    scraper_type = models.CharField(
        choices=(
            ('ZDFScraperPage', 'ZDFScraperPage'),
        ),
        null=True, blank=True,
        max_length=255
    )

    def __unicode__(self):
        return self.name

    def scrape(self, **kwargs):
        return utils.process_scraper(scraper=self, **kwargs)

    def get_title_xpaths(self):
        if self.title_xpaths:
            return self.title_xpaths.split(',')
        return []

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
            LiveChannel.objects.filter(source__htmlscraper_id=scraper.id, source__end_dt__lte=timezone.now()).delete()
            current_livechannels = LiveChannel.objects.filter(
                source__htmlscraper_id=scraper.id
            ).order_by('source__start_dt')
            for lc in current_livechannels:
                new_pos = self.playlist.playlistchannel_set.aggregate(max_pos=models.Max('position')).get('max_pos', 0) + 1
                pc, pc_created = self.playlist.playlistchannel_set.get_or_create(
                    livechannel=lc,
                    defaults={
                        'position': new_pos
                    }
                )
            #for ex_plc in self.playlist.playlistchannel_set.filter(source__htmlscraper_id=scraper.id):
            #    if ex_plc.livechannel not in current_livechannels:
            #        ex_plc.delete()

        return created_livechannels



