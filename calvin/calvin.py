#!/usr/bin/python3

import sys
import os.path
import re
import datetime
import urllib.request
import mimetypes


CALVIN = {
    'url': r'http://www.gocomics.com/calvinandhobbes/',
    'image': re.compile(r'(http://cdn.svcs.c2.uclick.com/c2/\w{32})\?width'),
    'date': re.compile(r'Calvin and Hobbes Comic Strip, (\w+ \d{1,2}, \d{4})'),
}

REQUEST_HEADRES = {
    'User-Agent': r'Mozilla/5.0 (X11; Linux i686; rv:9.0.1) Gecko/20100101 Firefox/9.0.1',
}


class CalvinError(Exception):
    pass

class SaveError(Exception):
    pass

class NotAvailable(Exception):
    pass

class Skip(Exception):
    pass


def date(text):
    return datetime.datetime.strptime(text, '%Y-%m-%d')

def replay():
    log_state = {}
    with open('log', 'r') as log:
        for line in log:
            date_text, url, ext = line.split()
            log_state[date(date_text)] = date_text + ext if ext != 'None' else None
    return open('log', 'a'), log_state

def read(url):
    request = urllib.request.Request(url=url, headers=REQUEST_HEADRES)
    with urllib.request.urlopen(request) as response:
        content_type = response.getheader('Content-Type')
        ext = ([None] + mimetypes.guess_all_extensions(content_type))[-1]
        return response.read(), content_type, ext

def find(date):
    page = read(CALVIN['url'] + date.strftime('%Y/%m/%d'))[0].decode()
    date_match = CALVIN['date'].search(page)
    if not date_match:
        raise CalvinError('No date')
    page_date = datetime.datetime.strptime(date_match.group(1), '%B %d, %Y').date()
    if page_date != date:
        raise NotAvailable
    image_match = CALVIN['image'].search(page)
    if not image_match:
        raise CalvinError('No image')
    image_url = image_match.group(1)
    return image_url

def save(image_url, date):
    (content, content_type, ext) = read(image_url)
    path = date.strftime('%Y-%m-%d') + (ext or '')
    if os.path.exists(path):
        raise SaveError('File exists')
    with open(path, 'wb') as file:
        file.write(content)
    return ext

def proceed(date, log_state):
    if date not in log_state:
        return
    if not log_state[date]:
        raise NotAvailable
    if log_state[date] and os.path.exists(log_state[date]):
            raise Skip

def download(last, end, log):
    log_file, log_state = log
    for ord in range(last.toordinal() + 1, end.toordinal() + 1):
        date = datetime.date.fromordinal(ord)
        date_text = date.strftime('%Y-%m-%d')
        print(date_text, end=' ')
        sys.stdout.flush() # it'd be nice if the reporter was contextmanager
        try:
            proceed(date, log_state)
            image_url = find(date)
            ext = save(image_url, date)
            print(date_text, image_url, ext, file=log_file)
            print('ok')
        except CalvinError as e:
            print(e)
        except SaveError as e:
            print(e)
        except NotAvailable:
            print(date_text, None, None, file=log_file)
            print('na')
        except Skip:
            print('--')


def main():
    log = replay()
    today = datetime.date.today()
    last_entry = max(log[1].keys()) if log[1] else today
    download(last_entry, today, log)


if __name__ == '__main__':
    main()

# vim: et sw=4 sts=4
