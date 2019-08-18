## command-runner

---

Run frequently-repeated and verbose command lines quickly. 

command-runner is a Python script that provides a short-cut mechanism for running verbose command lines quickly. For example, docker-compose does a great job of orchestrating Docker but its use often imposes long, verbose command lines. Consider this command line to launch docker-compose:

    docker-compose -f docker-compose.yml -f docker-compose-remote-debug.yml up -d

I need to do this a lot! command-runner reduces it to:

    cr up-remote


## Inspiration     

The inspiration for command-runner was Chris Fidao's (@fideloper on Twitter) [free workflow video](https://serversforhackers.com/c/div-dev-workflow-intro). While using Chris's (highly recommended) Docker videos to learn Docker, I also learned about how he uses a Bash script to organize his Docker workflow. Copying his Bash script skeleton, I also used Bash scripts to manage my docker workflows.

Over time, through, I brewed myself a righteous mess with these special-case Bash files all over the place. command-runner is an attempt to to organize complex command-line driven workflows into consistent and easy-to-use command lines--but to also have these streamlined work flows customizable on a per-project basis.  

> command-runner was written to run on Ubuntu. I think it would work on the Mac and Windows, but it hasn't been tested there.     


## How command-runner works

command-runner commands are defined in YAML files. For example, the `up-remote` command (which launches a Docker project configured for remote debug) is defined in YAML like this: 

    up-remote:
        cmd: docker-compose -f docker-compose.yml -f docker-compose-remote-debug.yml up -d
        msg: Starting with remote debug

Each command definition has a `cmd` key that defines the command and a `msg` key that shows a short message when the command runs.        

Enter the `cmd` as you would enter it on the command line. Use the macro `{{args}}` to collect command line arguments and present them in the command at runtime. For example, given this command definition:

    myls: 
        cmd: ls {{args}}
        msg: Silly exmaple to show args. 
        
this command line:

    cr myls -l -t -r
    
results in this command line:

    ls -l -t -r    
    
command-runner also lets you create alias commands. For example, create an alias for the `up-remote` command with a single `alias` key as shown below:

    upr: 
        alias: up-remote 

> Do not start command names with __ (double underscore). That pattern is reserved for special-case commands that may later be implemented. 
        
## command-runner command definition YAML files        

command-runner recogizes two YAML command definition files: 

* A global command definition file in 
    
        ~/global-commands.yaml
    
* A local command definition file in the current working directory named
    
        cmds.yaml    

    Any commands present in this local that are also present in the global file will overwrite those from the global file (a future version of command-runner will show what commands got overwritten). `cmds.yaml` is intended to be project-specific. I frequently copy the included `laravel-docker.yaml` file (as `cmds.yaml`) into a Laravel project. Once there, I can tweak its settings so that they are specific to that project. 
    
At least one of these files must be present for command-runner to run. There are a couple of sample YAML files included in this project. When I'm using command-runner with Docker-based projects, I usually put the `cmd.yaml` file in the same folder as the projects's Docker files.     

## command-runner's command line

The command line syntax is:

    dev [--dry-run|--help] command [args]

where `command` is a command defined in one of the two command definition files. `[args]` is any number of command line arguments to be passed using the {{{args}} macro. 

* the optional `--dry-run` flag shows the command line that would be run

* optional `--help` flag (or no arguments) shows a little help panel and command list.
    
## Beware using command lines with redirection

A command line with redirection like this doesn't work with Python's subprocess.call:

    sed 's/:/\n/g' <<< "$PATH"

I've looked at replacing subprocess.call with subprocess.run (which may alleviate this) but subprocess.run needs an array with the command and its arguments as separate elements. For the command lines I need to automate (usually related to Docker or Node.js), fixing this issue is a low priority.
        
## Installation

command-runner is a single Python 3 script file with two PIP3 dependencies:

* pip3 install pyYaml
* pip3 install termcolor

> Depending on your Python install you may not need to include the '3' in `pip3`.

To install command-runner:

1. Confirm that you have Python3 installed
1. Install these two PIP3 packages:
   - pip3 install termcolor pyyaml
   - pip3 install termcolor termcolor
1. Copy cr.py to your /usr/local/bin directory with 
   - sudo cp cr.py /usr/local/bin/cr 
1. Make cr executable with:
   - sudo chmod +x /usr/local/bin/cr

I use command-runner mostly on my host machine. But because it's a simple, single Python script it also easy to install into your VM's or Docker images. 

# Todo

* Show warnings when loading a subsquent command definition file overwrites previous command definitions. 

* Add an 'include file' syntax to the command-define file to allow the import of other special-case command definitions. 

## Licensing (MIT license)

Copyright 2019 by Roger Pence. All rights reserved.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

* The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.