# -*- coding: utf-8 -*-

import ujson
import requests
import os
import re
from collections import defaultdict
import time


TOKEN = 'keyN5xzdneAOOMW3l'
REPLIES_URL = 'https://api.airtable.com/v0/appQomn5s6YiUzewX/Meduza%20Reply'
HEADERS = {'Authorization': 'Bearer {}'.format(TOKEN)}

i = 1
resp = requests.get(REPLIES_URL, headers=HEADERS, params=dict(view='Grid view'))
resp = resp.json()
for record in resp['records']:
    id = record['id']
    data = {
        'fields': {
            u'Статус': u'Обработано'
        }
    }
    rrr = requests.patch(REPLIES_URL + '/{}'.format(id), headers=HEADERS, json=data)
    # print(record['fields']['E-mail'])
    print(i, rrr.json())
    time.sleep(1)
    if i >= 64:
        break
    i += 1