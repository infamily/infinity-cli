"""The init command."""


import os

from .base import Base


class Init(Base):
    """Initialize local storage folder .inf"""

    def run(self):
        print('Initializing...\n')

        current_directory = os.getcwd()
        final_directory = os.path.join(current_directory, '.inf')

        if not os.path.exists(final_directory):
            os.makedirs(final_directory)

        print('Done.')
