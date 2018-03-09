#!/usr/bin/env python

import sys
from wxpy import *
import asyncio
#import aiohttp


class Task(object):
    name = 'wechat'
    schema_name = 'wechat.org/message'
    schema_version = 'schema-version=1.0.0'
    schema_source_url = 'https://wechat.org/unknown/'

    schema = {
        'date': {'': [['str'], []]},
        'description': {'': [['str'], []]},
        'link': {'': [['str'], []]},
        'title': {'': [['str'], []]}
    }

    def __init__(self, loop):
        self.bot = Bot(console_qr=True)
        self.loop = loop
        self.friends = self.bot.friends()
        self.groups = self.bot.groups()
        self.groups.extend(self.friends)
        self.seen_item_ids = set()

    @property
    def specification(self):
        result = {
            '': [[self.schema_name, self.schema_version], [self.schema_source_url]]
        }
        result.update(self.schema)
        return result


    async def update(self):
        items_list = []

        for message in self.bot.messages:
            if message.id in self.seen_item_ids:
                continue
            else:
                self.seen_item_ids.add(message.id)
            items_list.append(message.raw)

        return items_list
