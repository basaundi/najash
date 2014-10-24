
from ..python.ast import NodeVisitor as PythonNodeVisitor
from . import ast

class PythonTransducer(PythonNodeVisitor):
  def generic_visit(self, node):
    node_class = node.__class__.__name__
    method = 'visit_' + node_class

    if hasattr(ast, node_class):
      cls = getattr(ast, node_class)
      children = [self.visit(getattr(node, f)) for f in cls._fields]
      return cls(*children)

    raise NotImplementedError(
      "Transduction of nodes of type '{}' not implemented'".format(node_class))
  
  def visit_str(self, s): return s
  def visit_int(self, n): return n
  def visit_list(self, lst):
    return [self.visit(n) for n in lst]
    
def from_python(ast):
  from .python_transducer import PythonTransducer
  py2js = PythonTransducer()
  return py2js.visit(ast)
  
