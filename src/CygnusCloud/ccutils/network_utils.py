'''
Created on Feb 19, 2013

@author: luis
'''
from network.exceptions.networkManager import NetworkManagerException

def sendPacket(networkManager, IPAddress, port, packet):
    try :
        if (networkManager.isConnectionReady(IPAddress, port)) :
            networkManager.sendPacket(IPAddress, port, packet)
            return True
        else :
            return False
    except NetworkManagerException as e:
        print str(e)
        return False
