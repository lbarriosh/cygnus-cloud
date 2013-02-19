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
            print "The connection is not ready -> drop packet"
            return False
    except NetworkManagerException as e:
        print "The connection is not ready -> drop packet"
        print str(e)
        return False
