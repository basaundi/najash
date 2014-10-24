
class AST(object):
  def __init__(self, *args):
    cls = self.__class__
    assert len(cls._fields) == len(args)
    for i, f in enumerate(cls._fields):
      setattr(self, f, args[i])
  
class Module(AST): _fields = ('body',)
class Expr(AST): _fields = ('value',)
class Str(AST): _fields = ('s',)
class Num(AST): _fields = ('n',)
class BinOp(AST): _fields = ('left', 'op', 'right')
class Add(AST): _fields = tuple()
class Sub(AST): _fields = tuple()
class Mult(AST): _fields = tuple()
class Div(AST): _fields = tuple()

class Assign(AST): _fields = ('targets', 'value')
class Name(AST): _fields = ('id', 'ctx')
class Store(AST): _fields = tuple()
class Load(AST): _fields = tuple()

