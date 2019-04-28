#!/usr/bin/python
import os
import subprocess

if os.uid != 0:
    print "Please run as root"
    exit()
    
requirements =  ["paramiko", "termcolor", "argparse", "cryptography==2.4.2", "setuptools", "wheel"]
Failed = []
Installed = []

for module in requirements:
    try:
        subprocess.check_output(("pip", "install", module))
        print "[+]: Installed " + module
    except:
        print "[-]: Failed to install " + module
        Failed.append(module)

