from datetime import datetime
import sys
import os
import re
import feedparser
from core.models import Pasty

if sys.version_info[0] > 2:
    from urllib.request import Request, urlopen
    from urllib.parse import quote_plus, urlparse, parse_qs
else:
    from urllib2 import Request, urlopen
    from urlparse import urlparse, parse_qs

try:
    from bs4 import BeautifulSoup
except ImportError:
    from BeautifulSoup import BeautifulSoup


def sync_rss_source(source):

    entries = []

    if source.parser() in globals():
        entries = globals()[source.parser()](source)
    else:
        entries = default_parser(source)

    for entry in entries:
        if not Pasty.objects.filter(unique_key=entry.get('id')):
            print(entry.get('id'))
            p = Pasty(text=entry.get('text'), date=entry.get('date'), source=entry.get('source'), unique_key=entry.get('id'))
            p.save()


def replace_br_to_newline(text):
    # strip_pattern = re.compile('</?p>|</?div>|</?a>|</?span>')
    br_pattern = re.compile('<br ?/?>')
    space_pattern = re.compile('\s\s+')
    # text = strip_pattern.sub('', text)
    text = space_pattern.sub(' ', text)
    text = br_pattern.sub(os.linesep, text)
    return text


def get_page(url):
    """
    Request the given URL and return the response page, using the cookie jar.

    @type  url: str
    @param url: URL to retrieve.

    @rtype:  str
    @return: Web page retrieved for the given URL.
    """
    request = Request(url)
    request.add_header('User-Agent',
                       'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0)')
    response = urlopen(request)
    http_message = response.info()
    full = http_message.type  # 'text/plain'

    ret = response.read()

    response.close()

    return ret

def perashki_ru(source):
    ret = []

    row = get_page(source.sync_url)

    soup = BeautifulSoup(row)

    for entry in soup.findAll('div', {"class": "PiroEntry"}):
        e = {}

        e['id'] = entry['id']

        entry_text = entry.find('div', {"class": "Text"})
        e['text'] = entry_text.text

        entry_date = entry.find('span', {"class": "date"})
        e['date'] = datetime.strptime(entry_date.text, '%d.%m.%Y')

        e['source'] = source.url

        if len(e.get('text', '')) > 0:
            ret.append(e)

    return ret


def default_parser(source):

    ret = []

    if source.sync_url:
        data = feedparser.parse(source.sync_url)
        if data.feed.get('title', False):
            for entry in data.entries:
                e = {}
                if entry.get('id', False):
                    e['id'] = entry.get('id')

                if entry.get('summary', False):
                    soup = BeautifulSoup(replace_br_to_newline(entry.get('summary')))
                    e['text'] = soup.text.strip()

                if entry.get('published_parsed', False):
                    e['date'] = datetime(entry.published_parsed[0], entry.published_parsed[1],
                                         entry.published_parsed[2], entry.published_parsed[3],
                                         entry.published_parsed[4], entry.published_parsed[5])

                e['source'] = source.url

                if len(e.get('text', '')) > 0:
                    ret.append(e)

    return ret
