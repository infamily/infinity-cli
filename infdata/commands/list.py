"""The list command."""

import os
import json
import json_lines
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
        self.load_config()

        schema_name = self.options.get('<name>')

        if not hasattr(self, 'api'):
            print('No api configuration. Try logging in by `inf login`')
            return

        for schema in self.api.schemas.get()['results']:
            print('{}=={}'.format(schema['name'], schema['version']))
            #name__startswith=schema_name))

