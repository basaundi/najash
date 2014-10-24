
from ast import AST, NodeVisitor, parse, iter_fields

from_text = parse

def from_file(fd, filename=None):
  if not filename:
    filename = '<unknown>'
    if hasattr(fd, 'name'):
      filename = fd.name
  return from_text(fd.read(), filename)

