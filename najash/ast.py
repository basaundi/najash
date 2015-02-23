
from ast import parse as from_text, walk
from pkgutil import find_loader

def from_file(fd, filename=None):
  if not filename:
    filename = '<unknown>'
    if hasattr(fd, 'name'):
      filename = fd.name
  return from_text(fd.read(), filename)

def from_name(mod):
    return from_text(find_loader(mod).get_source(mod))

def dependencies(unit):
    deps = set()
    for node in walk(unit):
        nname = type(node).__name__
        if nname == 'Import':
            for name in node.names:
                deps.add(name.name)
        elif nname == 'ImportFrom':
            if hasattr(node, 'module'):
                deps.add(node.module)
            for name in node.names:
                try:
                    loader = find_loader(node.module)
                except ImportError:
                    loader = None
                if not loader:
                    print('No module "', node.module, '" found')
                    continue
                if not loader.is_package(node.module):
                    continue
                mod = '.'.join((node.module, name.name))
                loader = find_loader(mod)
                if loader:
                    deps.add(mod)
    return deps

