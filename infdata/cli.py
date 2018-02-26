"""
inf

Usage:
  inf login
  inf login <server>
  inf switch
  inf list
  inf push <datafile>
  inf pull <name==version> [-p, --page-size <page_size>]
  inf run <task_name>
  inf tasks
  inf -h | --help
  inf --version
  inf init

Options:
  -h --help                         Show this screen.
  --version                         Show version.

Examples:
  inf init
  inf push data.json
  inf pull example.com/people==crawler-1.0.0

Help:
  For help using this tool, please open an issue on the Github repository:
  https://github.com/infamily/infinity-data
"""


from inspect import getmembers, isclass

from docopt import docopt

from . import __version__ as VERSION


def main():
    """Main CLI entrypoint."""
    import infdata.commands
    options = docopt(__doc__, version=VERSION)

    # Here we'll try to dynamically match the command the user is trying to run
    # with a pre-defined command class we've already created.
    for (k, v) in options.items():
        if hasattr(infdata.commands, k) and v:
            module = getattr(infdata.commands, k)
            infdata.commands = getmembers(module, isclass)
            command = [command[1] for command in infdata.commands if command[0] != 'Base'][0]
            command = command(options)
            command.run()
