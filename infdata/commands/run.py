import gzip
import json
import io

import asyncio

from .base import Base
from infdata.utils import iter_tasks


class Run(Base):

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
        loop = asyncio.get_event_loop()
        task = None

        for task_class in iter_tasks('tasks'):
            if task_class.name == self.task_name:
                task = task_class(loop)
                break

        if not task:
            print('Can\'t find "%s" task' % self.task_name)
            return

        print('[{task_name}]=>{schema_name}=={schema_version}'.format(
            task_name=self.task_name,
            schema_name=task.schema_name,
            schema_version=task.schema_version
        ))
        self.user = self.api.users.get()[0]
        schemas = self.api.schemas.get(name=task.schema_name, version=task.schema_version).get('results')

        if not schemas:
            try:
                schema = self.api.schemas.post({
                    'name': task.schema_name,
                    'version': task.schema_version,
                    'specification': [task.specification],
                    'owner': self.user['url']
                })
                print('Created schema ({}): "{}=={}".'.format(schema['url'], schema['name'],
                                                              schema['version']))
                schemas = self.api.schemas.get(name=task.schema_name, version=task.schema_version).get('results')
            except Exception as e:
                print('Failed to create schema: {}=={}'.format(task.schema_name, task.schema_version))
                if hasattr(e, 'content'):
                    print(e, e.content)
                else:
                    print(e)
        self.schema = schemas[0]


        @asyncio.coroutine
        def main():
            while True:
                records = yield from task.update()
                if records:
                    self.post_records(records)
                yield from asyncio.sleep(10)

        loop.run_until_complete(main())
        loop.close()

