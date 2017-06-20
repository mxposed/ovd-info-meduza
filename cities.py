# -*- coding: utf-8 -*-

import ujson
import requests
import os
import re
from collections import defaultdict
import time


with open('token') as f:
    TOKEN = f.read().strip()

CITIES_URL = 'https://api.airtable.com/v0/appQomn5s6YiUzewX/%D0%93%D0%BE%D1%80%D0%BE%D0%B4%D0%B0'
REPLIES_URL = 'https://api.airtable.com/v0/appQomn5s6YiUzewX/Meduza%20Reply'
HEADERS = {'Authorization': 'Bearer {}'.format(TOKEN)}
CASES_RE = re.compile(u'[аиоьеэяюыу]$')
URL_RE = re.compile(u'https?://[^\s]+')

CITIES = {}

def get_all_cities():
    offset = None
    while True:
        params = {'fields[]': u'Город'}
        if offset:
            params['offset'] = offset
        resp = requests.get(CITIES_URL, headers=HEADERS, params=params)
        resp = resp.json()
        for record in resp['records']:
            if u'Город' in record['fields']:
                city = record['fields'][u'Город']
                city = city.lower()
                if CASES_RE.search(city):
                    city = city[:-1]
                CITIES[city] = record['id']
            else:
                print(repr(record))
        if 'offset' in resp:
            offset = resp['offset']
        else:
            break

def parse_response(text):
    name = None
    email = None
    lines = text.split('\n')
    if len(lines) > 1:
        if lines[0].startswith('*name*: '):
            name = lines[0][8:]
        if lines[1].startswith('*email*: '):
            email = lines[1][9:]
    i = text.find('*text*:')
    text = text[i + 7:]
    return dict(
        name=name,
        email=email,
        text=text
    )

def collect_resps(text):
    result = []
    chunks = text.split('---')
    for chunk in chunks:
        chunk = chunk.strip()
        if chunk.startswith('*name*'):
            result.append(parse_response(chunk))
    return result



if os.path.exists('cities'):
    with open('cities') as f:
        CITIES = ujson.loads(f.read())
else:
    get_all_cities()
    with open('cities', 'w') as f:
        f.write(ujson.dumps(CITIES, indent=2))


if os.path.exists('responses.json'):
    with open('responses.json') as f:
        responses = ujson.loads(f.read())
else:
    with open('responses.txt') as f:
        responses = collect_resps(f.read())
        with open('responses.json', 'w') as f2:
            f2.write(ujson.dumps(responses, indent=2))

RESULT = defaultdict(list)
for idx, response in enumerate(responses):
    for city in CITIES.keys():
        txt = response['text'].lower()
        if ' ' + city in txt:
            RESULT[idx].append(city)


def create_record(idx, data):
    record = {
        'fields': {
            'Name': data['name'],
            'E-mail': data['email'],
            'Text': data['text'],
            u'Города': data['cities'],
            u'Ссылки': data['url'],
        }
    }
    resp = requests.post(REPLIES_URL, headers=HEADERS, json=record)
    print(idx)
    print(resp.json())
    time.sleep(0.5)


for idx, response in enumerate(responses):
    record = response
    record['url'] = None
    record['cities'] = []
    for city_id in RESULT[idx]:
        record['cities'].append(CITIES[city_id])
    url_match = URL_RE.search(record['text'])
    if url_match:
        record['url'] = url_match.group(0)
    if idx > 0:
        #print(repr(record))
        create_record(idx, record)
    # if idx >= 0:
        # break




