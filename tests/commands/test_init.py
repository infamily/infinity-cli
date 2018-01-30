"""Tests for our `inf init` subcommand."""


from subprocess import PIPE, Popen as popen
from unittest import TestCase


class TestInit(TestCase):
    def test_returns_multiple_lines(self):
        output = popen(['inf', 'init'], stdout=PIPE).communicate()[0]
        lines = output.decode('utf-8').split('\n')
        self.assertTrue(len(lines) != 1)

    def test_returns_init(self):
        output = popen(['inf', 'init'], stdout=PIPE).communicate()[0]
        self.assertTrue('Initializing...\n\nDone.' in output.decode('utf-8'))
