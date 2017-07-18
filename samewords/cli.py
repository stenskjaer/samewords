#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Command line interface director for the samewords script.
"""

import samewords
import argparse
import os

def parse_arguments():
    parser = argparse.ArgumentParser(
        prog='samewords',
        usage='%(prog)s [options] FILE',
        description='Annotate potentially ambiguous words in critical text editions '
                    'made with LaTeX and reledmac.')
    parser.add_argument('file', metavar='FILE', type=str, nargs=1,
                        help='Location of local file to be processed.')
    parser.add_argument('--output', dest='location', action='store',
                        help="Location of the output. You can specify a filename as part of the "
                             "address. If you don't do that, the name of the input file will be "
                             "put in the directory specified. (default: '%(default)s')")
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s {}'.format(samewords.__version__),
                        help="Show version and exit.")

    return vars(parser.parse_args())

def main():
    # Read command line arguments
    args = parse_arguments()

    filename = args['file'][0]
    output = args['location']

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
