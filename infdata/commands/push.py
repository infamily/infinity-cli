"""The register command."""
import gzip
import os
import json
import pprint
import io

import json_lines

from .base import Base
from infdata.utils import grouper
from infdata.utils import standardize
from infdata.utils import generate_metadata_template

get_id = lambda url: url.rsplit('/', 2)[-2]


class Push(Base):
    """Register a schema, and push data to Infinity server.

    Given:
    >>> pair = ['example.com/posts', 'crawler-1.0.0'],

    Result:
    - From Infinity JSON metadata header, create or update Schema.
    - From Infinity JSON records, create Instances associated.
    """

    def run(self):
        self.load_config()

        user = self.api.users.get()

        datafile = self.options.get('<datafile>')
        self.datapath = os.path.join(os.getcwd(), datafile)
        self.first_character = open(self.datapath).read(1)

        if self.first_character == '[':
            'Assume JSON'
            header = json.load(open(self.datapath))[0:1][0]
        elif self.first_character == '{':
            'Assume JSON lines'
            with open(self.datapath, 'rb') as f:
                for item in json_lines.reader(f):
                    header = item
                    break
        else:
            print('Unknown file type for "{}". Use JSON or JSON lines.'.format(datafile))
            return

        if not header:
            print("Looks like your data is missing metadata. Add metadata.")
            try:
                metadata_prototype = generate_metadata_template(header)
                print('Successfully determined a template metadata for your data.')
                pp = pprint.PrettyPrinter(indent=4)
                print('header = ', end='')
                pp.pprint(metadata_prototype)
                print('Modify and prepend this as JSON header as first record in your dataset.')
                print('Form more info on Infintiy JSON: (https://github.com/infamily/infinity-data).')
                print('Terminating.')
                return
            except Exception as e:
                print('Unable to determine the template for metadata. Check your data.')
                print(e)
                return

        print('IDENTIFYING SCHEMA...')
        try:
            schema_name = header[''][0][0]
            schema_version = header[''][0][1]

            schemas = self.api.schemas.get(name=schema_name, version=schema_version).get('results')

            if not schemas:
                try:
                    schema = self.api.schemas.post({
                        'name': schema_name,
                        'version': schema_version,
                        'specification': [header],
                        'owner': user[0]['url']
                    })
                    print('Created schema ({}): "{}=={}".'.format(schema['url'], schema['name'],
                                                                  schema['version']))

                except Exception as e:
                    print('Failed to create schema: {}=={}'.format(schema_name, schema_version))
                    print(e)
            else:
                schema = schemas[0]
                print('Found schema ({}): "{}=={}".'.format(schema['url'], schema['name'], schema['version']))

                if schema['specification'] != [header]:

                    print('\n--\nCurrent schema specification:', end='\n')
                    pp = pprint.PrettyPrinter(indent=4)
                    pp.pprint(schema['specification'])
                    print('Header schema:', end='\n')
                    pp.pprint(header)
                    print('--\n')

                    overwrite = input('Do you want to overwrite its specification with header? [y/N] ')

                    if overwrite in ['y', 'Y']:
                        schema = self.api.schemas(get_id(schema['url'])).patch({
                            'name': schema_name,
                            'version': schema_version,
                            'specification': [header],
                            'owner': user[0]['url']
                        })
                        print('Schema updated.')

            if 'specification' in schema.keys():

                print('UPLOADING INSTANCES...')

                if self.api.instances.get(schema=schema['url']):
                    proceed = input('Schema already has data instances. Continue adding more instnaces? (may create duplicates) [y/N] ')
                    if proceed in ['y', 'Y']:
                        pass
                    else:
                        print('Operation terminated.')
                        return

                print('Counting records...')
                total_records = sum(1 for _ in self.get_records())
                from progress.bar import Bar
                bar = Bar('Progress', max=total_records, fill='█')
                chunk_size = 1500

                for chunk_records in grouper(self.get_records(), chunk_size):
                    chunk_records = list(filter(None, chunk_records))

                    upload_data = []
                    normalized_records = standardize(schema['specification'], chunk_records)
                    for i, (record, normalized_record) in enumerate(
                            zip(chunk_records, normalized_records)):
                        instance = {
                            'data': record,
                            'info': normalized_record,
                            'schema': schema['url'],
                            'owner': user[0]['url']
                        }
                        upload_data.append(json.dumps(instance))

                    if upload_data:
                        response = self.api.instances_bulk._store["session"].post(
                            url=self.api.instances_bulk.url(),
                            files={
                                'file.jl.gz': io.BytesIO(
                                    gzip.compress('\n'.join(upload_data).encode())
                                )
                            }
                        )
                        response.raise_for_status()
                        bar.next(len(upload_data))

                bar.finish()

        except KeyboardInterrupt:
            raise

        except Exception as e:
            print(repr(e))
            print('''
Please, include schema name and version to the the metadata header. Example:

data = [
{"": [["schema_name", "schema_version"], []], "x": {"": [["float"],["https://www.wikidata.org/wiki/Q208826"]]}},
{"x": 1.5},
{"x": 3.5},
{"x": 4.1}
]''')

        print('Done.')

    def get_records(self):
        if self.first_character == '[':
            'Assume JSON'
            with open(self.datapath) as f:
                jsoniter = iter(json.load(f))
                next(jsoniter)
                for item in jsoniter:
                    yield item
        elif self.first_character == '{':
            'Assume JSON lines'
            with open(self.datapath, 'rb') as f:
                jsoniter = iter(json_lines.reader(f))
                next(jsoniter)
                for item in jsoniter:
                    yield item
        else:
            raise Exception('Unknown file type for "{}". Use JSON or JSON lines.'.format(self.datapath))

