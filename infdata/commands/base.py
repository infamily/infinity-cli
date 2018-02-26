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
