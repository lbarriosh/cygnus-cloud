#!/usr/bin/python
# -*- coding: utf8 -*-
# Image repository build script
# Version: 2.0
#

from __future__ import print_function

import imp
import sys
import os
from subprocess import call

dependencies = ["MySQLdb", "twisted", "pyftpdlib", "mysql"]
binary = "Image repository"
version = "5.0.1"
entryPointPath = "imageRepository"
entryPointFileName = "main.py"
targetScript = "imageRepository.sh"
configurationFilePath = "../../ImageRepository_settings.conf"

def printLogo():
    print('\t   _____                             _____ _                 _ ')
    print('\t  / ____|                           / ____| |               | |')
    print('\t | |    _   _  __ _ _ __  _   _ ___| |    | | ___  _   _  __| |')
    print('\t | |   | | | |/ _` | \'_ \| | | / __| |    | |/ _ \| | | |/ _` |')
    print('\t | |___| |_| | (_| | | | | |_| \__ \ |____| | (_) | |_| | (_| |')
    print('\t  \_____\__, |\__, |_| |_|\__,_|___/\_____|_|\___/ \__,_|\__,_|')
    print('\t         __/ | __/ |                                           ')
    print('\t        |___/ |___/ ')
    print()
    
def printCopyrightNotice():
    print("Copyright (C) 2012-13 Luis Barrios Hernández, Adrián Fernández Hernández")
    print("\t and Samuel Guayerbas Martín\n")
    print("CygnusCloud is distributed under the terms of the Apache License, Version 2.")
    print("For further information, please read the LICENSE.txt file.")

if __name__ == "__main__" :
    print('*' * 80)
    printLogo()
    print(binary + " installer")
    print('Version ' + version)
    printCopyrightNotice()
    print('*' * 80)
    print()
    
    print("Checking Python interpreter version...")
    
    python_version = sys.version_info[0] + sys.version_info[1] * 0.1 + sys.version_info[2] * 0.01
    
    if (python_version >= 3.0 or python_version < 2.7) :
        print("Error: CygnusCloud requires a Python 2.7.x interpreter")
        print("\tYour interpreter's version: {0}.{1}.{2}".format(sys.version_info[0], sys.version_info[1], sys.version_info[2]))
        sys.exit()    
    print("\tDone!")
    
    print("Checking dependencies...")
    
    for module in dependencies :
        try :
            imp.find_module(module)
        except ImportError:
            print("Error: the required module '{0}' is not installed".format(module))
            sys.exit()    
    print("\tDone!")
    
    print("Generating script...")
    
    f = open(targetScript, "w")
    f.write("#!/bin/bash\n")
    f.write("\n")
    f.write("export PYTHONPATH=$(pwd)/bin\n")
    f.write("cd $(pwd)/bin/" + entryPointPath + "\n")
    f.write("python -OO " + entryPointFileName + " " + configurationFilePath + "\n")
    f.close()
    call("chmod +x " + targetScript, shell=True)
    print("\tDone!")
    
    print("The installation process is now complete.")
    print("To start the {0} daemon, please run the\n\t'{1}'\n\tscript file.".format(binary.lower(), os.path.abspath(targetScript))) 