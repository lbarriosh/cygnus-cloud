# -*- coding: utf8 -*-
'''
A very simple load balancer
@author: Luis Barrios Hernández
@version: 1.0
'''

from loadBalancer import LoadBalancer

class SimpleLoadBalancer(LoadBalancer):
    '''
    These load balancers will deploy an image in the virtual machine
    server with less running VMs.
    '''
    
    def __init__(self, databaseConnector):
        LoadBalancer.__init__(self, databaseConnector)
    
    def assignVMServer(self, imageId):
        # Determine what virtual machine servers can host this image
        availableServers = self._dbConnector.getImageServers(imageId)
        if (len(availableServers) == 0) :
            return (0, 'The image is not available')
        # Choose the "less crowded" one.
        chosenServer = availableServers[0]
        chosenServerHosts = self._dbConnector.getVMServerStatistics(chosenServer)["ActiveHosts"]
        i = 1
        while (i != len(availableServers)) : 
            server = availableServers[i]
            hosts = self._dbConnector.getVMServerStatistics(server)["ActiveHosts"]
            if (hosts < chosenServerHosts) :
                chosenServer = server
                chosenServerHosts = hosts
        # Everything went OK
        return (chosenServer, None)
