#SPDX-License-Identifier: MIT
"""
Runs Augur with Gunicorn when called
"""


import os
import augur.application
import sys
import click
import logging
import coloredlogs
import colored
from augur.util import logger


CONTEXT_SETTINGS = dict(auto_envvar_prefix='AUGUR_CLI')


__pass_decorator = click.make_pass_decorator(augur.application.Application)
def pass_application(function):
    def decorator(app, *args, **kwargs):
        function(app, *args, **kwargs)
    return __pass_decorator(decorator)


class AugurMultiCommand(click.MultiCommand):

    def __commands_folder(self):
        return os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'cli')
        )

    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(self.__commands_folder()):
            if not filename.startswith('_') and filename.endswith('.py'):
                rv.append(filename[:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        try:
            if sys.version_info[0] == 2:
                name = name.encode('ascii', 'replace')
            mod = __import__('augur.cli.' + name,
                             None, None, ['cli'])
        except ImportError as e:
            logger.debug(e)
            return
        return mod.cli



@click.command(cls=AugurMultiCommand, context_settings=CONTEXT_SETTINGS)
@click.pass_context
def run(ctx):
    """
    Augur is an application for open source community health analytics
    """
    app = augur.application.Application()
    ctx.obj = app
    return ctx.obj


if __name__ == '__main__':
    run()
