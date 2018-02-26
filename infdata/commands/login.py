"""The register command."""

import os

from .base import Base

import slumber, configparser

from urllib.parse import urljoin, urlparse
from infdata.ping import ping
from infdata import settings


class Login(Base):
    """Singin to an Infinity server.

    Given:
    >>> email = 'some@email.com'

    Result:

    - Return a link to the captcha, and ask to enter captcha.
    - Given captcha is entered, tell to open e-mail, and enter OTP.
    - Save the token to user's configuration file.
    (~/.inf/config)
    """

    def run(self):

        # Create folder .inf, if doesn't exist
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

        if not self.options.get('<server>'):

            config = configparser.ConfigParser()
            config.optionxform=str
            config.read('.inf/config')

            CONFIG_SERVERS = [
                (value, config['servers'][value])
                for value in config['servers']
            ]

            print('Checking public servers:')
            KNOWN_SERVERS = {}
            for i, (name, url) in enumerate(CONFIG_SERVERS):
                result = {url: ping(urlparse(url).netloc)}
                KNOWN_SERVERS.update(result)
                ms = round(list(result.values())[0], 3) * 1000
                if ms not in [float('Inf')]:
                    ms = int(ms)
                else:
                    ms = '-- '
                print("[{}] ({}) {}: [{}ms]".format(i, name, url, ms))

            min_ping = min(KNOWN_SERVERS.values())

            DEFAULT_SERVER = [server for server in KNOWN_SERVERS
                if KNOWN_SERVERS[server] == min_ping][0]

            DEFAULT_SERVER_ID = [i for i, server in enumerate(CONFIG_SERVERS)
                if server[1] == DEFAULT_SERVER][0]

            server_id = input("\nEnter server id to use [{}]: ".format(DEFAULT_SERVER_ID)) or DEFAULT_SERVER_ID

            if server_id == '?':
                i = input('Enter server number: ')

            pair = CONFIG_SERVERS[int(server_id)]
            name = pair[0]
            root = pair[1]

        else:
            name = self.options.get('<server>')
            root = 'https://' + name


        print('Connecting to {}.'.format(root))
        config_path = os.path.join(os.getcwd(), '.inf/tokens')

        proceed = input('Generate token for server [{}]? [y/N] '.format(root))
        if proceed in ['y', 'Y']:
            pass
        else:
            return

        # Read whole config from .inf/tokens
        if not os.path.exists(config_path):
            open(config_path, 'a').close()

        tokens = configparser.ConfigParser()
        tokens.optionxform=str
        tokens.read(config_path)

        api = slumber.API(root)
        email = input('Please, enter the e-mail: ')
        captcha = api.captcha.get()
        captcha_response = input(
            '{}\nCaptcha response: '.format(
                'Visit {}'.format(
                    urljoin(root, captcha['image_url']))))

        try:
            response = api.signup.post(data={
                'email': email,
                "captcha": {
                    "hashkey": captcha['key'],
                    "response": captcha_response,
                }
            })

            password = input(
                'Check ({}) for one-time password.\nPassword: '.format(email))

            auth_data = api.signin.post(data={
                'email': email,
                'one_time_password': password
            })

            token = auth_data['auth_token'].rsplit('/', 2)[1]


            if not tokens.has_section(name):
                tokens.add_section(name)

            tokens[name]['root'] = root
            tokens[name]['email'] = email
            tokens[name]['token'] = token

            with open(config_path, 'w') as f:
                tokens.write(f)

            config = configparser.ConfigParser()
            config.optionxform=str
            config.read('.inf/config')

            config['current']['server'] = name

            with open('.inf/config', 'w') as f:
                config.write(f)


        except Exception as e:
            print(e)
            print('Error. Check if your input.')

        print('Done.')
