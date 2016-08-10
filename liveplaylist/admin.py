from django.contrib import admin

import models


class PlaylistChannelInline(admin.TabularInline):
    model = models.PlaylistChannel


class PlaylistAdmin(admin.ModelAdmin):
    inlines = [PlaylistChannelInline]


class PlaylistChannelAdmin(admin.ModelAdmin):
    list_display = ['playlist', 'livechannel', 'position']


class LiveChannelAdmin(admin.ModelAdmin):
    search_fields = ['name', ]
    list_display = ['name', 'source', 'get_wrapped_stream_url']
    list_filter = ['source__htmlscraper']


class LiveSourceAdmin(admin.ModelAdmin):
    search_fields = ['name', 'stream_url']
    list_display = ['name', 'htmlscraper', 'wrapper', 'stream_url', 'start_dt', 'end_dt']
    list_filter = ['htmlscraper', 'wrapper']


class HTMLScraperAdmin(admin.ModelAdmin):
    search_fields = ['name', ]
    list_display = ['name', 'display_name', 'scraper_type', 'default_wrapper']
    actions = ['scrape_channels', ]

    def scrape_channels(self, request, queryset):
        for obj in queryset:
            obj.scrape()


class PlaylistUpdateAdmin(admin.ModelAdmin):
    actions = ['update_playlist', ]

    def update_playlist(self, request, queryset):
        for obj in queryset:
            obj.update_playlist()


admin.site.register(models.Playlist, PlaylistAdmin)
admin.site.register(models.PlaylistChannel, PlaylistChannelAdmin)
admin.site.register(models.LiveChannel, LiveChannelAdmin)
admin.site.register(models.LiveSource, LiveSourceAdmin)
admin.site.register(models.SourceWrapper)
admin.site.register(models.HTMLScraper, HTMLScraperAdmin)
admin.site.register(models.PlaylistUpdate, PlaylistUpdateAdmin)
