"""The switch command."""

import os

from .base import Base
import configparser


class Which(Base):

    def run(self):

        current_directory = os.getcwd()

        tokens = configparser.ConfigParser()
        tokens.optionxform=str
        tokens.read('.inf/tokens')

        config = configparser.ConfigParser()
        config.optionxform=str
        config.read('.inf/config')

        current = config['current']['server']

        if current not in tokens.sections():
            print("Have no token of server [{}]. Login first.".format(current))
            return

        for i, section in enumerate(tokens.sections()):
            if current == section:
                print('*', end='')
            else:
                print(' ', end='')

            print('[{}]: ({}) {}'.format(i, section, tokens[section]['root']))

        CURRENT_ID = tokens.sections().index(current)

        server_id = input("\nEnter server id to use [{}]: ".format(CURRENT_ID)) or CURRENT_ID

        config['current']['server'] = tokens.sections()[int(server_id)]

        with open('.inf/config', 'w') as f:
            config.write(f)

        print('Switched to [{}] server.'.format(config['current']['server']))
