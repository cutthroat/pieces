#!/usr/bin/python3

import sys
import os.path
import re
import datetime
import urllib.request
import mimetypes


CALVIN_URL = r'http://www.gocomics.com/calvinandhobbes/'

IMAGE_REGEX = re.compile(r'(http://cdn.svcs.c2.uclick.com/c2/\w{32})\?width')

DATE_REGEX = re.compile(r'Calvin and Hobbes Comic Strip, (\w+ \d{1,2}, \d{4})')

DATE_FORMAT='%Y-%m-%d'

HEADERS = {
    'User-Agent': r'Mozilla/5.0 (X11; Linux i686; rv:9.0.1) Gecko/20100101 Firefox/9.0.1',
}


# replay log
with open('log', 'r') as LOG:
    LOG_STATE = {}
    for line in LOG:
        text_date, url, ext = line.split()
        LOG_STATE[parse_date(text_date)] = text_date + ext if ext != 'None' else None

# reopen log
LOG = open('log', 'a')


def got_date(date):
    print(date, end=' ')
    sys.stdout.flush()

def got_already():
    print('skip')

def got_no_image(date):
    if date in LOG_STATE and LOG_STATE[date] is not None:
        print(date, None, None, file=LOG)
    print('None')

def got_url():
    print('.', end='')
    sys.stdout.flush()

def got_image(date, url, ext):
    if not ext:
        print(' file exists')
        return
    print(date, url, ext, file=LOG)
    print(' ok')


def parse_date(text, default=None):
    return datetime.datetime.strptime(text, DATE_FORMAT).date() if text is not None else default

def input_interval():
    _, start, end, *_ = sys.argv + [None, None]
    today = date.datetime.today()
    return parse_date(start, today), parse_date(end, today)

def date_range(start, end):
    for i in range(start.toordinal(), end.toordinal() + 1):
        yield datetime.date.fromordinal(i)

def read_url(url):
    request = urllib.request.Request(url=url, headers=HEADERS)
    with urllib.request.urlopen(request) as response:
        return response.read(), response.getheader('Content-Type')

def read_page(date):
    content, _ = read_url(CALVIN_URL+date.strftime('%Y/%m/%d'))
    return content.decode()

def comic_date(page):
    match = DATE_REGEX.search(page)
    return datetime.datetime.strptime(match.group(1), '%B %d, %Y').date() if match else None

def image_url(page):
    match = IMAGE_REGEX.search(page)
    return match.group(1) if match else None

def save_image(url, date):
    content, content_type = read_url(url)
    ext = (['.unknown'] + mimetypes.guess_all_extensions(content_type))[-1]
    fname = date.strftime(DATE_FORMAT) + ext
    if os.path.exists(fname):
        return
    with open(fname, 'wb') as file:
        file.write(content)
    return ext


if __name__ == '__main__':
    start, end = input_interval()
    for date in date_range(start, end):
        got_date(date)
        if date in LOG_STATE and LOG_STATE[date] and os.path.exists(LOG_STATE[date]):
            got_already()
            continue
        page = read_page(date)
        url = image_url(page)
        if url is None or comic_date(page) != date:
            got_no_image(date)
            continue
        got_url()
        ext = save_image(url, date)
        got_image(date, url, ext)


# vim: et sw=4 sts=4
