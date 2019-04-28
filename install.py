#!/usr/bin/python
import os
import subprocess

requirements =  ["paramiko", "termcolor"]
Failed = []
Installed = []

for module in requirements:
    try:
        subprocess.check_output(("pip", "install", module))
        print "[+]: Installed " + module
    except:
        print "[-]: Failed to install " + module
        Failed.append(module)

