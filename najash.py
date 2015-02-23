#!/usr/bin/env python3

"""
najash
======

Tools for javascript, in python.
"""

__author__ = 'Ander Martinez <ander.basaundi@gmail.com>'

from sys import stdout, stdin
from argparse import ArgumentParser, FileType

from najash.build import Builder

def arguments():
    arp = ArgumentParser()
    arp.add_argument('inp', nargs='?', type=FileType('r'), default=stdin)
    arp.add_argument('out', nargs='?', type=FileType('w'), default=stdout)
    return arp.parse_args()


def main():
    args = arguments()
    builder = Builder(args.out)
    builder.build_file(args.inp)

if __name__ == '__main__':
    main()

