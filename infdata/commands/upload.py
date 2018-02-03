"""The register command."""

import os
import json
import pprint
import slumber
import requests
import json_lines
import configparser

from .base import Base
from infdata.utils import take
from infdata.utils import standardize

get_id = lambda url: url.rsplit('/', 2)[-2]


class Upload(Base):
    """Register a schema, and upload data to Infinity server.

    Given:
    >>> pair = ['example.com/posts', 'crawler-1.0.0'],

    Result:
    - From Infinity JSON metadata header, create or update Schema.
    - From Infinity JSON records, create Instances associated.
    """

    def run(self):

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

        api = slumber.API(root, session=session)
        user = api.users.get()

        datafile = self.options.get('<datafile>')
        datafile = 'data.jl'

        if datafile:
            datapath = os.path.join(os.getcwd(), datafile)

            first_character = open(datapath).read(1)

            if first_character == '[':
                'Assume JSON'
                data = json.load(open(datapath))
            elif first_character == '{':
                'Assume JSON lines'
                data = []
                with open(datapath, 'rb') as f:
                    for item in json_lines.reader(f):
                        data.append(item)
            else:
                print('Unknown file type for "{}". Use JSON or JSON lines.'.format(datafile))
                return

        header, records = take(data)

        print('IDENTIFYING SCHEMA...')
        try:
            schema_name = header[0][''][0][0]
            schema_version = header[0][''][0][1]

            schemas = api.schemas.get(name=schema_name, version=schema_version).get('results')

            if not schemas:
                try:
                    schema = api.schemas.post({
                        'name': schema_name,
                        'version': schema_version,
                        'specification': header,
                        'owner': user[0]['url']
                    })
                    print('Created schema ({}): "{}=={}".'.format(schema['url'], schema['name'], schema['version']))

                except Exception as e:
                    print('Failed to create schema: {}'.format(meta))
                    print(e)
            else:
                schema = schemas[0]
                print('Found schema ({}): "{}=={}".'.format(schema['url'], schema['name'], schema['version']))

                if schema['specification'] != header:

                    print('\n--\nCurrent schema specification:', end='\n')
                    pp = pprint.PrettyPrinter(indent=4)
                    pp.pprint(schema['specification'])
                    print('Header schema:', end='\n')
                    pp.pprint(header)
                    print('--\n')

                    overwrite = input('Do you want to overwrite its specification with header? [y/N] ')

                    if overwrite in ['y', 'Y']:
                        schema = api.schemas(get_id(schema['url'])).patch({
                            'name': schema_name,
                            'version': schema_version,
                            'specification': header,
                            'owner': user[0]['url']
                        })


            if 'specification' in schema.keys():

                print('UPLOADING INSTANCES...')

                if api.instances.get(schema=schema['url']):
                    proceed = input('Schema already has data instances. Continue adding more instnaces? (may create duplicates) [y/N] ')
                    if proceed in ['y', 'Y']:
                        pass
                    else:
                        print('Operation terminated.')
                        return

                normalized_records = standardize(schema['specification'], records)

                from progress.bar import Bar
                bar = Bar('Progress', max=len(records), fill='█')
                for i, (record, normalized_record) in enumerate(
                        zip(records, normalized_records)):

                    instance = {
                        'data': record,
                        'info': normalized_record,
                        'schema': schema['url'],
                        'owner': user[0]['url']
                    }

                    api.instances.post(instance)

                    bar.next()

                bar.finish()


        except KeyboardInterrupt:
            raise

        except:

            print('''
Please, include schema name and version to the the metadata header. Example:

data = [
{"": [["schema_name", "schema_version"], []], "x": {"": [["float"],["https://www.wikidata.org/wiki/Q208826"]]}},
{"x": 1.5},
{"x": 3.5},
{"x": 4.1}
]''')

        print('Done.')
