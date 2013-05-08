# -*- coding: utf8 -*-
'''
Un balanceador de carga muy simple.
@author: Luis Barrios Hernández
@version: 1.0
'''

from loadBalancer import LoadBalancer

class PenaltyBasedLoadBalancer(LoadBalancer):
    '''
    Este balanceador de carga creará las nuevas máquinas virtuales en el servidor con menos
    carga de trabajo.
    '''
    
    def __init__(self, databaseConnector, vCPUsWeight, vCPUsExcessThreshold, ramWeight, storageSpaceWeight, temporarySpaceWeight):
        """
        Inicializa el estado del balanceador de carga
        Argumentos:
            databaseConnector: objeto que se usará para leer de la base de datos de estado.
        """
        LoadBalancer.__init__(self, databaseConnector)
        self.__vCPUsWeight = vCPUsWeight
        self.__vCPUsExcessThreshold = vCPUsExcessThreshold
        self.__ramWeight = ramWeight
        self.__storageSpaceWeight = storageSpaceWeight
        self.__temporarySpaceWeight = temporarySpaceWeight
    
    def assignVMServer(self, imageID, create_new_image=False):
        """
        Escoge el servidor de máquinas virtuales que albergará una máquina virtual.
        Argumentos:
            imageId: el identificador único de la imagen
        Returns:
            una tupla (servidor escogido, mensaje de error). Cuando mensaje de error es None,
            servidor escogido será el ID del servidor en el que se colocará la imagen..
        """
        
        # Paso 1: obtenemos el conjunto de servidores que podemos utilizar
        
        if (not create_new_image) :            
            
            availableServers = self._dbConnector.getHosts(imageID)
            if (len(availableServers) == 0) :
                return (0, 'The image is not available')
        else :
            availableServers = self._dbConnector.getReadyVanillaServers()
            if (len(availableServers) == 0) :
                return (0, 'There are no vanilla servers available')
        
        # Paso 2: obtener las características de la imagen
        vanillaFamilyID = self._dbConnector.getFamilyID(imageID)
        if (vanillaFamilyID == None) :
            if (create_new_image) :
                token = "source"
            else :
                token = ""
            return (0, "The {0} image does not exist".format(token))
        
        imageFeatures = self._dbConnector.getVanillaImageFamilyFeatures(vanillaFamilyID)
        
        
        # Paso 2: calcular la penalización de cada servidor
        
        serverPenalties = []
        
        for serverID in availableServers :            
            serverStatusData = self._dbConnector.getVMServerStatistics(serverID)
            normalizedVCPUPenalty = float(imageFeatures["vCPUs"] + serverStatusData["ActiveVCPUs"]) / serverStatusData["PhysicalCPUs"]
            normalizedRAMPenalty = float(imageFeatures["RAMSize"] + serverStatusData["RAMInUse"]) / serverStatusData["RAMSize"]
            normalizedStorageSpacePenalty = float(imageFeatures["osDiskSize"] + serverStatusData["AvailableStorageSpace"]
                                                      - serverStatusData["FreeStorageSpace"]) / serverStatusData["AvailableStorageSpace"]
            normalizedTemporarySpacePenalty = float(imageFeatures["dataDiskSize"] + serverStatusData["AvailableTemporarySpace"]
                                                      - serverStatusData["FreeTemporarySpace"]) / serverStatusData["AvailableTemporarySpace"]            
                    
            if (normalizedVCPUPenalty <= (1 + self.__vCPUsExcessThreshold) or normalizedRAMPenalty <= 1 
                    or normalizedStorageSpacePenalty <= 1 or normalizedTemporarySpacePenalty <= 1) :
                # La imagen cabe. Podemos considerar este servidor. Si no cabe, ignoramos este servidor
                serverPenalty = self.__vCPUsWeight * normalizedVCPUPenalty + self.__ramWeight * normalizedRAMPenalty + \
                    self.__storageSpaceWeight * normalizedStorageSpacePenalty + self.__temporarySpaceWeight * normalizedTemporarySpacePenalty                     
                serverPenalties.append((serverID, serverPenalty))    
            
        # Coger el menos penalizado
        
        serverPenalties.sort(key=lambda tupl : tupl[1])                   
        
        if (serverPenalties != []) :
            # Al menos un servidor puede albergar la imagen => indicamos cuál es
            return (serverPenalties[0][0], None)
        else :
            if (create_new_image) :
                token = "vanilla"
            else :
                token = ""
            return (0, 'All the {0} virtual machine servers are under full load. Please conctact the system administrators.'.format(token))