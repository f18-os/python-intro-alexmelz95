#! /usr/bin/env python3

import os, sys, re, signal, subprocess

exit = 0
piping = False
path = ""
pipeCommands = []

while(exit == 0):
    args = []
    sleep = False

    if piping == False:
        command = ""
        prompt = ""
        if 'PS1' in os.environ:
            prompt = os.environ['PS1']
        else:
            prompt = "prompt>$ "
        while len(command) == 0:
            command = input(prompt)
            if command == "murder":
                sys.exit(0)
            if "|" in command:
                piping = True
                pipeCommands = command.split()
            else:
                args = command.split()
            sysin_reset = os.dup(sys.stdin.fileno())
            sysout_reset = os.dup(sys.stdout.fileno())

    if piping == True:
        i = 0
        while i != len(pipeCommands) and pipeCommands[i] != "|":
            args.append(pipeCommands[i])
            i+=1
        pipeCommands = pipeCommands[i+1:]

    if args[0] == "cd":
        dir = ""
        newdir = ""
        dir = os.getcwd()
        dir = dir.split("/")
        if(args[1] == ".."):
            for i in range(len(dir)-1):
                newdir += dir[i]
                if i != len(dir)-2:
                    newdir += "/"
        else:
            newdir = args[1]
        os.chdir(newdir)

    else:
        if args[0][0] == "/":
            path = args[0]

        if args[len(args)-1] == "&":
            sleep = True
            args = args[:len(args)-1]

        if piping == True:
            pin, pout = os.pipe()
            for f in (pin, pout):
                os.set_inheritable(f, True)

        rc = os.fork()

        if rc < 0:
            sys.exit(1)
        elif rc == 0:
            if piping == True and len(pipeCommands) > 0:
                #Check Collaboration Report #1
                os.dup2(pout, sys.stdout.fileno())
                os.close(pin)
                os.close(pout)

            args2 = []

            outputFile = ""
            inputFile = ""
            i = 0
            while i < len(args):
                if args[i] == ">":
                    outputFile = args[i+1]
                    os.close(1)
                    sys.stdout = open(outputFile, "w")
                    fd = sys.stdout.fileno()
                    os.set_inheritable(fd, True)
                    args2 = args[:i]
                if args[i] == "<":
                    inputFile = args[i+1]
                    os.close(0)
                    sys.stdin = open(inputFile, "r")
                    fd = sys.stdin.fileno()
                    os.set_inheritable(fd, True)
                    args2 = args[:i]
                    args = args[:i] + args[i+2:]
                    i = 0
                i += 1

            if len(args2) == 0:
                args2 = args

            if len(path) != 0:
                program = path
                try:
                    os.execve(program, args2, os.environ)
                except FileNotFoundError:
                    pass
            else:
                for dir in re.split(":", os.environ['PATH']):
                    program = "%s/%s" % (dir, args2[0])
                    try:
                        os.execve(program, args2, os.environ)
                    except FileNotFoundError:
                        pass
            sys.exit(1)
        else:
            if not sleep:
                childPidCode = os.wait()

            if piping == True and len(pipeCommands) > 0:
                #Check Collaboration Report #2
                os.dup2(pin, sys.stdin.fileno())
                os.close(pout)
                os.close(pin)

            if piping == True and not pipeCommands:
                piping = False
                pipeCommands = []
                os.dup2(sysin_reset, sys.stdin.fileno())
                os.dup2(sysout_reset, sys.stdout.fileno())
