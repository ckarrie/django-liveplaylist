from liveplaylist.utils import ScraperPage
from lxml import html
from scrapy.contrib.loader import XPathItemLoader


class ZDFScraperPage(ScraperPage):
    def get_icon_from_subpage(self, pagetree):
        xl = XPathItemLoader(response=pagetree.tostring(), item={'image': ''})
        t1 = pagetree.xpath(
            "//style[re:test(local-name(), 'background-image.*/([^/]+)')",
            namespaces={"re": "http://exslt.org/regular-expressions"}
        )

        t2 = xl.get_xpath('//style', re=r"background-image.*/([^/]+)'")
        print "t1", t1
        print "t2", t2

        return t2