#!/usr/bin/env python3

import sys
import subprocess
from pathlib import Path
from termcolor import colored, cprint
import os
import yaml
import re
from pprint import pprint

# command-runner
# by Roger Pence
version = 'v 1.0.9'
date = 'August 24, 2019'

"""
Copyright 2019 by Roger Pence. All rights reserved.

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the
Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

* The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS," WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF
OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Installation:

* Confirm that you have Python 3 installed
* Install these Pip 3  packages:
   - pip3 install termcolor
   - pip3 install pyyaml
   - pip3 install colorama (Windows only)
* Copy cr.py to your /usr/local/bin directory with
   - sudo cp cr.py /usr/local/bin/cr
* Make cr executable with:
   - sudo chmod +x /usr/local/bin/cr

Your file names for Python 3 and pip3 may not include the '3'. Check first.
command-runner requires Python 3.
"""


def exit_with_error(error_message):
    print(error_message)
    exit(1)


def confirm_command_definitions(cmds, file_name):
    for cmd in cmds:
        if 'alias' in cmds[cmd]:
            continue
        if 'cmd' not in cmds[cmd]:
            cprint(
                f'\'cmd\' key not in \'{cmd}\' in {file_name} YAML file', 'red')
            exit(1)

        if 'msg' not in cmds[cmd]:
            cprint(
                f'\'msg\' key not in \'{cmd}\' in {file_name} YAML file', 'red')
            exit(1)


def load_commands(file_name):
    if not os.path.isfile(file_name):
        exit_with_error(f'Error: {file_name} file not found.')
    else:
        with open(file_name, 'r') as f:
            try:
                cmds = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                cprint('An error occurred parsing the configuration file.',
                       'red')
                cprint('The following error should help to locate where in \
the file the error occurred.', 'red')
                print(exc)
                exit(1)

        confirm_command_definitions(cmds, file_name)

        # Add filename key to commands.
        for cmd in cmds:
            cmds[cmd]['filename'] = 'global' if 'global' in file_name else 'local'

        return cmds


def all_args(args):
    return ' '.join(args)


def no_command_line_args_provided():
    return len(sys.argv) == 1


def launch_command(command):
    # Watch for commands with embedded redirection.
    # Something like this doesn't work with Python's subprocess.call.
    # sed 's/:/\n/g' <<< "$PATH"

    subprocess.call(command, shell=True)

    # I've looked at replacing subprocess.call with subprocess.run
    # but run needs an array with the command and its arguments.
    # For the essentially command lines I need to automate (usually
    # related to Docker and docker-compose), this is a low priority.


def pop_first_element(arr):
    arr.pop(0)
    return arr


def replace_token(command_line, token, value):
    return command_line.replace(token, value)


def add_cmdline_args(command_line, args):
    command_line = replace_token(command_line, '{{args}}', all_args(args))

    for i in range(0, len(args)):
        if re.search(r'{{\d}}', command_line):
            token = '{0}{1}{2}'.format('{{', i, '}}')
            command_line = replace_token(command_line, token, args[i])

    command_line = re.sub(r'{{\d}}', '', command_line)

    return command_line


def get_actual_command(command):
    if 'alias' in cmds[command]:
        alias_command = cmds[command]['alias']
        if not alias_command in cmds:
            cprint(
                f'aliased command \'{alias_command}\' is not defined.', 'red')
            exit(1)
        return alias_command
    else:
        return command


