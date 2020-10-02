#SPDX-License-Identifier: MIT
"""
Runs Augur with Gunicorn when called
"""

import os
import sys
import click
import importlib
import augur.application

CONTEXT_SETTINGS = dict(auto_envvar_prefix='AUGUR')

class AugurMultiCommand(click.MultiCommand):
    def __commands_folder(self):
        return os.path.abspath(os.path.dirname(__file__))

    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(self.__commands_folder()):
            if not filename.startswith('_') and filename.endswith('.py'):
                rv.append(filename[:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        try:
            module = importlib.import_module('.' + name, 'augur.cli')
            return module.cli
        except ModuleNotFoundError as e:
            pass

@click.command(cls=AugurMultiCommand, context_settings=CONTEXT_SETTINGS)
@click.pass_context
def run(ctx):
    """
    Augur is an application for open source community health analytics
    """
    return ctx
