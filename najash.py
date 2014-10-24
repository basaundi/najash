#!/usr/bin/env python3

"""
najash
======

Tools for javascript, in python.
"""

__author__ = 'Ander Martinez <ander.basaundi@gmail.com>'

from sys import stdout, stdin
from argparse import ArgumentParser, FileType

from najash.python import ast as py_ast
from najash.javascript.python_transducer import from_python
from najash.javascript.gen import from_ast

def main():
  arp = ArgumentParser()
  arp.add_argument('inp', nargs='?', type=FileType('r'), default=stdin)
  arp.add_argument('out', nargs='?', type=FileType('w'), default=stdout)
  args = arp.parse_args()

  p_ast = py_ast.from_file(args.inp)
  j_ast = from_python(p_ast)
  j_src = from_ast(j_ast)
  args.out.write(j_src)

if __name__ == '__main__':
  main()

