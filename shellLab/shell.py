#! /usr/bin/env python3

import os, sys, re

pid = os.getpid()

os.write(1, ("About to fork (pid:%d)\n" % pid).encode())

rc = os.fork()

if rc < 0:
    os.write(2, ("fork failed, returning %d\n" % rc).encode())
    sys.exit(1)
elif rc == 0:                   # child
    os.write(1, ("I am child.  My pid==%d.  Parent's pid=%d\n" % (os.getpid(), pid)).encode())
    args = []
    args2 = []
    while len(args) == 0:
        command = input("prompt> ")
        args = command.split()

    outputFile = ""
    inputFile = ""
    for i in range(len(args)):
        if args[i] == ">":
            outputFile = args[i+1]
            os.close(1)                 # redirect child's stdout
            sys.stdout = open(outputFile, "w+")
            fd = sys.stdout.fileno() # os.open("p4-output.txt", os.O_CREAT)
            os.set_inheritable(fd, True)
            os.write(2, ("Child: opened fd=%d for writing\n" % fd).encode())
            args2 = args[:i]
        if args[i] == "<":
            inputFile = args[i+1]
            try:
                inputFile = open(inputFile, "r")
            except FileNotFoundError:
                os.write(2, ("Child:    Could not exec %s\n" % args[0]).encode())
                sys.exit(1)
            inputText = inputFile.read()
            inputFile.close()
            arrayInputText = inputText.split()
            args2 = args[:i] + arrayInputText

    if len(args2) == 0:
        args2 = args

    for dir in re.split(":", os.environ['PATH']): # try each directory in the path
        program = "%s/%s" % (dir, args2[0])
        os.write(1, ("Child:  ...trying to exec %s\n" % program).encode())
        try:
            os.execve(program, args2, os.environ) # try to exec program
        except FileNotFoundError:             # ...expected
            pass                              # ...fail quietly

    os.write(2, ("Child:    Could not exec %s\n" % args[0]).encode())
    sys.exit(1)
else:                           # parent (forked ok)
    os.write(1, ("I am parent.  My pid=%d.  Child's pid=%d\n" % (pid, rc)).encode())
    childPidCode = os.wait()
    os.write(1, ("Parent: Child %d terminated with exit code %d\n" %
                 childPidCode).encode())
