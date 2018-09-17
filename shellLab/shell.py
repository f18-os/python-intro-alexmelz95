#! /usr/bin/env python3

import os, sys, re, signal, subprocess
exit = 0
# piping = False
# pipeCounter = 0
# pipeCommands = []
while(exit == 0):
    args = []
    sleep = False


    # if piping == True and pipeCounter == len(pipeCommands):
    #     piping = False
    #     pipeCounter = 0
    #     pipeCommands = []

    # if piping == False:
        command = ""
        while len(command) == 0:
            command = input("prompt>$ ")
            if command == "murder":
                sys.exit(0)
        if "|" in command:
            pipeCommands = command.split("|")
            piping = True
        else:
            args = command.split()
    #
    # if piping == True:
    #     if pipeCounter < len(pipeCommands):
    #         args = pipeCommands[pipeCounter].split()
    #         pipeCounter += 1

    pid = os.getpid()

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

    elif args[len(args)-1] == "&":
        sleep = True

    # os.write(1, ("About to fork (pid:%d)\n" % pid).encode())
    else:
        rc = os.fork()

        if rc < 0:
            # os.write(2, ("fork failed, returning %d\n" % rc).encode())
            sys.exit(1)
        elif rc == 0:                   # child
            # os.write(1, ("I am child.  My pid==%d.  Parent's pid=%d\n" % (os.getpid(), pid)).encode())
            args2 = []
            # for i in range(len(args)):
            #     if args[i] == "|":
            #         pipe = True

            outputFile = ""
            inputFile = ""
            for i in range(len(args)):
                if args[i] == ">":
                    outputFile = args[i+1]
                    os.close(1)                 # redirect child's stdout
                    sys.stdout = open(outputFile, "w")
                    fd = sys.stdout.fileno() # os.open("p4-output.txt", os.O_CREAT)
                    os.set_inheritable(fd, True)
                    # os.write(2, ("Child: opened fd=%d for writing\n" % fd).encode())
                    args2 = args[:i]
                if args[i] == "<":
                    inputFile = args[i+1]
                    os.close(0)
                    sys.stdin = open(inputFile, "r")
                    fd = sys.stdin.fileno()
                    os.set_inheritable(fd, True)
                    args2 = args[:i]

            # if piping == True and pipeCounter != len(pipeCommands):
            #     os.close(1)                 # redirect child's stdout
            #     sys.stdout = open("pipeOutput.txt", "w")
            #     fd = sys.stdout.fileno() # os.open("p4-output.txt", os.O_CREAT)
            #     os.set_inheritable(fd, True)


            if len(args2) == 0:
                args2 = args

            if piping == True and pipeCounter > 1:
                args2.append("pipeOutput.txt")


            for dir in re.split(":", os.environ['PATH']): # try each directory in the path
                program = "%s/%s" % (dir, args2[0])
                # os.write(1, ("Child:  ...trying to exec %s\n" % program).encode())
                try:
                    os.execve(program, args2, os.environ) # try to exec program
                except FileNotFoundError:             # ...expected
                    pass                              # ...fail quietly

            os.write(1, ("%s: command not found\n" % args2[0]).encode())
            sys.exit(1)
        elif rc == 2:
            sys.exit(0)
        else:                           # parent (forked ok)
            # os.write(1, ("I am parent.  My pid=%d.  Child's pid=%d\n" % (pid, rc)).encode())
            if not sleep:
                childPidCode = os.wait()
            # os.write(1, ("Parent: Child %d terminated with exit code %d\n" %
            #              childPidCode).encode())
