#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Command line interface director for the samewords script.
"""

import json

import samewords
import argparse
import os

from samewords import settings


def load_config(filename):
    """Load and read in configuration from local config file.

    :return Dictionary of the configuration."""
    try:
        with open(filename, mode='r') as f:
            conf = json.loads(f.read())
        return conf
    except json.decoder.JSONDecodeError as e:
        raise
    except FileNotFoundError:
        return {}


def parse_config_file(filename: str) -> object:
    """Parse the config file and update the global settings.
    If successful, return settings, otherwise return None."""
    filename = os.path.expanduser(filename)
    if os.path.isfile(filename):
        user_conf = load_config(filename)
        settings.ellipsis_patterns += user_conf.get('ellipsis_patterns', [])
        settings.exclude_macros += user_conf.get('exclude_macros', [])
        settings.sensitive_context_match = user_conf.get(
            'sensitive_context_match', False)
        return settings
    return None

def parse_arguments():
    parser = argparse.ArgumentParser(
        prog='samewords',
        usage='%(prog)s [options] FILE',
        description='Annotate potentially ambiguous words in critical text '
                    'editions made with LaTeX and reledmac.')
    parser.add_argument('file', metavar='FILE', type=str, nargs=1,
                        help='Location of local file to be processed.')
    parser.add_argument(
        '--output', dest='location', action='store',
        help=("Location of the output. You can specify a filename as part of "
              "the address. If you don't do that, the name of the input file "
              "will be put in the directory specified. (default: '%("
              "default)s')")
    )
    parser.add_argument(
        '--config-file', dest='config', action='store',
        help=("Location of the configuration file. For information on what it "
             "may contain, see the README.")
        )
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s {}'.format(samewords.__version__),
                        help="Show version and exit.")
    return vars(parser.parse_args())

def main():
    # Read command line arguments
    args = parse_arguments()

    filename = args['file'][0]
    output = args['location']
    config = args['config']

    if config:
        parse_config_file(config)

    if not output:
        print(samewords.core.process_document(filename))
    else:
        if os.path.isdir(output):
            _, output_filename = os.path.split(filename)
            output_dir = output
        elif os.path.isfile(output):
            answer = input('The file {} already exists. Overwrite (y/n)?'
                           .format(output))
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
