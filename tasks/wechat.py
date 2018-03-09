#!/usr/bin/env python

import sys
from wxpy import *
import asyncio
#import aiohttp


class Task(object):
    name = 'wechat'
    schema_name = 'wechat.org/message'
    schema_version = 'schema-version=1.0.0'
    schema_source_url = 'https://www.wikidata.org/wiki/Q628523'

    schema = {
      'AppInfo': {
          'AppID': {'': [['str'], ['https://www.wikidata.org/wiki/Q50379926']]},
          'Type': {'': [['int'], ['https://www.wikidata.org/wiki/Q16889133']]}},
      'AppMsgType': {'': [['int'], ['https://www.wikidata.org/wiki/Q628523', 'https://www.wikidata.org/wiki/Q16889133']]},
      'Content': {'': [['str'], []]},
      'CreateTime': {'': [['int'], []]},
      'EncryFileName': {'': [['str'], []]},
      'FileName': {'': [['str'], []]},
      'FileSize': {'': [['str'], []]},
      'ForwardFlag': {'': [['int'], []]},
      'FromUserName': {'': [['str'], []]},
      'HasProductId': {'': [['int'], []]},
      'ImgHeight': {'': [['int'], []]},
      'ImgStatus': {'': [['int'], []]},
      'ImgWidth': {'': [['int'], []]},
      'MediaId': {'': [['str'], []]},
      'MsgId': {'': [['str'], []]},
      'MsgType': {'': [['int'], []]},
      'NewMsgId': {'': [['int'], []]},
      'OriContent': {'': [['str'], []]},
      'PlayLength': {'': [['int'], []]},
      'RecommendInfo': {
          'Alias': {'': [['str'], []]},
          'AttrStatus': {'': [['int'], []]},
          'City': {'': [['str'], ['https://www.wikidata.org/wiki/Q515']]},
          'Content': {'': [['str'], []]},
          'NickName': {'': [['str'], []]},
          'OpCode': {'': [['int'], []]},
          'Province': {'': [['str'], []]},
          'QQNum': {'': [['int'], ['https://www.wikidata.org/wiki/Q50379921']]},
          'Scene': {'': [['int'], []]},
          'Sex': {'': [['int'], ['https://www.wikidata.org/wiki/Q290']]},
          'Signature': {'': [['str'], []]},
          'Ticket': {'': [['str'], []]},
          'UserName': {'': [['str'], []]},
          'VerifyFlag': {'': [['int'], []]}
      },
      'Status': {'': [['int'], []]},
      'StatusNotifyCode': {'': [['int'], []]},
      'StatusNotifyUserName': {'': [['str'], []]},
      'SubMsgType': {'': [['int'], []]},
      'Text': {'': [['str'], []]},
      'Ticket': {'': [['str'], []]},
      'ToUserName': {'': [['str'], []]},
      'Type': {'': [['str'], []]},
      'Url': {'': [['str'], []]},
      'VoiceLength': {'': [['int'], []]}
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
