import ast
import tokenize

class Tokens:
    OPERATORS = tuple(x.strip() for x in """
    (       )       [       ]       .
    +       -       *       **      /       //      %
    <<      >>      &       |       ^       ~
    <       >       <=      >=      ==      !=""".split())

    def __init__(self, root, name):
        self.tokens = self.generate(root)
        self.name = name
        self.indentation = 0

    def __iter__(self):
        return self

    def __next__(self):
        token = next(self.tokens)
        if token:
            type_ = tokenize.NAME
            if token[0] == '\n':
                type_ = tokenize.NEWLINE
            if token[0] == '\r':
                type_ = tokenize.NL
                token = '\n'
            elif token[0] == '\t':
                type_ = tokenize.INDENT
            elif token[0] == '\b':
                type_ = tokenize.DEDENT
            elif token[0] == "'":
                type_ = tokenize.STRING
            elif token in self.OPERATORS:
                type_ = tokenize.OP
            return (type_, token)
        raise StopIteration()

    def generate(self, node):
        type_ = type(node).__name__
        if hasattr(self, type_):
            yield from getattr(self, type_)(node)
        else:
            yield from ('[', type_, ']')

    def indent(self):
        self.indentation += 1
        yield '\t' * self.indentation

    def dedent(self):
        self.indentation -= 1
        yield '\b'

    def stmts(self, stmts):
        yield from self.indent()
        yield '{'
        yield '\r'
        for stmt in stmts:
            yield from self.generate(stmt)
            yield '\n'
        yield from self.dedent()
        yield '}'

    def expr(self, expr):
        if hasattr(expr, 'ctx') and isinstance(expr.ctx, ast.Store):
            yield 'var'
        yield from self.generate(expr)

    def Name(self, node):
        yield node.id

    def NameConstant(self, node):
        if node.value is False:
            yield 'false'
        elif node.value is True:
            yield 'true'
        else:
            yield repr(node.value)

    def Attribute(self, node):
        yield from self.expr(node.value)
        yield '.'
        yield node.attr
        
    def Expr(self, node):
        yield from self.expr(node.value)

    def Str(self, node):
        yield repr(node.s)

    def Num(self, node):
        yield str(node.n)

    def Tuple(self, node):
        if isinstance(node.ctx, ast.Store):
            yield '['
        else:
            yield from ('tuple', '(')
        comma = False
        for expr in node.elts:
            if comma:
                yield ','
            yield from self.expr(expr)
            comma = True
        if isinstance(node.ctx, ast.Store):
            yield ']'
        else:
            yield ')'

    def List(self, node):
        yield '['
        comma = False
        for expr in node.elts:
            if comma:
                yield ','
            yield from self.expr(expr)
            comma = True
        yield ']'

    def Call(self, node):
        yield from self.expr(node.func)
        yield '('
        comma = False
        for expr in node.args:
            if comma:
                yield ','
            yield from self.expr(expr)
            comma = True
        yield ')'

    def Return(self, node):
        yield 'return'
        if node.value:
            yield from self.expr(node.value)

    def Assign(self, node):
        for expr in node.targets:
            yield from self.expr(expr)
            yield '='
            yield from self.expr(node.value)

    def If(self, node):
        yield from ('if', '(')
        yield from self.expr(node.test)
        yield ')'
        yield from self.stmts(node.body)

    def For(self, node):
        yield from ('for', '(')
        yield from self.expr(node.target)
        yield 'of'
        yield from self.expr(node.iter)
        yield ')'
        yield from self.stmts(node.body)

    def FunctionDef(self, node):
        yield from ('$def', '(', 'function', node.name, '(', ')')
        yield from self.stmts(node.body)
        yield ')'

    def ClassDef(self, node):
        yield from ('$class', '(', repr(node.name), ',', 'function', '(', ')')
        yield from self.stmts(node.body)
        yield ')'

    def Import(self, node):
        for alias in node.names:
            name = alias.name
            asname = alias.asname if alias.asname else alias.name
            yield from (asname, '=', '$import', '(', repr(name), ')')

    def Module(self, node):
        if self.name != '__main__':
            yield from ('$module', '(', repr(self.name), ',', 'function', '(', ')')
            yield from ('{', 'with', '(', 'this', ')')
        yield from self.stmts(node.body)
        if self.name != '__main__':
            yield ')'

untokenize = tokenize.untokenize

