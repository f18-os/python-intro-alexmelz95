import sys        # command line arguments
import re         # regular expression tools
import os         # checking if file exists
import subprocess # executing program

regex = re.compile('[^a-zA-Z]')

if len(sys.argv) is not 3:
    print("Correct usage: wordCount.py <input text file> <output file>")
    exit()

inputFile = sys.argv[1];
outputFile = sys.argv[2];

if not os.path.exists(inputFile):
    print ("Text file input %s doesn't exist! Exiting" % inputFile)
    exit()

inputFile = open(inputFile, "r")
inputText = inputFile.read()
inputFile.close()

arrayInputText = regex.sub(" ", inputText).lower().split()
arrayInputText.sort()

outputText = {}
for word in arrayInputText:
    if word in outputText:
        outputText[word] += 1
    else:
        outputText[word] = 1

outputFile = open(outputFile, "w")

for key in outputText:
    outputFile.write(key + " " + str(outputText[key]) + "\n")

outputFile.close()
