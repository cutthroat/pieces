#!/usr/bin/python3

import os.path
import urllib.request

HEADERS = {
    'User-Agent': r'Mozilla/5.0 (X11; Linux i686; rv:9.0.1) Gecko/20100101 Firefox/9.0.1',
}

LOG = open('log', 'r')

def different(fname, url):
    if not os.path.exists(fname):
        return False
    with open(fname, 'rb') as file:
        content = file.read()
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request) as response:
        return content != response.read()

if __name__ == '__main__':
    for line in LOG:
        text_date, url, ext = line.split()
        if ext == 'None':
            continue
        fname = text_date + ext
        if different(fname, url):
            print(fname, '!=', url)
        else:
            print(fname, 'ok')

# vim: et sw=4 sts=4
