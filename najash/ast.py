
from ast import parse as from_text, walk
from importlib import find_loader

def from_file(fd, filename=None):
  if not filename:
    filename = '<unknown>'
    if hasattr(fd, 'name'):
      filename = fd.name
  return from_text(fd.read(), filename)

def from_name(mod):
    return from_text(find_loader(mod).get_source(mod))

def dependencies(unit, path = None):
    deps = set()
    for node in walk(unit):
        nname = type(node).__name__
        if nname == 'Import':
            for name in node.names:
                deps.add(name.name)
        elif nname == 'ImportFrom':
            prefix = None
            if node.level:
                paths = path.split('.')
                for i in range(node.level):
                    paths.pop()
                prefix = '.'.join(paths)

            if node.module:
                if prefix:
                    prefix += '.' + node.module
                else:
                    prefix = node.module
                deps.add(prefix)

            for name in node.names:
                try:
                    loader = find_loader(prefix)
                except ImportError:
                    loader = None
                if not loader:
                    print('No module "', prefix, '" found')
                    continue

                if not loader.is_package(prefix):
                    continue

                mod = '.'.join((prefix, name.name))
                loader = find_loader(mod)
                if loader:
                    deps.add(mod)
    return deps

