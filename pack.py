from os import path as OS_PATH

from linpgtoolbox.builder import Builder

# Get the current working directory
cwd: str = OS_PATH.dirname(OS_PATH.realpath(__file__))

# Compile and pack the project
Builder.compile(cwd)
Builder.pack(cwd)
