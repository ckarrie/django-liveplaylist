from collections import OrderedDict
from django.utils import six, timezone
from urlparse import urlsplit, urlunsplit
import datetime
import re


def get_m3u(playlist):
    m3u_lines = [u'#EXTM3U']
    for plc in playlist.playlistchannel_set.order_by('position'):
        entry_name = u'#EXTINF:-1,' + plc.get_entry_name()
        m3u_lines.append(entry_name)
        m3u_lines.append(plc.get_wrapped_stream_url())

    return u''.join(m3u_lines)


def make_absolute(base_url, path):
    if path.startswith('/') or path.startswith('.'):
        scheme, netloc, base_path, query, fragment = urlsplit(base_url)
        url = urlunsplit((scheme, netloc, path, query, fragment,))
    else:
        url = path
    return url


class ScraperPage(object):
    titles = []
    epg_text = []
    start_time = None
    end_time = None
    icon = ''

    def get_icon_from_subpage(self, pagetree):
        raise NotImplementedError()


def start_scraper(scraper):
    import requests
    from lxml import html

    htmlpage = requests.get(scraper.main_page_url)

    base_url = scraper.main_page_url
    tree = html.fromstring(htmlpage.content)
    subpage_hrefs = list(set(tree.xpath(scraper.main_page_find_subpages_xpath)))

    found_streams = OrderedDict()

    for subpage_href in subpage_hrefs:
        subpage_url = make_absolute(
            base_url=base_url,
            path=subpage_href
        )

        subpage_htmlpage = requests.get(subpage_url)
        subpage_tree = html.fromstring(subpage_htmlpage.content)
        subpage_streams = subpage_tree.xpath(scraper.subpage_find_stream_xpath)
        title_xpaths = scraper.title_xpaths.split(',') if ',' in scraper.title_xpaths else [scraper.title_xpaths]
        title = u''
        titles_tuple = []
        for title_xpath in title_xpaths:
            titles = subpage_tree.xpath(title_xpath)
            title_str = u' '.join(titles)
            titles_tuple.append(title_str)
            title += title_str

        titles_tuple = tuple(titles_tuple)

        if scraper.filter_title_contains and len(scraper.filter_title_contains) > 1 and scraper.filter_title_contains not in title:
            print "--- skipping title ---", title, titles_tuple
            continue

        for sub_stream in subpage_streams:
            if 'zdf.de' in scraper.main_page_url:
                stream_icon = subpage_href.getparent().getparent().getparent().getparent().xpath('div[@class="image"]/a/img/@src')[0]
                stream_icon = stream_icon.replace('timg94x65blob', 'timg485x273blob')
                stream_icon_url = make_absolute(
                    base_url=base_url,
                    path=stream_icon
                )
                titles_tuple += (stream_icon_url, )

            if sub_stream in found_streams:
                found_streams[sub_stream].append(titles_tuple)
            else:
                found_streams[sub_stream] = [titles_tuple, ]

    return found_streams


def delete_streams_not_in_scraper(scraper, found_streams):
    found_stream_urls = found_streams.keys()
    deleted_livesources = []

    for found_steam_url in found_stream_urls:
        not_found_urls = scraper.livesource_set.exclude(stream_url=found_steam_url)
        for ls in not_found_urls:
            deleted_livesources.append(u'%(ls)s URL=%(url)s' % {'ls': ls.name, 'url': ls.stream_url})
            #ls.delete()

    return deleted_livesources


def process_scraper(scraper, livechannel_title_index=None, delete_obsolete_streams=True):
    found_streams = start_scraper(scraper=scraper)
    for streams, titles_tuple in found_streams.items():
        print streams
        for title in titles_tuple:
            print "- ", title

    scraper_results = {
        'created_livechannels': [],
        'created_livesources': [],
        'deleted_livesource': []
    }
    # cleanup
    if delete_obsolete_streams:
        scraper_results['deleted_livesource'] = delete_streams_not_in_scraper(scraper, found_streams)
        #for dlc in scraper_results['deleted_livesource']:
        #    print dlc

    # map to LiveSources

    for stream_url, titles_tuples in found_streams.items():
        for titles_tuple in titles_tuples:
            titles_tuple = list(titles_tuple)
            stream_logo_url = ''
            if scraper.scraper_type == u'ZDFScraperPage':
                start_end_text = titles_tuple[0].replace("Olympia 2016, ", "").split(" - ")
                if titles_tuple[-1].startswith('http'):
                    stream_logo_url = titles_tuple[-1]
                    titles_tuple = titles_tuple[0:-1]

                stream_start_dt = None
                stream_end_time = None
                stream_end_dt = None
                zdf_start_regex = re.compile(r'(?P<day>\d{1,2}).(?P<month>\d{1,2}).(?P<year>\d{4}) '
                                             r'(?P<hour>\d{1,2}):(?P<minute>\d{1,2})')
                zdf_end_regex = re.compile(r'(?P<hour>\d{1,2}):(?P<minute>\d{1,2})')
                zdf_start_regex_match = zdf_start_regex.match(start_end_text[0])
                zdf_end_regex_match = zdf_end_regex.match(start_end_text[1])
                if zdf_start_regex_match:
                    kw = {k: int(v) for k, v in six.iteritems(zdf_start_regex_match.groupdict())}
                    stream_start_dt = datetime.datetime(**kw)

                if zdf_end_regex_match:
                    kw = {k: int(v) for k, v in six.iteritems(zdf_end_regex_match.groupdict())}
                    stream_end_time = datetime.time(**kw)

                if stream_start_dt is not None and stream_end_time is not None:
                    stream_end_dt = datetime.datetime(year=stream_start_dt.year, month=stream_start_dt.month,
                                                      day=stream_start_dt.day,
                                                      hour=stream_end_time.hour, minute=stream_end_time.minute)

                    if stream_start_dt is not None and stream_end_time < stream_start_dt.time():
                        stream_end_dt = stream_end_dt + datetime.timedelta(days=+1)

            else:
                stream_start_dt = timezone.now()
                stream_end_dt = stream_start_dt + datetime.timedelta(days=365 * 2)

            full_title = u' '.join(titles_tuple)
            if livechannel_title_index is not None:
                livechannel_title = titles_tuple[livechannel_title_index]
            else:
                livechannel_title = full_title

            ls, ls_created = scraper.livesource_set.get_or_create(
                stream_url=stream_url,
                start_dt=stream_start_dt,
                end_dt=stream_end_dt,
                stream_logo_url=stream_logo_url,
                defaults={
                    'wrapper': scraper.default_wrapper,
                    'name': full_title,
                }
            )
            if ls_created:
                scraper_results['created_livesources'].append(ls)
            else:
                ls.name = full_title
                ls.save()

            lc, lc_created = ls.livechannel_set.get_or_create(
                source=ls,
                defaults={
                    'name': livechannel_title
                }
            )

            if not lc_created:
                lc.name = livechannel_title
                lc.save()

            else:
                scraper_results['created_livechannels'].append(lc)

    return scraper_results



