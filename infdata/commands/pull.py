"""The pull command."""

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


class Pull(Base):
    """.

    Given:
    >>> string = 'example.com/posts==crawler-1.0.0'

    Result:
    - The string is split into schema_name, schema_version.
    - The version is looked up, and the records
      are downloadeded and saved to the .inf/data/ as json lines
      named as
    - If there are new records, they are appended to the bottom
      of the file.

    """

    def run(self):
        self.load_config()

        user = self.api.users.get()

        page_size = self.options.get('<page_size>') or 3000
        schema_name_version = self.options.get('<name==version>')
        #schema_name_version = 'example.com/person==v1'

        if not '==' in schema_name_version:
            print('Please, use: inf pull name==version.')
            return

        name, version = schema_name_version.rsplit('==', 1)

        # Lookup if the schema exists
        schemas = self.api.schemas.get(name=name, version=version).get('results')

        if not schemas:
            print('Schema ({}=={}) not found.'.format(name,version))
            return

        schema = schemas[0]

        # Creating a file to store data
        version = '{}=={}'.format(schema['name'], schema['version'])
        filename = quote_plus(version)

        # Todo: add to settings
        DATA_DIRECTORY = os.path.join(os.getcwd(), '.inf/data/')
        if not os.path.exists(DATA_DIRECTORY):
            os.makedirs(DATA_DIRECTORY)

        target_path = os.path.join(os.getcwd(), '.inf/data/{}'.format(filename))

        response = self.api.instances_bulk.get(schema=get_id(schema['url']))
        count = response.get('count')
        limit = int(input('There are totally {} instances. Enter the number to download [all]: '.format(count)) or count)

        if os.path.exists(target_path):
            proceed = input('The data of this schema already present. Are you sure you want to recreate it? [y/N] ')
            if proceed not in ['y', 'Y']:
                print('Stopped.')
                return
            else:
                os.remove(target_path)


        with open(target_path, 'a') as f:
            f.write(json.dumps(schema['specification'][0])+'\n')

        def write(results):
            for result in results:
                if result.get('data'):

                    with open(target_path, 'a') as f:
                        f.write(json.dumps(result.get('data'))+'\n')
            return len(results)

        from progress.bar import Bar
        bar = Bar('Progress', max=limit, fill='█')
        written = 0
        if response.get('next'):
            increment = write(response.get('results'))
            bar.next(increment)
            written += increment
            if written >= limit:
                print('Done.')
                return

            while response.get('next'):
                next_page_id = dict(parse_qsl(urlparse(response.get('next')).query)).get('page')
                headers = {'Accept-Encoding': 'gzip'}
                r = self.api.instances_bulk._store["session"].get(
                    url=self.api.instances_bulk.url(),
                    params=dict(
                        schema=get_id(schema['url']), page=next_page_id, page_size=page_size
                    ),
                    headers=headers
                )
                r.raise_for_status()
                response = r.json()
                increment = write(response.get('results'))
                bar.next(increment)
                written += increment
                if written >= limit:
                    print('Done.')
                    return
        bar.finish()

        print('Done.')
