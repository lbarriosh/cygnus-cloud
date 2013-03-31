#!/usr/bin/python
#
# Virtual machine server build file
# Version: 1.0
#

from __future__ import print_function

import imp
import sys
from subprocess import call

dependencies = ["MySQLdb", "twisted"]
binary = "Web server endpoint"
version = "1.0+"
entryPointPath = "clusterServer/connector"
entryPointFileName = "webServerEndpoint.py"
targetScript = "webServerEndpoint.sh"

if __name__ == "__main__" :
    
    print(binary + " " + version + " installer ")
    
    print("Checking Python interpreter version...")
    
    python_version = sys.version_info[0] + sys.version_info[1] * 0.1 + sys.version_info[2] * 0.01
    
    if (python_version >= 3.0 or python_version < 2.7) :
        print("Error: CygnusCloud requires a Python 2.7.x interpreter")
        print("\tYour version: {0}.{1}.{2}".format(sys.version_info[0], sys.version_info[1], sys.version_info[2]))
        sys.exit()    
    
    print("Checking dependencies...")
    
    for module in dependencies :
        try :
            imp.find_module(module)
        except ImportError:
            print("Error: the required module '{0}' is not installed".format(module))
            sys.exit()    
    
    print("Generating script...")
    
    f = open(targetScript, "w")
    f.write("#!/bin/bash\n")
    f.write("\n")
    f.write("export PYTHONPATH=$(pwd)/bin\n")
    f.write("cd $(pwd)/bin/" + entryPointPath + "\n")
    f.write("python " + entryPointFileName + "\n")
    f.close()
    call("chmod +x " + targetScript, shell=True)
    
    print("The installation is complete")