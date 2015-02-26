
from ast import parse as from_text, walk
from importlib import find_loader
import os.path

def from_file(fd, filename=None):
  if not filename:
    filename = '<unknown>'
    if hasattr(fd, 'name'):
      filename = fd.name
  return from_text(fd.read(), filename)

def from_name(mod):
    loader = find_loader(mod)
    if not loader:
        raise ImportError(mod)
    src = loader.get_source(mod)
    if not src:
        raise ImportError(mod)
    return from_text(src)

def is_package(path):
    loader = find_loader(path)
    if not loader:
        return False
    return loader.is_package(path)

def is_submodule(module, package):
    if not is_package(package):
        return False
    loader = find_loader(package)
    path = os.path.dirname(loader.path)
    fpath = os.path.join(path, module)
    return os.path.isdir(fpath) or os.path.isfile(fpath+'.py')

def dependencies(unit, path = None):
    deps = []
    for node in walk(unit):
        nname = type(node).__name__
        if nname == 'Import':
            for name in node.names:
                if name.name not in deps: deps.append(name.name)
        elif nname == 'ImportFrom':
            module = node.module
            if node.level:
                paths = path.split('.')
                if is_package(path):
                    paths.append('__init__')
                for i in range(node.level):
                    paths.pop()
                if module:
                    paths.append(module)
                module = '.'.join(paths)

            for name in node.names:
                if is_submodule(name.name, module):
                    mod = module + '.' + name.name
                    if mod not in deps: deps.append(mod)
    return deps

