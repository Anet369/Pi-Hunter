#!/usr/bin/python
import os
import subprocess

aptPackages = ["nmap", "python-pip"]

os.system("apt install -y " + " ".join(aptPackages))

requirements = open("requirements.txt", "r").read().split("\n")
for module in requirements:
    if module != "":
        os.system("pip install '" + module + "'")
