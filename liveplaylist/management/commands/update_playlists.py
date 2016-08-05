from django.apps import apps
from django.core.management.base import BaseCommand

__author__ = 'ckw'


class Command(BaseCommand):
    """
    usage:
    #/home/ckw/workspace/venvs/lp
    python dpl/manage.py update_playlists

    in cron:
    (sinnvollerweise Nachts um 6:00 Uhr
    0 6 * * * /home/ckw/workspace/venvs/lp/bin/python /home/ckw/workspace/venvs/lp/dpl/manage.py update_playlists
    """

    help = 'Update Playlists'

    def handle(self, *args, **options):
        pu_mdl = apps.get_model('liveplaylist', 'PlaylistUpdate')
        for pu in pu_mdl.objects.all():
            created_livechannels = pu.update_playlist()
            self.stdout.write(self.style.SUCCESS('Updated Playlist %(pl)s, created new %(lcs)d' % {
                'pl': pu.playlist,
                'lcs': len(created_livechannels)
            }))

