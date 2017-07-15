#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Samewords annotates potentially ambiguous words in critical text editions
made with LaTeX and reledmac.

Usage: samewords [options] <file>

Arguments:
  <file>                Location of local file to be processed.

Options:
  --output <location>      Location of output. You can specify a filename as
                           part of the address. If you don't do that, the name
                           of the input file will be used.
  --include-macros <file>  File listing the macros that should be ignored when
                           comparing text segments.
  -v, --version            Show version and exit.
  -h, --help               Show this help message and exit.
"""

import samewords
import docopt
import os


def cl_arguments():
    try:
        return docopt.docopt(__doc__, version=samewords.__version__)
    except docopt.DocoptExit:
        return {}

ARGS = cl_arguments()

def main():
    args = cl_arguments()
    print(args)
    filename = args['<file>']
    output = args['--output']

    if not output:
        print(samewords.core.process_document(filename))
    else:
        if os.path.isdir(output):
            _, output_filename = os.path.split(filename)
            output_dir = output
        elif os.path.isfile(output):
            answer = input('The file {} already exists. Overwrite (y/n)? '.format(output))
            if answer.lower() == 'y':
                output_dir, output_filename = os.path.split(output)
            else:
                print('Quit.')
                exit(0)
        else:
            output_dir, output_filename = os.path.split(output)
        output_result = os.path.join(output_dir, output_filename)

        # Starting conversion
        print('Starting conversion.')
        output_content = samewords.core.process_document(filename)
        print('Conversion succeeded. Saving file to {}'.format(output_result))
        with open(output_result, mode='w') as f:
            f.write(output_content)