def show_help(cmds, verbose=True):
    if verbose:
        print('-------------------')
        print('command-runner help')
        print('-------------------')
        print('by Roger Pence')
        print(f'{version}')
        print(f'{date}')
        print('https://github.com/rogerpence/command-runner')
        print('-------------------')
        print('Run command:')
        print('    cr command [args]')
        print('Test a command:')
        print('    cr --dry-run | -d command [args]')
        print('Show all commands:')
        print('    cr --help | -h (or just \'cr\')')
        print('To search commands for text:')
        print('    cr --search | -s search-text')
        print('')
        print('Global commands are prefixed with an asterisk.')

    max_key_len = 0
    for key in cmds:
        if len(key) > max_key_len:
            max_key_len = len(key)

    global_command_count = 0
    local_command_count = 0

    for key in cmds:
        if cmds[key]['filename'] == 'global':
            command = '*' + key
            global_command_count += 1
        else:
            command = key
            local_command_count += 1

        command = colored(command, 'blue')

        if 'alias' in cmds[key]:
            alias = cmds[key]['alias']
            text = colored(alias, 'blue')
            aliased_to = colored('is aliased to ', 'white')
            print(command + "\n  " + aliased_to + text)
        else:
            cmd = cmds[key]['cmd']
            cmd = colored(cmd, 'yellow')
            print(command + "\n  " + cmd)

    if verbose:
        print(f'Global commands: {global_command_count} \
Local commands: {local_command_count}')


def get_commands():
    home_path = str(Path.home())

    local_cmds = load_commands('cmds.yaml') if \
        os.path.isfile('cmds.yaml') else {}

    global_fname = os.path.join(home_path, 'global-commands.yaml')
    global_cmds = load_commands(global_fname) if \
        os.path.isfile(global_fname) else {}

    cmds = {**global_cmds, **local_cmds}

    if (len(cmds) > 0):
        return cmds
    else:
        cprint(f"'{global_fname}' and/or local 'cmds.yaml' not found.", 'red')
        exit(1)


def main(command, args):
    if command in cmds.keys():
        actual_command = get_actual_command(command)
        command_line = cmds[actual_command]['cmd']
        command_line_with_args = add_cmdline_args(command_line, args)

        message = cmds[actual_command]['msg']
        if len(message) != 0:
            print(message)
        if dry_run:
            cprint('\nThis is a dry run. \
This command would have been run:', 'red')
            print(f'Command in YAML file..: {command_line}')
            print(f'Procssed command......: {command_line_with_args}')
            exit(0)
        else:
            launch_command(command_line_with_args)
            exit(0)

    if command.startswith('-'):
        msg = 'flag not found'
    else:
        msg = 'command not found'
    print(colored(command, 'red') + ' ' + msg)
    print('dev --help to show syntax and available commands')


def search_commands(cmds):
    if len(sys.argv) == 1:
        cprint('Search argument is missing.', 'red')
        cprint('Use this command line to search:', 'red')
        cprint('    cr -s <search-value>', 'red')
        exit(1)

    scoped_commands = {}
    scope = sys.argv[1]

    for cmd in cmds:
        if 'alias' in cmds[cmd]:
            continue
        # Search in command name and command.
        if scope in cmd + cmds[cmd]['cmd']:
            scoped_commands[cmd] = cmds[cmd]

    if len(scoped_commands) == 0:
        cprint(f'No commands were found containing \'{scope}\'', 'red')
        exit(0)

    cprint(f'Commands found containing \'{scope}\':', 'blue')

    show_help(scoped_commands, verbose=False)


if __name__ == '__main__':
    # --------------------------------------------
    # Windows-only code.
    # --------------------------------------------
    # termcolor needs colorama to work on Windows.
    # Be sure to get the colorama module with:
    # pip3 install colorama
    # See the GitHub README for notes on
    # IGNORE_COLORAMA environment variable.

    if os.name == 'nt' and 'IGNORE_COLORAMA' not in os.environ:
        import importlib
        import colorama
        colorama.init()

    cmds = get_commands()

    dry_run = False

    if no_command_line_args_provided():
        show_help(cmds)
        exit(0)

    if sys.argv[1] == '--help' or sys.argv[1] == '-h':
        show_help(cmds)
        exit(0)

    args = pop_first_element(sys.argv)  # Program name is first arg.

    if args[0] == '--dry-run' or args[0] == '-d':
        dry_run = True
        args = pop_first_element(args)

    if args[0] == '--search' or args[0] == '-s':
        search_commands(cmds)
        exit()

    command = args[0]
    args = pop_first_element(args)

    main(command, args)
