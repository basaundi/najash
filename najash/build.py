
from sys import builtin_module_names, path
import os.path

from . import ast, gen

class Builder:
    def __init__(self, out):
        self.out = out
        self.built = set()
        path.append(os.path.join(os.path.dirname(__file__), 'python.js'))
        self.blacklist = (
            'os.path', 'main', 'os', 'array', 'importlib',
            'pkgutil', 'collections', 'tokenize', 'argparse',
            'inspect', 'imp', 'glob'
        )

    def transpile(self, unit, name='__main__'):
        tokens = gen.Tokens(unit, name)
        return gen.untokenize(tokens)

    def build(self, unit, name='__main__'):
        self.built.add(name)
        for mod in ast.dependencies(unit, name):
            if not self.needed(mod):
                continue
            self.build_mod(mod)
            self.out.write('\n')
        self.out.write(self.transpile(unit, name))

    def build_mod(self, mod):
        fname = mod.replace('.', '/') + '.js'
        for p in path:
            if os.path.isdir(p):
                candidate = os.path.join(p, fname)
                if os.path.isfile(candidate):
                    self.out.write(open(candidate).read())
                    return

        dep = ast.from_name(mod)
        self.build(dep, mod)

    def build_filename(self, fname):
        path.append(os.path.dirname(fname))
        with open(fname, 'r') as fd:
            self.build_file(fd)

    def build_file(self, inp):
        self.out.write('(function(){\n')
        self.build_mod('builtins')

        self.out.write('\n')
        #self.out.write('\n$module("__main__", function()')
        root = ast.from_file(inp)
        self.build(root)
        #self.out.write(')\n')

        self.out.write('\n$import("__main__")})()')

    def needed(self, mod):
        if mod in builtin_module_names:
            return False
        if mod in self.built:
            return False
        if mod.startswith('_'):
            return False
        if mod in self.blacklist:
            return False
        return True

