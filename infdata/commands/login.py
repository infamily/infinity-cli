"""The register command."""

import os

from .base import Base

from urllib.parse import urljoin
import pickle

import slumber
import requests


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

        root = input("Enter server url [http://0.0.0.0:8000]: ") or 'http://0.0.0.0:8000'

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
