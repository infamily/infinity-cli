import gzip
import json
import os
import io

import asyncio
import json_lines

from .base import Base
from infdata.utils import iter_tasks


class Bind(Base):

    def post_records(self, records):
        lines_data = []
        for record in records:
            instance = {
                'data': record,
                'schema': self.schema['url'],
                'owner': self.user['url']
            }
            lines_data.append(json.dumps(instance))

        if lines_data:
            # check exists?
            response = self.api.instances_bulk._store["session"].post(
                url=self.api.instances_bulk.url(),
                files={
                    'file.jl.gz': io.BytesIO(
                        gzip.compress('\n'.join(lines_data).encode())
                    )
                }
            )
            response.raise_for_status()
            print('Added %s instances' % len(lines_data))

    def run(self):
        self.load_config()
        self.task_name = self.options.get('<task_name>')
        TaskClass = None

        for task in iter_tasks('tasks'):
            if task.name == self.task_name:
                TaskClass = task
                break

        if not TaskClass:
            print('Can\'t find "%s" task' % self.task_name)
            return

        self.datapath = os.path.join(os.getcwd(), self.options.get('<datafile>'))

        self.specification = self.read_header()
        schema_name, schema_version = self.specification[''][0]

        print('[{task_name}]=>{schema_name}=={schema_version}'.format(
            task_name=self.task_name,
            schema_name=schema_name,
            schema_version=schema_version
        ))
        self.user = self.api.users.get()[0]
        schemas = self.api.schemas.get(name=schema_name, version=schema_version).get('results')

        if not schemas:
            try:
                schema = self.api.schemas.post({
                    'name': schema_name,
                    'version': schema_version,
                    'specification': [self.specification],
                    'owner': self.user['url']
                })
                print('Created schema ({}): "{}=={}".'.format(schema['url'], schema['name'],
                                                              schema['version']))
                schemas = self.api.schemas.get(name=schema_name, version=schema_version).get('results')
            except Exception as e:
                print('Failed to create schema: {}=={}'.format(schema_name, schema_version))
                print(e)
        self.schema = schemas[0]

        loop = asyncio.get_event_loop()

        task = TaskClass(loop)

        @asyncio.coroutine
        def main():
            while True:
                records = yield from task.update()
                if records:
                    self.post_records(records)
                yield from asyncio.sleep(10)

        loop.run_until_complete(main())
        loop.close()

    def read_header(self):
        with open(self.datapath) as fp:
            for line in json_lines.reader(fp):
                return line
