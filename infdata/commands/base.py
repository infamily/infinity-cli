"""The base command."""
import configparser
import os

import requests
import slumber


class Base(object):
    """A base command."""

    def __init__(self, options, *args, **kwargs):
        self.options = options
        self.args = args
        self.kwargs = kwargs

    def load_config(self):

        current_directory = os.getcwd()
        final_directory = os.path.join(current_directory, '.inf')

        if not os.path.exists(final_directory):
            os.makedirs(final_directory)
            # Create default servers from the settings
        if not os.path.exists(os.path.join(final_directory, 'config')):
            with open(os.path.join(final_directory, 'config'), 'w') as f:
                content = '[servers]\n'+'\n'.join(
                    ['='.join(pair) for pair in settings.INITIAL_SERVERS]
                )
                content += '\n\n[current]\nserver={}'.format(settings.INITIAL_CURRENT)
                f.write(content)

        config_path = os.path.join(os.getcwd(), '.inf/config')

        self.config = configparser.ConfigParser()
        self.config.optionxform = str
        self.config.read(config_path)

        current = self.config['current']['server']

        tokens_path = os.path.join(os.getcwd(), '.inf/tokens')
        tokens = configparser.ConfigParser()
        tokens.optionxform = str
        tokens.read(tokens_path)

        if current in tokens.sections():
            self.api_base_url = tokens[current].get('root')
            self.auth_email = tokens[current].get('email')
            auth_token = tokens[current].get('token')

            if auth_token:
                self.api_session = requests.Session()
                self.api_session.headers.update(
                    {'Authorization': 'Token {}'.format(auth_token)}
                )
            else:
                raise Exception('Error in registration. Use `inf login`')
            self.api = slumber.API(self.api_base_url, session=self.api_session)

    def run(self):
        raise NotImplementedError('You must implement the run() method yourself!')
