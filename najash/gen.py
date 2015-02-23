import ast
import tokenize

class Tokens:
    OPERATORS = tuple(x.strip() for x in """
    .       (       )       [       ]       ,
    +       -       *       **      /       //      %
    <<      >>      &       |       ^       ~
    <       >       <=      >=      ==      !=""".split())

    OPERATOR = {
        ast.Add:  '+',
        ast.Sub:  '-',
        ast.Mult: '*',
        ast.Div:  '/',
        ast.Mod:  '%',
        #ast.Pow:   '+',
        ast.LShift: '<<',
        ast.RShift: '>>',
        ast.BitOr: '|',
        ast.BitXor: '^',
        ast.BitAnd: '&',
        #ast.FloorDiv: '+'
    }

    CMPOP = {
        ast.Eq:    '===',
        ast.NotEq: '!==',
        ast.Lt:    '<',
        ast.LtE:   '<=',
        ast.Gt:    '>',
        ast.GtE:   '>=',
        #ast.Is: 'is',
        #ast.IsNot: 'isnt',
        #ast.In: 'in',
        #ast.NotIn: 'notin'
    }

    def __init__(self, root, name):
        self.tokens = self.generate(root)
        self.name = name
        self.indentation = 0
        self.scope = [root]

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
        yield from '{\r'
        if stmts:
            if isinstance(stmts[0], ast.Expr) and \
                isinstance(stmts[0].value, ast.Str): # docstring
                stmts = stmts[1:]
            for stmt in stmts:
                yield from self.generate(stmt)
                yield '\n'
        yield from self.dedent()
        yield '}'

    def expr(self, expr, not_decl = None):
        #if not not_decl and hasattr(expr, 'ctx') and \
        #    isinstance(expr.ctx, ast.Store):
        #    yield 'var'
        yield from self.generate(expr)

    def exprs(self, exprs):
        comma = False
        for expr in exprs:
            if comma:
                yield ','
            yield from self.expr(expr, True)
            comma = True

    def operation(self, l, op, r, op_defs):
        if type(op) in op_defs:
            yield from l
            yield op_defs[type(op)]
            yield from r
        else:
            yield from ('${}'.format(type(op).__name__), '(')
            yield from l
            yield ','
            yield from r
            yield ')'

    def has_yield(self, body):
        for stmt in body:
            if isinstance(stmt, (ast.Yield, ast.YieldFrom)):
                return True
            if isinstance(stmt, (ast.With, ast.For, ast.While, ast.If, ast.Try)):
                if self.has_yield(stmt.body):
                    return True
            if isinstance(stmt, (ast.For, ast.While, ast.If, ast.Try)):
                if self.has_yield(stmt.orelse):
                    return True
            if isinstance(stmt, ast.Try):
                if self.has_yield(stmt.finalbody):
                    return True
        return False


    def Module(self, node):
        node.locals = []
        if self.name: # != '__main__':
            yield from ('$module', '(', repr(self.name), ',',
                        'function', '(', ')')
            yield from self.stmts(node.body)
            yield ')'
        else:
            yield from self.stmts(node.body)

    ### stmt ###

    def FunctionDef(self, node):
        # (identifier name, arguments args, 
        #                   stmt* body, expr* decorator_list, expr? returns)
        yield from ('$def', '(', 'function')
        if self.has_yield(node.body):
            yield '*'
        yield from (node.name, '(')

        node.locals = []
        # (arg* args, arg? vararg, arg* kwonlyargs, expr* kw_defaults,
        #        arg? kwarg, expr* defaults)
        tail = False
        for arg in node.args.args:
            yield arg.arg
            node.locals.append(arg.arg)
            tail = True

        yield ')'
        self.scope.append(node)
        yield from self.stmts(node.body)
        self.scope.pop()
        yield ')'

    def ClassDef(self, node):
        yield from ('$class', '(', repr(node.name), ',', 'function', '(', ')')
        yield from self.stmts(node.body)
        yield ')'

    def Return(self, node):
        yield 'return'
        if node.value:
            yield from self.expr(node.value)

    # TODO: Delete

    def Assign(self, node):
        for expr in node.targets:
            yield from self.expr(expr)
            yield '='
            yield from self.expr(node.value)

    # TODO: AugAssign

    def For(self, node):
        yield from ('for', '(')
        yield from self.expr(node.target)
        yield 'of'
        yield from self.expr(node.iter)
        yield ')'
        yield from self.stmts(node.body)

    def While(self, node):
        yield from ('while', '(')
        yield from self.expr(node.test)
        yield ')'
        yield from self.stmts(node.body)

    def If(self, node):
        yield from ('if', '(')
        yield from self.expr(node.test)
        yield ')'
        yield from self.stmts(node.body)

    # TODO: With
    # TODO: Raise

    def Try(self, node):
        yield 'try'
        yield from self.stmts(node.body)
        if node.handlers:
            yield from ('catch', '(' , '$e', ')')
            yield from self.indent()
            yield from '{\r'
            for handler in node.handlers:
                if handler.name:
                    yield from ('var', handler.name, '=', '$e')
                if handler.type:
                    yield from ('if', '(', '$e', 'instanceof')
                    yield from self.expr(handler.type)
                    yield ')'
                yield from self.stmts(handler.body)
            if not node.orelse:
                yield from ('else', '{', 'throw', '$e', '}')
                yield from self.dedent()
                yield from '\r}'
        if node.orelse:
            yield 'else'
            yield from self.stmts(node.orelse)
            yield from self.dedent()
            yield from '\r}'
        if node.finalbody:
            yield 'finally'
            yield from self.stmts(node.finalbody)

    # TODO: Assert

    def Import(self, node):
        for alias in node.names:
            name = alias.name
            asname = alias.asname if alias.asname else alias.name
            # yield from ('var', asname, '=')
            yield from ('$import', '(', repr(name))
            if alias.asname:
                yield repr(asname)
            yield from ')\n'

    def ImportFrom(self, node):
        for alias in node.names:
            name = alias.name
            asname = alias.asname if alias.asname else alias.name
            #if name != '*':
            #    yield from ('var', asname, '=')
            yield from ('$import', '(', repr(node.module),
                         ',', repr(name))
            if alias.asname:
                yield repr(asname)
            yield from ')\n'
    # TODO: Global
    # TODO: Nonlocal

    def Expr(self, node):
        yield from self.expr(node.value)

    # TODO: Pass
    # TODO: Break
    # TODO: Continue

    ### expr ###
    #def BoolOp(self, node):
    #    pass

    def BinOp(self, node):
        l = self.expr(node.left)
        r = self.expr(node.right)
        yield from self.operation(l, node.op, r, self.OPERATOR)

    # TODO: UnaryOp
    # TODO: Lambda
    # TODO: IfExp

    def Dict(self, node):
        yield from ('dict', '(', '{')
        tail = False
        for k, v in zip(node.keys, node.values):
            if tail:
                yield ','
            yield from self.expr(k)
            yield ':'
            yield from self.expr(v)
            tail = True
        yield from '})'

    # TODO: Set
    # TODO: ListComp(expr elt, comprehension* generators)
    # TODO: SetComp(expr elt, comprehension* generators)
    # TODO: DictComp(expr key, expr value, comprehension* generators)
    # TODO: GeneratorExp(expr elt, comprehension* generators)
    # TODO: Yield(expr? value)
    # TODO: YieldFrom(expr value)

    def Compare(self, node):
        l = []
        if not isinstance(node.left, ast.Name):
            l.append('(')
            l.extend(self.expr(node.left))
            l.append(')')
        else:
            l.extend(self.expr(node.left))
        for op, comp in zip(node.ops, node.comparators):
            r = self.expr(comp)
            yield from self.operation(l, op, r, self.CMPOP)

    def Call(self, node):
        # Call(expr func, expr* args, keyword* keywords,
        #     expr? starargs, expr? kwargs)
        yield from self.expr(node.func)
        yield '('
        yield from self.exprs(node.args)
        yield ')'
    
    def Num(self, node):
        yield str(node.n)

    def Str(self, node):
        yield repr(node.s)

    # TODO: Bytes(bytes s)

    def NameConstant(self, node):
        if node.value is False:
            yield 'false'
        elif node.value is True:
            yield 'true'
        else:
            yield repr(node.value)

    # TODO: Ellipsis

    #### in assignment context ####
    def Attribute(self, node):
        # Attribute(expr value, identifier attr, expr_context ctx)
        yield from self.expr(node.value)
        yield '.'
        yield node.attr

    # TODO: Subscript(expr value, slice slice, expr_context ctx)
    # TODO: Starred(expr value, expr_context ctx)

    def Name(self, node):
        # Name(identifier id, expr_context ctx)
        if node.id in self.scope[-1].locals:
            if isinstance(node.ctx, ast.Store):
                yield 'var'
        else:
            yield from ('this', '.')
        yield node.id

    def List(self, node):
        yield '['
        yield from self.exprs(node.elts)
        yield ']'

    def Tuple(self, node):
        if isinstance(node.ctx, ast.Store):
            yield '['
            yield from self.exprs(node.elts)
            yield ']'
        else:
            yield from ('tuple', '(')
            yield from self.exprs(node.elts)
            yield ')'

untokenize = tokenize.untokenize

