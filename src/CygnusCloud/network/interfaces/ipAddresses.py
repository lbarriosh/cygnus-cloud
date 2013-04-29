# -*- coding: utf8 -*-
'''
Interface IP address finder
@author: Paul Cannon (ActiveState code recipes)
'''

from ccutils.processes.childProcessManager import ChildProcessManager

def get_ip_address(ifname):
    try :
        output = ChildProcessManager.runCommandInForeground("/sbin/ifconfig " + ifname, Exception)
        if not ("inet addr" in output) :
            raise Exception
        targetLine = output.splitlines()[1]
        ip_address = targetLine.split(" ")[11]
        return ip_address.replace("addr:", "")
        
    except Exception:
        raise Exception("The network interface " + ifname + " is not ready")

if __name__ == "__main__" :
    print get_ip_address('eth0')