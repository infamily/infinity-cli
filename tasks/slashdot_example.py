import xml.etree.ElementTree as ET
import aiohttp


class Task(object):
    name = 'slashdot'
    last_date = None

    def __init__(self, loop):
        self.loop = loop
        self.session = None
        self.seen_item_links = set()
        self.prev_headers = None

    async def update(self):
        headers = {}
        if self.prev_headers and self.prev_headers.get('ETag', None):
            headers = {'If-None-Match': self.prev_headers.get('ETag', None)}

        self.session = self.session or aiohttp.ClientSession()
        r = await self.session.get('http://rss.slashdot.org/Slashdot/slashdotMain', headers=headers)

        if r.status == 304:
            return []

        r.raise_for_status()
        self.prev_headers = r.headers

        content = await r.text()
        root = ET.fromstring(content)
        items = root.findall('.//{http://purl.org/rss/1.0/}item')
        items_list = []
        for item in items:
            title = item.find('{http://purl.org/rss/1.0/}title')
            link = item.find('{http://purl.org/rss/1.0/}link')
            description = item.find('{http://purl.org/rss/1.0/}description')
            date = item.find('{http://purl.org/dc/elements/1.1/}date')

            if link.text in self.seen_item_links:
                continue
            else:
                self.seen_item_links.add(link.text)

            item_dict = {}
            item_dict.update({'title': title.text})
            item_dict.update({'link': link.text})
            item_dict.update({'description': description.text})
            item_dict.update({'date': date.text})

            items_list.append(item_dict)
        return items_list
