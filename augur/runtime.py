#SPDX-License-Identifier: MIT
"""
Runs Augur with Gunicorn when called
"""

import os
import sys
import click
from functools import update_wrapper
import augur.application

CONTEXT_SETTINGS = dict(auto_envvar_prefix='AUGUR')

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
        mod = __import__('augur.cli.' + name,
                         None, None, ['cli'])
        return mod.cli

def pass_application(f):
    @click.pass_context
    def new_func(ctx, *args, **kwargs):
        ctx.obj = augur.application.Application()
        return ctx.invoke(f, ctx.obj, *args, **kwargs)
    return update_wrapper(new_func, f)

@click.command(cls=AugurMultiCommand, context_settings=CONTEXT_SETTINGS)
@click.pass_context
def run(ctx):
    """
    Augur is an application for open source community health analytics
    """
    app = augur.application.Application()
    ctx.obj = app
    return ctx.obj
