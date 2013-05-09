# -*- coding: utf8 -*-
'''
Un balanceador de carga muy simple.
@author: Luis Barrios Hernández
@version: 1.0
'''

from loadBalancer import LoadBalancer, MODE_T

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
        
    def assignVMServer(self, imageID, mode):
        """
        Escoge el servidor de máquinas virtuales que albergará una máquina virtual.
        Argumentos:
            imageId: el identificador único de la imagen
        Returns:
            una tupla (servidor escogido, mensaje de error). Cuando mensaje de error es None,
            servidor escogido será el ID del servidor en el que se colocará la imagen.
        """
        
        # Paso 1: obtenemos el conjunto de servidores que podemos utilizar
        
        if (mode == MODE_T.BOOT_DOMAIN) :
            availableServers = self._dbConnector.getHosts(imageID)
            errorMessage = 'The image is not available'
            token = ""
        elif (mode == MODE_T.CREATE_OR_EDIT_IMAGE):
            availableServers = self._dbConnector.getVanillaVMServers()
            errorMessage = 'There are no vanilla servers available'
            token = "source"
        else:
            availableServers = self._dbConnector.getCandidateVMServers(imageID)
            errorMessage = 'There are no servers available'
            
        if (len(availableServers) == 0) :
            return (0, errorMessage)
            
        # Paso 2: obtenemos las características de la imagen
        
        vanillaFamilyID = self._dbConnector.getFamilyID(imageID)
        if (vanillaFamilyID == None) :
            return (0, "The {0} image does not exist".format(token))            
        
        imageFeatures = self._dbConnector.getVanillaImageFamilyFeatures(vanillaFamilyID)       
        
        # Paso 3: calcular la penalización de cada servidor. Si además estamos en modo
        # despliegue, calculamos el número de copias que cada servidor puede albergar.
        
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
                if (mode != MODE_T.DEPLOY_IMAGE) :                
                    serverPenalties.append((serverID, serverPenalty))    
                else :
                    copies_with_cpus = serverStatusData["PhysicalCPUs"] / imageFeatures["vCPUs"]
                    copies_with_RAM = serverStatusData["RAMSize"] / imageFeatures["RAMSize"]
                    copies_with_temporaryDiskSpace = serverStatusData["AvailableTemporarySpace"] / imageFeatures["dataDiskSize"]
                    values = [copies_with_cpus, copies_with_RAM, copies_with_temporaryDiskSpace]
                    serverPenalties.append((serverID, serverPenalty, min(values)))    
                
        if (serverPenalties == []) :
            if (mode == MODE_T.CREATE_OR_EDIT_IMAGE) :
                token = "vanilla"
            else :
                token = ""
            return (0, 'All the {0} virtual machine servers are under full load. Please conctact the system administrators.'.format(token))
        
        # Ordenar los servidores por su penalización
        
        serverPenalties.sort(key=lambda tupl : tupl[1])    
        
        # En modo despliegue, devolvemos una lista de servidores y un número de copias. En el resto de modos,
        # devolvemos sólo el primer servidor (el menos penalizado)               
        
        if (mode != MODE_T.DEPLOY_IMAGE) :
            # Al menos un servidor puede albergar la imagen => indicamos cuál es
            return (serverPenalties[0][0], None)
        else :
            copies = 0
            servers = []
            for tup in serverPenalties :
                servers.append((tup[0], tup[2]))
                copies += tup[2]
            return (servers, None, copies)