from .base import Base
from infdata.utils import iter_tasks


class Tasks(Base):

    def run(self):
        for Task in iter_tasks('tasks'):
            print('Task "%s"' % Task.name)
