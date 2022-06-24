#SPDX-License-Identifier: MIT
import click
from functools import update_wrapper

from augur.application import Application
from augur.config import AugurConfig
from augur.logging import AugurLogging, ROOT_AUGUR_DIRECTORY

def pass_application(f):
    @click.pass_context
    def new_func(ctx, *args, **kwargs):
        ctx.obj = Application()
        return ctx.invoke(f, ctx.obj, *args, **kwargs)
    return update_wrapper(new_func, f)

def pass_config(f):
    @click.pass_context
    def new_func(ctx, *args, **kwargs):
        ctx.obj = Application(offline_mode=True).config
        return ctx.invoke(f, ctx.obj, *args, **kwargs)
    return update_wrapper(new_func, f)

def pass_logs_dir(f):
    @click.pass_context
    def new_func(ctx, *args, **kwargs):
        config = AugurConfig(ROOT_AUGUR_DIRECTORY)
        ctx.obj = AugurLogging.get_log_directories(config, reset_logfiles=False)
        return ctx.invoke(f, ctx.obj, *args, **kwargs)
    return update_wrapper(new_func, f)

def initialize_logging(f):
    def new_func(*args, **kwargs):
        AugurLogging(reset_logfiles=False)
        return f(*args, **kwargs)
    return update_wrapper(new_func, f)