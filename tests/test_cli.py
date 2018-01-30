"""Tests for our main inf CLI module."""


from subprocess import PIPE, Popen as popen
from unittest import TestCase

from src import __version__ as VERSION


class TestHelp(TestCase):
    def test_returns_usage_information(self):
        output = popen(['inf', '-h'], stdout=PIPE).communicate()[0]
        self.assertTrue('Usage:' in output.decode('utf-8'))

        output = popen(['inf', '--help'], stdout=PIPE).communicate()[0]
        self.assertTrue('Usage:' in output.decode('utf-8'))


class TestVersion(TestCase):
    def test_returns_version_information(self):
        output = popen(['inf', '--version'], stdout=PIPE).communicate()[0]
        self.assertEqual(output.decode('utf-8').strip(), VERSION)
