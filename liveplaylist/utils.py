from collections import OrderedDict
from urlparse import urlsplit, urlunsplit
from django.apps import apps

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

        title_xpaths = scraper.title_xpaths.split(',') if ',' in scraper.title_xpaths else []
        title = u''
        titles_tuple = []
        for title_xpath in title_xpaths:
            titles = subpage_tree.xpath(title_xpath)
            title_str = u' '.join(titles)
            titles_tuple.append(title_str)
            title += title_str

        titles_tuple = tuple(titles_tuple)

        if scraper.filter_title_contains:
            if scraper.filter_title_contains in title:
                found_streams[titles_tuple] = subpage_streams
        else:
            found_streams[titles_tuple] = subpage_streams

    return found_streams


def delete_streams_not_in_scraper(scraper, found_streams):
    found_stream_urls = []
    deleted_livesources = []
    for titles_tuple, streams in found_streams.items():
        for stream in streams:
            found_stream_urls.append(stream)

    found_unique_stream_urls = list(set(found_stream_urls))
    if len(found_stream_urls) != len(found_unique_stream_urls):
        print "hmmm"

    for found_steam_url in found_unique_stream_urls:
        not_found_urls = scraper.livesource_set.exclude(stream_url=found_steam_url)
        for ls in not_found_urls:
            deleted_livesources.append(u'%(ls)s URL=%(url)s' % {'ls': ls.name, 'url': ls.stream_url})
            ls.delete()

    return deleted_livesources


def process_scraper(scraper, livechannel_title_index=None, delete_obsolete_streams=True):
    found_streams = start_scraper(scraper=scraper)
    scraper_results = {
        'created_livechannels': [],
        'created_livesources': [],
        'deleted_livesource': []
    }
    # cleanup
    if delete_obsolete_streams:
        scraper_results['deleted_livesource'] = delete_streams_not_in_scraper(scraper, found_streams)

    # map to LiveSources

    for titles_tuple, streams in found_streams.items():
        for stream in streams:
            existing_same_streams = scraper.livesource_set.filter(stream_url=stream)
            full_title = u' '.join(titles_tuple)
            if livechannel_title_index is not None:
                livechannel_title = titles_tuple[livechannel_title_index]
            else:
                livechannel_title = full_title

            if not existing_same_streams.exists():
                ls, ls_created = scraper.livesource_set.get_or_create(
                    stream_url=stream,
                    defaults={
                        'wrapper': scraper.default_wrapper,
                        'name': full_title,
                    }
                )
                if ls_created:
                    scraper_results['created_livesources'].append(ls)
            else:
                for ls in existing_same_streams:
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



