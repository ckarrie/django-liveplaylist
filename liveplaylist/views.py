import models
from django.apps import apps
from django.views import generic
from django.db.models import Q
from django.utils import timezone


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
            'livechannels': apps.get_model('liveplaylist.LiveChannel').objects.filter(
                Q(source__end_dt__isnull=True) | Q(source__end_dt__gte=timezone.now())
            ).order_by('name', 'source__start_dt', 'source__last_updated'),
            'wrappers': apps.get_model('liveplaylist.SourceWrapper').objects.all()
        })
        return ctx


class PlayListM3UView(generic.DetailView):
    template_name = 'liveplaylist/m3u.html'
    model = models.Playlist
    content_type = 'audio/x-mpegurl'

    def get_context_data(self, **kwargs):
        ctx = super(PlayListM3UView, self).get_context_data(**kwargs)
        unwrap = self.request.GET.get('unwrap') == '1'
        wrapper_id = self.request.GET.get('wrapper')
        if wrapper_id:
            wrapper = models.SourceWrapper.objects.get(id=wrapper_id)
            current_playlistchannels = self.object.get_current_playlistchannels(wrapper=wrapper)
        else:
            current_playlistchannels = self.object.get_current_playlistchannels()

        ctx.update({
            'unwrap': unwrap,
            'current_playlistchannels': current_playlistchannels
        })
        return ctx

    def render_to_response(self, context, **response_kwargs):
        as_text = self.request.GET.get('as_text') == '1'
        if as_text:
            self.content_type = 'text/plain'
        return super(PlayListM3UView, self).render_to_response(context, **response_kwargs)
