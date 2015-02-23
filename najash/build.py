
from sys import builtin_module_names
from . import ast, gen

class Builder:
    def __init__(self, out):
        self.out = out
        self.built = set()
        self.blacklist = (
            'os.path', 'main', 'os', 'array', 'importlib', 're',
            'pkgutil', 'collections', 'tokenize', 'argparse',
            'inspect', 'imp'
        )

    def transpile(self, unit, name='__main__'):
        tokens = gen.Tokens(unit, name)
        return gen.untokenize(tokens)

    def build(self, unit, name='__main__'):
        self.built.add(name)
        for mod in ast.dependencies(unit, name):
            if not self.needed(mod):
                continue
            print('%%%', mod)
            dep = ast.from_name(mod)
            self.build(dep, mod)
        self.out.write(self.transpile(unit, name))

    def build_file(self, inp):
        root = ast.from_file(inp)
        self.build(root)

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

