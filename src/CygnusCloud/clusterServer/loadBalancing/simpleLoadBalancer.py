# -*- coding: utf8 -*-
'''
Un balanceador de carga muy simple.
@author: Luis Barrios Hernández
@version: 1.0
'''

from loadBalancer import LoadBalancer

class SimpleLoadBalancer(LoadBalancer):
    '''
    Este balanceador de carga creará las nuevas máquinas virtuales en el servidor con menos
    carga de trabajo.
    '''
    
    def __init__(self, databaseConnector):
        """
        Inicializa el estado del balanceador de carga
        Argumentos:
            databaseConnector: objeto que se usará para leer de la base de datos de estado.
        """
        LoadBalancer.__init__(self, databaseConnector)
    
    def assignVMServer(self, imageId):
        """
        Escoge el servidor de máquinas virtuales que albergará una máquina virtual.
        Argumentos:
            imageId: el identificador único de la imagen
        Returns:
            una tupla (servidor escogido, mensaje de error). Cuando mensaje de error es None,
            servidor escogido será el ID del servidor en el que se colocará la imagen..
        """
        
        # Buscar servidores candidatos. Si hay más de uno, la imagen se colocará en el que menos
        # máquinas virtuales activas tenga.
        
        availableServers = self._dbConnector.getImageServers(imageId)
        if (len(availableServers) == 0) :
            return (0, 'The image is not available')
        
        
        chosenServer = availableServers[0]
        chosenServerHosts = self._dbConnector.getVMServerStatistics(chosenServer)["ActiveHosts"]
        i = 1
        while (i != len(availableServers)) : 
            server = availableServers[i]
            hosts = self._dbConnector.getVMServerStatistics(server)["ActiveHosts"]
            if (hosts < chosenServerHosts) :
                chosenServer = server
                chosenServerHosts = hosts
                
        
        return (chosenServer, None)
