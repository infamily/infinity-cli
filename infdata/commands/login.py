"""The register command."""

import os

from .base import Base

import slumber

from urllib.parse import urljoin, urlparse
from infdata.ping import ping


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

        #todo: add to settings
        print('Searching servers.', end='')
        KNOWN_SERVERS = {}
        for name, url in [
                ('LOCALHOST', 'http://0.0.0.0:8000'),
                ('Shanghai', 'https://test.wefindx.io'),
                ('Vilnius', 'https://lt.wfx.io'),
                ('Frankfurt', 'https://test.wefindx.io'),
                ('DEVELOPMENT', 'https://dev.wfx.io')
            ]:
            KNOWN_SERVERS.update({url: ping(urlparse(url).netloc)})
            print('.', end='')
        print('\n')


        min_ping = min(KNOWN_SERVERS.values())
        DEFAULT_SERVER = [server for server in KNOWN_SERVERS
                          if KNOWN_SERVERS[server] == min_ping][0]

        root = input("Enter server url or [?] to choose [{}]: ".format(DEFAULT_SERVER)) or DEFAULT_SERVER

        if root == '?':
            choices = {i: server for i, server in enumerate(KNOWN_SERVERS)}
            for i in choices:
                print('[{}]'.format(i), choices[i])
            i = input('Enter server number: ')
            root = choices[int(i)]
            print('Using [{}].'.format(root))

        config_path = os.path.join(os.getcwd(), '.inf/config')

        if os.path.exists(config_path):

            proceed = input('You are already seem to have signed in with token .inf/token, are you really want to regenerate the token? [y/N] ')

            if proceed in ['y', 'Y']:
                pass
            else:
                return

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

            with open(config_path, 'w') as f:

                auth = '[server]\nroot={}\nemail={}\ntoken={}'.format(
                    root, email, token
                )

                f.write(auth)

        except:
            print('Error. Check if your input.')

        print('Done.')
