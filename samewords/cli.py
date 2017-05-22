#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Samewords annotates potentially ambiguous words in critical text editions
made with LaTeX and reledmac.

Usage: samewords [options] <file>

Arguments:
  <file>                Location of local file to be processed.

Options:
  --output <location>   Location of output. You can specify a filename as part of
                        the address. If you don't do that, the name of the input
                        file will be used.
  -v, --version         Show version and exit.
  -h, --help            Show this help message and exit.
"""

import samewords
from docopt import docopt
import os

def main():
    # Read command line arguments
    args = docopt(__doc__, version=samewords.__version__)

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
