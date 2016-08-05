import models
from django.apps import apps
from django.views import generic
from django.db.models import Q


class IndexView(generic.TemplateView):
    template_name = 'liveplaylist/index.html'

    def get_context_data(self, **kwargs):
        ctx = super(IndexView, self).get_context_data(**kwargs)
        playlists = apps.get_model('liveplaylist.Playlist').objects.all()
        pl_filter = Q(public=True)
        if self.request.user.is_authenticated():
            pl_filter |= Q(owner=self.request.user)
        ctx.update({
            'playlists': playlists.filter(pl_filter),
            'scrapers': apps.get_model('liveplaylist.HTMLScraper').objects.all(),
            'livechannels': apps.get_model('liveplaylist.LiveChannel').objects.all(),
        })
        return ctx


class PlayListM3UView(generic.DetailView):
    template_name = 'liveplaylist/m3u.html'
    model = models.Playlist
    content_type = 'audio/x-mpegurl'

    def get_context_data(self, **kwargs):
        ctx = super(PlayListM3UView, self).get_context_data(**kwargs)
        unwrap = self.request.GET.get('unwrap') == '1'
        ctx.update({
            'unwrap': unwrap
        })
        return ctx