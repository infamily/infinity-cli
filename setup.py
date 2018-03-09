from codecs import open
from os.path import abspath, dirname, join
from subprocess import call

from setuptools import Command, find_packages, setup

from infdata import __version__

this_dir = abspath(dirname(__file__))
with open(join(this_dir, 'README.md'), encoding='utf-8') as file:
    long_description = file.read()


class RunTests(Command):
    """Run all tests."""
    description = 'run tests'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Run all tests!"""
        errno = call(['py.test', '--cov=infdata', '--cov-report=term-missing'])
        raise SystemExit(errno)


setup(
    name='infdata',
    version=__version__,
    description='Package management command for data.',
    long_description=long_description,
    url='https://github.com/infamily/infinity-data',
    author='Mindey I.',
    author_email='mindey@qq.com',
    license='UNLICENSE',
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: Public Domain',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='inf',
    packages=find_packages(exclude=['docs', 'tests*']),
    install_requires=[
        'docopt',
        'boltons',
        'slumber',
        'requests',
        'json-lines',
        'progress',
        'asyncio==3.4.3',
        'aiohttp==2.3.10',
        'feedparser',
        'wxpy'
    ],
    extras_require={
        'test': ['coverage', 'pytest', 'pytest-cov'],
    },
    entry_points={
        'console_scripts': [
            'inf=infdata.cli:main',
        ],
    },
    cmdclass={'test': RunTests},
)
