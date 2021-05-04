#this is for reading python files only as a test
#command line argument is read and the resulting matches are printed as an array
#should list all imports to the python program file provided as argument
import sys
import re

f = open(sys.argv[1], 'r')
matches = re.findall("import\s*(\w*)", f.read())
print(matches)
f.close()
