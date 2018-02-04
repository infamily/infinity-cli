"""The install command."""

import os
import json
import slumber
import requests
import json_lines
import configparser
from urllib.parse import (
    urlparse,
    parse_qsl,
    quote_plus,
    unquote_plus
)

from .base import Base

get_id = lambda url: url.rsplit('/', 2)[-2]


class List(Base):

    def run(self):

        #todo: refactor repeating block
        config_path = os.path.join(os.getcwd(), '.inf/config')
        config = configparser.ConfigParser()
        config.optionxform=str
        config.read(config_path)

        if 'server' in config.sections():
            root = config['server'].get('root')
            email = config['server'].get('email')
            token = config['server'].get('token')

            session = requests.Session()
            header = {
                'Authorization': 'Token {}'.format(token)}
            session.headers.update(header)
        else:
            print('Error in registration. Use `inf login`')
            return
        #/todo: refactor repeating block

        schema_name = self.options.get('<name>')

        api = slumber.API(root, session=session)

        for schema in api.schemas.get()['results']:
            print('{}=={}'.format(schema['name'], schema['version']))
            #name__startswith=schema_name))

