#!/usr/bin/env python3

"""
najash
======

Tools for javascript, in python.
"""

from sys import stdout, stdin, path
from argparse import ArgumentParser, FileType
import os.path

from najash.build import Builder


__author__ = 'Ander Martinez <ander.basaundi@gmail.com>'


def arguments():
    arp = ArgumentParser()
    arp.add_argument('inp', nargs='?', type=FileType('r'), default=stdin)
    arp.add_argument('out', nargs='?', type=FileType('w'), default=stdout)
    return arp.parse_args()


def main():
    args = arguments()
    builder = Builder(args.out)
    if args.inp is not stdin:
        path.append(os.path.dirname(os.path.abspath(args.inp.name)))
    builder.build_file(args.inp)

if __name__ == '__main__':
    main()
