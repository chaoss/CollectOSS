from functools import update_wrapper

import click
from augur.application import Application

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