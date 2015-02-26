
from ast import parse as from_text, walk
import sys
from os.path import dirname
from importlib.machinery import PathFinder

def from_file(fd, filename=None):
  if not filename:
    filename = '<unknown>'
    if hasattr(fd, 'name'):
      filename = fd.name
  return from_text(fd.read(), filename)

def from_filename(fname):
    with open(fname) as fd:
        ast = from_file(fd, fname)
    return ast

def name_path(mod, pkg):
    loader = None
    parent = None
    path = sys.path
    if pkg:
        pkg_path = name_path(pkg, None)
        if pkg_path:
            path = [dirname(pkg_path), ] + path
    parts = mod.split('.')
    prefix = ''
    for part in parts:
        if not part:
            prefix += '.'
            continue
        name = prefix + part
        loader = PathFinder.find_module(name, path)
        prefix = ''
        if loader:
            parent = dirname(loader.path)
            if loader.is_package(name):
                path = parent,
            else:
                path = tuple()
    if not loader:
        return None
    return loader.path

def from_name(mod, pkg = None):
    path = name_path(mod, pkg)
    if not path:
        raise ImportError(mod)
    return from_filename(path)

def dependencies(unit, current):
    deps = []
    for node in walk(unit):
        nname = type(node).__name__
        if nname == 'Import':
            for name in node.names:
                if name.name not in deps: deps.append(name.name)
        elif nname == 'ImportFrom':
            module = ''
            if node.level:
                module = '.' * (node.level - (0 if node.module else 1))

            if node.module:
                module += node.module

            for name in node.names:
                candidate = module + '.' + name.name
                path = name_path(candidate, current)
                if path:
                    if candidate not in deps: deps.append(candidate)
                else:
                    if module not in deps: deps.append(module)
    return deps

