
from sys import builtin_module_names, path
import os.path
from importlib.machinery import PathFinder

from . import ast, gen


class Builder:
    def __init__(self, out):
        self.out = out
        self.built = set()
        path.insert(0, os.path.join(os.path.dirname(__file__), 'python.js'))
        self.blacklist = (
            'os.path', 'main', 'os', 'array', 'importlib',
            'pkgutil', 'collections', 'tokenize', 'argparse',
            'wsgiref.simple_server', 'time',
            'types', 'copy'
        )

    def transpile(self, unit, name='__main__'):
        tokens = gen.Tokens(unit, name)
        return gen.untokenize(tokens)

    def build(self, unit, name='__main__'):
        self.built.add(name)
        for mod in ast.dependencies(unit, name):
            if not self.needed(mod):
                continue
            self.build_mod(mod, name)
            self.out.write('\n')
        self.out.write(self.transpile(unit, name))

    @staticmethod
    def get_alternative(mod, pkg=None):
        if mod.startswith('.') and pkg:
            loader = PathFinder.find_module(pkg, path)
            if loader:
                # modpath = ast.name_path(mod, pkg)
                mod = pkg + mod

        fname = mod.replace('.', '/') + '.js'  # FIXME
        for p in path:
            if os.path.isdir(p):
                candidate = os.path.join(p, fname)
                if os.path.isfile(candidate):
                    return candidate, mod
        return None, None

    def build_mod(self, mod, pkg=None, wrap=True):
        candidate, modname = self.get_alternative(mod, pkg)
        if candidate:
            with open(candidate) as fd:
                if wrap:
                    self.out.write('\n$module("')
                    self.out.write(modname)
                    self.out.write('", function(){\n')
                self.out.write(fd.read())
                if wrap:
                    self.out.write('\n})')
            return

        dep = ast.from_name(mod, pkg)
        self.build(dep, mod)

    def build_filename(self, fname):
        path.append(os.path.dirname(fname))
        with open(fname, 'r') as fd:
            self.build_file(fd)

    def build_file(self, inp):
        self.out.write('(function(){\n')
        self.build_mod('builtins', wrap=False)

        self.out.write('\n')
        # self.out.write('\n$module("__main__", function()')
        root = ast.from_file(inp)
        self.build(root)
        # self.out.write(')\n')

        self.out.write('\n$import("__main__")})()')

    def needed(self, mod):
        if mod in builtin_module_names:
            return False
        if mod in self.built:
            return False
        if mod.startswith('_'):
            return False
        for blackm in self.blacklist:
            if mod.startswith(blackm):
                return False
        return True
