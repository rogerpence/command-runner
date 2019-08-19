#!/usr/bin/env python

#   command-runner 
#   by Roger Pence
version = 'v 1.0.1'
#   August 18, 2019
 
# Copyright 2019 by Roger Pence. All rights reserved.

# Permission is hereby granted, free of charge, to any person obtaining a copy of 
# this software and associated documentation files (the "Software"), to deal in 
# the Software without restriction, including without limitation the rights to use, 
# copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the
# Software, and to permit persons to whom the Software is furnished to do so, 
# subject to the following conditions:

# * The above copyright notice and this permission notice shall be included in all
#   copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
# OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF 
# OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Installation:

# * Confirm that you have Python3 installed
# * Install these two PIP3 packages:
#    - pip3 install termcolor pyyaml
#    - pip3 install termcolor termcolor
# * Copy cr.py to your /usr/local/bin directory with 
#    - sudo cp cr.py /usr/local/bin/cr 
# * Make cr executable with:
#    - sudo chmod +x /usr/local/bin/cr
  
import subprocess  
import sys  
import yaml
import os
from termcolor import colored
from pathlib import Path

def exit_with_error(error_message):
    print(error_message)
    exit(1)        

def load_commands(file_name):
    if not os.path.isfile(file_name):
        exit_with_error(f"Error: {file_name} file not found.")
    else:        
        with open(file_name, 'r') as f:
            try:
                cmds = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                print(colored('An error occurred parsing the configuration file.', 'red'))
                print(colored('The following error should help to location where in the the file the error occurred.', 'red'))
                print(exc)                
                exit(1)
            return cmds

def all_args():
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

def add_cmdline_args(command_line):
    return replace_token(command_line, '{{args}}', all_args())

def get_actual_command(command):
    if 'alias' in cmds[command]:
        alias_command = cmds[command]['alias']
        if not alias_command in cmds: 
            print(colored(F'aliased command \'{alias_command}\' is not defined.', 'red'))
            exit(1)
        return alias_command
    else:        
        return command

def pad_command_with_trailing_blanks(key, max_key_len):
    command = key + (' ' * max_key_len)
    command = command[:max_key_len + 3]
    return command 

def show_help():
    print('-------------------')
    print('command-runner help')
    print('-------------------')
    print(F'{version}')
    print('by Roger Pence')
    print('-------------------')
    print('syntax:')
    print('    dev [--dry-run|--help] command [args]')
    print('    optional --dry-run flag shows the command that would be run')
    print('    optional --help flag (or no arguments) shows this help list')
    print('    commands are shown below in blue:')

    max_key_len = 0
    for key in cmds:
        if len(key) > max_key_len:
            max_key_len = len(key) 

    for key in cmds:
        command = pad_command_with_trailing_blanks(key, max_key_len)
        command = colored(colored(command, 'blue'))            
        if 'alias' in cmds[key]:            
            alias = cmds[key]['alias']
            text = colored(alias, 'blue')
            aliased_to = colored('is aliased to ', 'white')
            print(command + "\n  " +  aliased_to + text)
        else: 
            cmd = cmds[key]['cmd']
            msg = cmds[key]['msg']
            cmd = colored(cmd, 'yellow')
            print(command + "\n  " + cmd)

    print('')
    print('note: {{args}} in a command is replaced with all command line args')

def get_commands():
    home_path = str(Path.home())    

    if os.path.isfile('cmds.yaml'):
        local_cmds = load_commands('cmds.yaml')

    if os.path.isfile(f"{home_path}/global-commands.yaml"):
        global_cmds = load_commands(f"{home_path}/global-commands.yaml")

    if 'local_cmds' in locals() and 'global_cmds' in locals():
        cmds = {**global_cmds, **local_cmds}
        return cmds

    if 'local_cmds' in locals():
        cmds = local_cmds
        return cmds

    if 'global_cmds' in locals():
        cmds =  global_cmds            
        return cmds

    if not 'local_cmds' in locals() and not 'global_cmds' in locals():
        print(f"{home_path}/global-commands.yaml or ./cmds.yaml not found.")
        exit(1)
    
def main():       
    if command in cmds.keys():
        actual_command = get_actual_command(command)
        command_line = cmds[actual_command]['cmd']
        command_line = add_cmdline_args(command_line)

        message = cmds[actual_command]['msg']
        if len(message) != 0:
            print(message)
        if dry_run:
            print(colored('This is a dry run. This command would have been run:', 'red'))
            print(command_line)
            exit(0)
        else:
            launch_command(command_line)
            exit(0)

    if command.startswith('-'):
        msg = 'flag not found'            
    else:
        msg = 'command not found'                    
    print(colored(command, 'red') + ' ' + msg)            
    print('dev --help to show syntax and available commands')

if __name__ == '__main__':
    cmds = get_commands()

    dry_run = False

    if no_command_line_args_provided():
        show_help()
        exit(0)

    if sys.argv[1] == '--help':
        show_help()
        exit(0)
    
    args = pop_first_element(sys.argv) # Program name is first arg.

    if args[0] == '--dry-run':
        dry_run = True
        args = pop_first_element(args)        

    command = args[0]
    args = pop_first_element(args)

    main()        
