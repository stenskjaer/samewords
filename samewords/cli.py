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
  --config-file <file>     JSON-formatted file with application configuration variables. For
                           recognized keys and formatting of values, see the documentation on
                           https://github.com/stenskjaer/samewords. [default: ~/.samewords.json]
  -v, --version            Show version and exit.
  -h, --help               Show this help message and exit.
"""

import json

import samewords
import docopt
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
        settings.include_macros += user_conf.get('include_macros', [])
        settings.exclude_macros += user_conf.get('exclude_macros', [])
        return settings
    return None


def main():
    args = docopt.docopt(__doc__, version=samewords.__version__)
    filename = args['<file>']
    output = args['--output']
    parse_config_file(args['--config-file'])

    if not output:
        print(samewords.core.process_document(filename))
    else:
        if os.path.isdir(output):
            _, output_filename = os.path.split(filename)
            output_dir = output
        elif os.path.isfile(output):
            answer = input(
                'The file {} already exists. Overwrite (y/n)? '.format(output))
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
