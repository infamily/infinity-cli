import time

import aiohttp
import feedparser


class Task(object):
    name = 'futureoflife'
    schema_name = 'futureoflife.org/idea'
    schema_version = 'schema-version=1.0.0'
    schema_source_url = 'https://futureoflife.org/feed/'
    schema = {
        'date': {'': [['str'], []]},
        'description': {'': [['str'], []]},
        'link': {'': [['str'], []]},
        'title': {'': [['str'], []]}
    }

    def __init__(self, loop):
        self.loop = loop
        self.session = None
        self.seen_ids = set()
        self.prev_headers = None

    @property
    def specification(self):
        result = {
            '': [[self.schema_name, self.schema_version], [self.schema_source_url]]
        }
        result.update(self.schema)
        return result

    async def update(self):
        headers = {}
        if self.prev_headers and self.prev_headers.get('ETag', None):
            headers = {'If-None-Match': self.prev_headers.get('ETag', None)}

        self.session = self.session or aiohttp.ClientSession()
        r = await self.session.get(self.schema_source_url, headers=headers)

        if r.status == 304:
            return []

        r.raise_for_status()
        self.prev_headers = r.headers

        content = await r.text()

        d = feedparser.parse(content)
        items_list = []
        for item in d['entries']:

            if item['id'] in self.seen_ids:
                continue
            else:
                self.seen_ids.add(item['id'])

            item_dict = {
                'date': time.strftime('%Y-%m-%dT%H:%M:%SZ', item['published_parsed']),
                'title': item['title'],
                'link': item['link'],
                'description': item['summary_detail']['value'],
            }
            items_list.append(item_dict)

        return items_list