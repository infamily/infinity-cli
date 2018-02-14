import asyncio
import logging
import requests
import xml.etree.ElementTree as ET


class Task(object):
    name = 'slashdot'
    last_date = None

    def __init__(self, loop, log=None):
        self.loop = loop
        self.log = log or logging.getLogger('tasks.%s' % self.name)

    async def update(self):
        headers = {}
        if self.last_date:
            headers = {
                'If-Modified-Since': self.last_date
            }

        # use aiohttp ?
        r = requests.get('http://rss.slashdot.org/Slashdot/slashdotMain', headers=headers)
        if r.status_code == 304:
            self.log.info('No new data')
            return []
        r.raise_for_status()
        self.last_date = r.headers['Last-Modified']

        root = ET.fromstring(r.content)
        items = root.findall('.//{http://purl.org/rss/1.0/}item')
        items_list = []
        for item in items:
            title = item.find('{http://purl.org/rss/1.0/}title')
            link = item.find('{http://purl.org/rss/1.0/}link')
            description = item.find('{http://purl.org/rss/1.0/}description')
            date = item.find('{http://purl.org/dc/elements/1.1/}date')

            item_dict = {}
            item_dict.update({'title': title.text})
            item_dict.update({'link': link.text})
            item_dict.update({'description': description.text})
            item_dict.update({'date': date.text})

            items_list.append(item_dict)
        return items_list
