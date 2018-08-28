import pkgutil
import importlib

__all__ = []
loaded = []

__path__ = pkgutil.extend_path(__path__, __name__)
for importer, modname, ispkg in pkgutil.walk_packages(path=__path__, prefix=__name__+'.'):
    if ispkg:
        module = importlib.import_module(modname)
        __all__.append(modname)
        loaded.append(module)