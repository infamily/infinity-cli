"""The switch command."""

import os

from .base import Base
import configparser


class Switch(Base):

    def run(self):

        current_directory = os.getcwd()

        tokens = configparser.ConfigParser()
        tokens.optionxform=str
        tokens.read('.inf/tokens')

        for i, section in enumerate(tokens.sections()):
            print('[{}]: ({}) {}'.format(i, section, tokens[section]['root']))

        config = configparser.ConfigParser()
        config.optionxform=str
        config.read('.inf/config')

        current = config['current']['server']

        CURRENT_ID = tokens.sections().index(current)

        server_id = input("\nEnter server id to use [{}]: ".format(CURRENT_ID)) or CURRENT_ID

        config['current']['server'] = tokens.sections()[int(server_id)]

        with open('.inf/config', 'w') as f:
            config.write(f)
