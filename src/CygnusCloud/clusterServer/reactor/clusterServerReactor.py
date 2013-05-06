# -*- coding: utf8 -*-
'''
Definiciones del reactor del servidor de cluster
@author: Luis Barrios Hernández
@version: 4.0
'''

from clusterServer.networking.callbacks import VMServerCallback, WebCallback, ImageRepositoryCallback
from clusterServer.threads.clusterStatusMonitoringThread import ClusterStatusMonitoringThread
from database.utils.configuration import DBConfigurator
from database.clusterServer.clusterServerDB import ClusterServerDatabaseConnector, SERVER_STATE_T
from network.manager.networkManager import NetworkManager
from clusterServer.networking.packets import ClusterServerPacketHandler, MAIN_SERVER_PACKET_T as WEB_PACKET_T
from virtualMachineServer.networking.packets import VMServerPacketHandler, VM_SERVER_PACKET_T as VMSRVR_PACKET_T
from time import sleep
from clusterServer.loadBalancing.simpleLoadBalancer import SimpleLoadBalancer
from network.twistedInteraction.clientConnection import RECONNECTION_T
from clusterServer.loadBalancing.penaltyBasedLoadBalancer import PenaltyBasedLoadBalancer
from imageRepository.packets import ImageRepositoryPacketHandler, PACKET_T as REPOSITORY_PACKET_T

class WebPacketReactor(object):
    '''
    Estos objetos procesarán los paquetes recibidos desde el endpoint de la web
    '''
    def processWebIncomingPacket(self, packet):
        raise NotImplementedError
    
class VMServerPacketReactor(object):
    '''
    Estos objetos procesarán los paquetes recibidos desde un servidor de máquinas virtuales
    '''
    def processVMServerIncomingPacket(self, packet):
        raise NotImplementedError

class ClusterServerReactor(WebPacketReactor, VMServerPacketReactor):
    '''
    Estos objetos reaccionan a los paquetes recibidos desde los servidores de máquinas
    virtuales y desde el endpoint de la web.
    '''
    def __init__(self, loadBalancerSettings, timeout):
        """
        Inicializa el estado del reactor
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        """        
        self.__finished = False
        self.__loadBalancerSettings = loadBalancerSettings
        self.__timeout = timeout
        
    def connectToDatabase(self, mysqlRootsPassword, dbName, dbUser, dbPassword, scriptPath):
        """
        Establece la conexión con la base de datos del servidor de cluster.
        Argumentos:
            mysqlRootsPassword: La contraseña de root de MySQL
            dbName: nombre de la base de datos del servidor de cluster
            dbUser: usuario a utilizar
            dbPassword: contraseña del usuario a utilizar
            scriptPath: ruta del script de inicialización de la base de datos
        Devuelve:
            Nada
        """
        configurator = DBConfigurator(mysqlRootsPassword)
        configurator.runSQLScript(dbName, scriptPath)
        configurator.addUser(dbUser, dbPassword, dbName, True)
        self.__dbConnector = ClusterServerDatabaseConnector(dbUser, dbPassword, dbName)
        self.__dbConnector.resetVMServersStatus()
        
    def startListenning(self, certificatePath, listenningPort, repositoryIP, repositoryPort, vmServerStatusUpdateInterval):
        """
        Hace que el reactor comience a escuchar las peticiones del endpoint.
        Argumentos:
            certificatePath: ruta de los ficheros server.crt y server.key
            listenningPort: el puerto en el que se escuchará
        Devuelve:
            Nada
        """
        if (self.__loadBalancerSettings[0] == "penalty-based") :
            self.__loadBalancer = PenaltyBasedLoadBalancer(self.__dbConnector, self.__loadBalancerSettings[1], 
                self.__loadBalancerSettings[2], self.__loadBalancerSettings[3], self.__loadBalancerSettings[4], 
                self.__loadBalancerSettings[5])
        else :
            self.__loadBalancer = SimpleLoadBalancer(self.__dbConnector)
        self.__networkManager = NetworkManager(certificatePath)
        self.__webPort = listenningPort
        self.__repositoryIP = repositoryIP
        self.__repositoryPort = repositoryPort
        self.__dbConnector.addImageRepository(repositoryIP, repositoryPort, SERVER_STATE_T.READY)
        self.__networkManager.startNetworkService()        
        self.__imageRepositoryPacketHandler = ImageRepositoryPacketHandler(self.__networkManager)
        self.__webPacketHandler = ClusterServerPacketHandler(self.__networkManager)
        self.__vmServerPacketHandler = VMServerPacketHandler(self.__networkManager)
        self.__webCallback = WebCallback(self)
        self.__vmServerCallback = VMServerCallback(self)
        self.__imageRepositoryCallback = ImageRepositoryCallback(self)
        try :
            self.__networkManager.connectTo(repositoryIP, repositoryPort, 10, self.__imageRepositoryCallback, True, True)
        except Exception as e:
            print "Can't connect to the image repository: " + e.message
            self.__finished = True
            return
            
        self.__networkManager.listenIn(listenningPort, self.__webCallback, True)        
        self.__vmServerStatusUpdateThread = ClusterStatusMonitoringThread(self, vmServerStatusUpdateInterval)
        self.__vmServerStatusUpdateThread.run()
        
    def processWebIncomingPacket(self, packet):
        """
        Procesa un paquete enviado desd el endpoint de la web
        Argumentos:
            packet: el paquete que hay que procesar
        Devuelve:
            Nada
        """
        data = self.__webPacketHandler.readPacket(packet)
        if (data["packet_type"] == WEB_PACKET_T.REGISTER_VM_SERVER) :
            self.__registerVMServer(data)
        elif (data["packet_type"] == WEB_PACKET_T.QUERY_VM_SERVERS_STATUS) :
            self.__sendVMServerStatusData()
        elif (data["packet_type"] == WEB_PACKET_T.UNREGISTER_OR_SHUTDOWN_VM_SERVER) :
            self.__unregisterOrShutdownVMServer(data)
        elif (data["packet_type"] == WEB_PACKET_T.BOOTUP_VM_SERVER) :
            self.__bootUpVMServer(data)
        elif (data["packet_type"] == WEB_PACKET_T.VM_BOOT_REQUEST):
            self.__bootUpVM(data)
        elif (data["packet_type"] == WEB_PACKET_T.HALT) :
            self.__doImmediateShutdown(data)
        elif (data["packet_type"] == WEB_PACKET_T.QUERY_VM_DISTRIBUTION) :
            self.__sendVMDistributionData()
        elif (data["packet_type"] == WEB_PACKET_T.QUERY_ACTIVE_VM_DATA) :
            self.__requestVNCConnectionData()
        elif (data["packet_type"] == WEB_PACKET_T.DOMAIN_DESTRUCTION) :
            self.__destroyDomain(data)
        elif (data["packet_type"] == WEB_PACKET_T.VM_SERVER_CONFIGURATION_CHANGE):
            self.__changeVMServerConfiguration(data)
        elif (data["packet_type"] == WEB_PACKET_T.REPOSITORY_STATUS_REQUEST):
            self.__sendRepositoryStatusData()
        elif (data["packet_type"] == WEB_PACKET_T.DEPLOY_IMAGE):
            self.__deployImage(data)
            
    def __deployImage(self, data):
        serverNameOrIPAddress = data["ServerNameOrIPAddress"]
        
        # Comprobar si el servidor existe
        
        serverID = self.__dbConnector.getVMServerID(serverNameOrIPAddress)
        if (serverID == None) :
            p = self.__webPacketHandler.createVMServerGenericErrorPacket(WEB_PACKET_T.IMAGE_DEPLOYMENT_ERROR, serverNameOrIPAddress, 
                                                                         "The virtual machine server is not registered", data["CommandID"])
            self.__networkManager.sendPacket('', self.__webPort, p)
            return
        
        # Comprobar si el servidor está arrancado
        serverData = self.__dbConnector.getVMServerBasicData(serverID)
        if (serverData["ServerStatus"] != SERVER_STATE_T.READY):
            p = self.__webPacketHandler.createVMServerGenericErrorPacket(WEB_PACKET_T.IMAGE_DEPLOYMENT_ERROR, serverNameOrIPAddress, 
                                                                         "The virtual machine server is ready", data["CommandID"])
            self.__networkManager.sendPacket('', self.__webPort, p)
            return
        
        # Comprobar que el servidor no tiene ya la imagen
        if self.__dbConnector.hostsImage(serverID, data["ImageID"]) :
            p = self.__webPacketHandler.createVMServerGenericErrorPacket(WEB_PACKET_T.IMAGE_DEPLOYMENT_ERROR, serverNameOrIPAddress, 
                                                                         "The image {0} is already hosted on this server".format(data["ImageID"]), 
                                                                         data["CommandID"])
            self.__networkManager.sendPacket('', self.__webPort, p)
            return
            
        # Todo es correcto => enviar la petición
        p = self.__vmServerPacketHandler.createImageDeploymentPacket(self.__repositoryIP, self.__repositoryPort, data["ImageID"], data["CommandID"])
        self.__networkManager.sendPacket(serverData["ServerIP"], serverData["ServerPort"], p)
            
    def __sendRepositoryStatusData(self):
        repositoryStatus = self.__dbConnector.getImageRepositoryStatus(self.__repositoryIP, self.__repositoryPort)
        p = self.__webPacketHandler.createRepositoryStatusPacket(repositoryStatus["FreeDiskSpace"], 
                                                                 repositoryStatus["AvailableDiskSpace"], 
                                                                 repositoryStatus["ConnectionStatus"])
        self.__networkManager.sendPacket('', self.__webPort, p)
            
    def __requestVNCConnectionData(self):
        """
        Solicita los datos de conexión VNC a todos los servidores de máquinas virtuales.
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        """
        p = self.__vmServerPacketHandler.createVMServerDataRequestPacket(VMSRVR_PACKET_T.QUERY_ACTIVE_VM_DATA)
        
        connectionData = self.__dbConnector.getActiveVMServersConnectionData()
        for cd in connectionData :            
            errorMessage = self.__networkManager.sendPacket(cd["ServerIP"], cd["ServerPort"], p)
            NetworkManager.printConnectionWarningIfNecessary(cd["ServerIP"], cd["ServerPort"], "VNC connection data request", errorMessage)
            
    def __doImmediateShutdown(self, data):
        """
        Apaga TODAS las máquinas del cluster, incluyendo los servidores de máquinas virtuales.
        Argumentos:
            data: diccionario con los datos del paquete
        Devuelve:
            Nada
        """    
        # Apagamos el repositorio
        p = self.__imageRepositoryPacketHandler.createHaltPacket()
        self.__networkManager.sendPacket(self.__repositoryIP, self.__repositoryPort, p)
        self.__networkManager.closeConnection(self.__repositoryIP, self.__repositoryPort)
        # Apagamos los servidores de máquinas virtuales
        self.__vmServerStatusUpdateThread.stop()
        vmServersConnectionData = self.__dbConnector.getActiveVMServersConnectionData()
        if (vmServersConnectionData != None) :
            args = dict()
            args["Halt"] = data["HaltVMServers"]
            args["Unregister"] = False            
            for connectionData in vmServersConnectionData :
                args["ServerNameOrIPAddress"] = connectionData["ServerIP"]
                self.__unregisterOrShutdownVMServer(args)  
        self.__finished = True   
             
    def __registerVMServer(self, data):
        """
        Procesa un paquete de registro de un servidor de máquinas virtuales
        Argumentos:
            data: diccionario con los datos del paquete recibido
        Devuelve:
            Nada
        """
        try :
            # Comprobar si la IP y el nombre del servidor ya están en uso
            server_id = self.__dbConnector.getVMServerID(data["VMServerIP"])
            if (server_id != None) :
                raise Exception("The IP address " + data["VMServerIP"] + " is assigned to another VM server")
          
            server_id = self.__dbConnector.getVMServerID(data["VMServerName"])
            if (server_id != None) :
                raise Exception("The name " + data["VMServerName"] + " is assigned to another VM server")
            
            # Establecer la conexión
            self.__networkManager.connectTo(data["VMServerIP"], data["VMServerPort"], 
                                                20, self.__vmServerCallback, True, True)
            while not self.__networkManager.isConnectionReady(data["VMServerIP"], data["VMServerPort"]) :
                sleep(0.1)
                
            # Registrar el nuevo servidor y pedirle su estado
            self.__dbConnector.registerVMServer(data["VMServerName"], data["VMServerIP"], 
                                                    data["VMServerPort"], data["IsVanillaServer"])
            
            self.__sendStatusRequestPackets(data["VMServerIP"], data["VMServerPort"])
            
            
            # Indicar al endpoint de la web que el comando se ha ejecutado con éxito
            p = self.__webPacketHandler.createExecutedCommandPacket(data["CommandID"])
        except Exception as e:                
            p = self.__webPacketHandler.createVMServerRegistrationErrorPacket(data["VMServerIP"], 
                                                                            data["VMServerPort"], 
                                                                            data["VMServerName"], e.message, data["CommandID"])        
        self.__networkManager.sendPacket('', self.__webPort, p)
        
    def __sendStatusRequestPackets(self, vmServerIP, vmServerPort):
        """
        Envía los paquetes de solicitud de estado a un servidor de máquinas virtuales
        Argumentos:
            vmServerIP : la IP del servidor de máquinas virtuales
            vmServerPort: el puerto del servidor de máquinas virtuales
        Devuelve:
            Nada
        """
        p = self.__vmServerPacketHandler.createVMServerDataRequestPacket(VMSRVR_PACKET_T.SERVER_STATUS_REQUEST)
        errorMessage = self.__networkManager.sendPacket(vmServerIP, vmServerPort, p)
        NetworkManager.printConnectionWarningIfNecessary(vmServerIP, vmServerPort, "status request", errorMessage)
        p = self.__vmServerPacketHandler.createVMServerDataRequestPacket(VMSRVR_PACKET_T.QUERY_ACTIVE_DOMAIN_UIDS)            
        errorMessage = self.__networkManager.sendPacket(vmServerIP, vmServerPort, p)
        NetworkManager.printConnectionWarningIfNecessary(vmServerIP, vmServerPort, "active domain UIDs request", errorMessage)
        
    def sendStatusRequestPacketsToClusterMachines(self):
        for serverID in self.__dbConnector.getVMServerIDs() :
            serverData = self.__dbConnector.getVMServerBasicData(serverID)
            if (serverData["ServerStatus"] == SERVER_STATE_T.READY) :
                self.__sendStatusRequestPackets(serverData["ServerIP"], serverData["ServerPort"])
        p = self.__imageRepositoryPacketHandler.createStatusRequestPacket()
        self.__networkManager.sendPacket(self.__repositoryIP, self.__repositoryPort, p)            
            
    def __unregisterOrShutdownVMServer(self, data):
        """
        Procesa un paquete de apagado o borrado de un servidor de máquinas virtuales
        Argumentos:
            data: diccionario con los datos del paquete
        Devuelve:
            nada
        """
        key = data["ServerNameOrIPAddress"] 
        haltServer = data["Halt"]
        unregister = data["Unregister"]
        
        if data.has_key("CommandID") :
            useCommandID = True 
            commandID = data["CommandID"]
        else :
            useCommandID = False
            commandID = ""
            
        # Paso 1: averiguar si existe el servidor
        serverID = self.__dbConnector.getVMServerID(key)
        if (serverID == None) :
            errorMessage = "The virtual machine server with name or IP address <<{0}>> is not registered".format(key)
            if (unregister) :
                packet_type = WEB_PACKET_T.VM_SERVER_UNREGISTRATION_ERROR
            else :
                packet_type = WEB_PACKET_T.VM_SERVER_SHUTDOWN_ERROR
            p = self.__webPacketHandler.createVMServerGenericErrorPacket(packet_type, key, errorMessage, commandID)
            self.__networkManager.sendPacket('', self.__webPort, p)  
            return
        
        # Paso 2: sabemos que el servidor existe. Si está arrancado, lo paramos 
        serverData = self.__dbConnector.getVMServerBasicData(serverID)            
        status = serverData["ServerStatus"]    
        if (status == SERVER_STATE_T.READY or status == SERVER_STATE_T.BOOTING) :  
            try :
                connectionReady = self.__networkManager.isConnectionReady(serverData["ServerIP"], serverData["ServerPort"])
            except Exception as e :
                connectionReady = False
                errorMessage = e.message                    
            if (not connectionReady) :   
                if (unregister) :
                    packet_type = WEB_PACKET_T.VM_SERVER_UNREGISTRATION_ERROR
                else :
                    packet_type = WEB_PACKET_T.VM_SERVER_SHUTDOWN_ERROR
                p = self.__webPacketHandler.createVMServerGenericErrorPacket(packet_type, key, errorMessage, commandID)
                self.__networkManager.sendPacket('', self.__webPort, p)  
                return
            
            # La conexión está lista => enviamos el paquete de apagado
            self.__dbConnector.deleteHostedVMs(serverID)
            if not haltServer :
                p = self.__vmServerPacketHandler.createVMServerShutdownPacket()
            else :
                p = self.__vmServerPacketHandler.createVMServerHaltPacket()
                self.__networkManager.sendPacket(serverData["ServerIP"], serverData["ServerPort"], p)
                     
            # Cerramos la conexión 
            self.__networkManager.closeConnection(serverData["ServerIP"], serverData["ServerPort"])       
            
        # Paso 3: borramos el servidor de la base de datos (sólo si es necesario)      
        if (unregister) :
            self.__dbConnector.deleteVMServer(key)
            
        # Paso 4: respondemos a la web (sólo si es necesario)      
        if (useCommandID) :
            p = self.__webPacketHandler.createExecutedCommandPacket(commandID)
            self.__networkManager.sendPacket('', self.__webPort, p)  
            
    def __updateVMServerStatus(self, data):
        """
        Procesa un paquete de estado enviado desde un servidor de máquinas virtuales
        Argumentos:
            data: diccionario con los datos del paquete recibido
        Devuelve:
            Nada
        """
        # Identificar el servidor de máquinas virtuales y actualizar su estado en la base de datos.
        
        serverID = None
        while (serverID == None) :
            serverID = self.__dbConnector.getVMServerID(data["VMServerIP"])
            if (serverID == None) :
                sleep(0.1)
                
        self.__dbConnector.updateVMServerStatus(serverID, SERVER_STATE_T.READY)
        self.__dbConnector.setVMServerStatistics(serverID, data["ActiveDomains"], data["RAMInUse"], data["RAMSize"], 
                                                 data["FreeStorageSpace"], data["AvailableStorageSpace"], data["FreeTemporarySpace"],
                                                 data["AvailableTemporarySpace"], data["ActiveVCPUs"], data["PhysicalCPUs"])
        
    def __bootUpVMServer(self, data):
        """
        Procesa un paquete de arranque de un servidor de máquinas virtuales
        Argumentos:
            data: diccionario con los datos del paquete recibido
        Devuelve:
            Nada
        """
        try :
            
            # Comprobar si el servidor está registrado
            
            serverNameOrIPAddress = data["ServerNameOrIPAddress"]
            serverId = self.__dbConnector.getVMServerID(serverNameOrIPAddress)
            if (serverId == None) :
                raise Exception("The virtual machine server is not registered")
            serverData = self.__dbConnector.getVMServerBasicData(serverId)
            
            if (serverData["ServerStatus"] != SERVER_STATE_T.SHUT_DOWN and 
                serverData["ServerStatus"] != SERVER_STATE_T.CONNECTION_TIMED_OUT) :
                # El servidor ya está arrancado => ignoramos la petición
                return
            
            # Establecer la conexión
            
            self.__networkManager.connectTo(serverData["ServerIP"], serverData["ServerPort"], 
                                                20, self.__vmServerCallback, True, True)
            while not self.__networkManager.isConnectionReady(serverData["ServerIP"], serverData["ServerPort"]) :
                sleep(0.1)
                
            # Solicitar el estado al servidor de máquinas virtuales
            
            self.__dbConnector.updateVMServerStatus(serverId, SERVER_STATE_T.BOOTING)
            
            self.__sendStatusRequestPackets(serverData["ServerIP"], serverData["ServerPort"])
            
            # Indicar al endpoint que el comando se ha ejecutado con éxito
            p = self.__webPacketHandler.createExecutedCommandPacket(data["CommandID"])
        except Exception as e:
            p = self.__webPacketHandler.createVMServerGenericErrorPacket(WEB_PACKET_T.VM_SERVER_BOOTUP_ERROR, 
                                                                         serverNameOrIPAddress, e.message, data["CommandID"])
        self.__networkManager.sendPacket('', self.__webPort, p)
            
    def __sendVMServerStatusData(self):
        """
        Envía el estado de los servidores de máquinas virtuales al endpoint de la web.
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        """
        self.__sendStatusData(self.__dbConnector.getVMServerBasicData, self.__webPacketHandler.createVMServerStatusPacket)
        
    def __sendVMDistributionData(self):
        """
        Envía la distribución de las imágenes al endpoint de la web
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        """    
        self.__sendStatusData(self.__dbConnector.getHostedImages, self.__webPacketHandler.createVMDistributionPacket)
        
    def __sendStatusData(self, queryMethod, packetCreationMethod):
        """
        Envía información de estado al endpoint de la web
        Argumentos:
            queryMethod: el método que extraerá la información de estado de la base de datos
            packetCreationMethod: el método que creará los paquetes de estado
        Devuelve:
            Nada
        """        
        # La información de las tablas se fragmenta en varios segmentos para no superar
        # el tamaño máximo del paquete (64 KB)
        
        segmentSize = 200 # Cada segmento llevará 200 filas de la tabla
        outgoingData = []
        serverIDs = self.__dbConnector.getVMServerIDs()
        if (len(serverIDs) == 0) :
            # No hay datos => responder con segmento vacío
            segmentCounter = 0
            segmentNumber = 0
            sendLastSegment = True
        else :
            # Hay datos => calcular el número de segmentos que necesitamos
            segmentCounter = 1        
            segmentNumber = (len(serverIDs) / segmentSize)
            if (len(serverIDs) % segmentSize != 0) :
                segmentNumber += 1
                sendLastSegment = True
            else :
                # Si la división no es exacta, hay que enviar un último segmento con lo que quede
                sendLastSegment = False  
                
        # Crear los segmentos y enviarlos cuando estén llenos
        for serverID in serverIDs :
            row = queryMethod(serverID)
            if (isinstance(row, dict)) :
                outgoingData.append(row)
            else :
                outgoingData += row
                
            if (len(outgoingData) >= segmentSize) :
                packet = packetCreationMethod(segmentCounter, segmentNumber, outgoingData)
                self.__networkManager.sendPacket('', self.__webPort, packet)
                outgoingData = []
                segmentCounter += 1
                
        # Enviar un segmento con los datos que quedan (sólo si hace falta)
        if (sendLastSegment) :
            packet = packetCreationMethod(segmentCounter, segmentNumber, outgoingData)
            self.__networkManager.sendPacket('', self.__webPort, packet)             
                   
    def __bootUpVM(self, data):
        """
        Procesa un paquete de arranque de máquina virtual
        Argumentos:
            data: diccionario con los datos del paquete
        Devuelve:
            Nada
        """
        vmID = data["VMID"]
        userID = data["UserID"]
        
        # Escoger el servidor de máquinas virtuales que alojará la máquina
        (serverID, errorMessage) = self.__loadBalancer.assignVMServer(vmID)
        if (errorMessage != None) :
            # Error => avisar al usuario
            p = self.__webPacketHandler.createVMBootFailurePacket(vmID, errorMessage, data["CommandID"])
            self.__networkManager.sendPacket('', self.__webPort, p)
        else :           
            # Enviar la petición de arranque al servidor de máquinas virtuales
            p = self.__vmServerPacketHandler.createVMBootPacket(vmID, userID, data["CommandID"])
            serverData = self.__dbConnector.getVMServerBasicData(serverID)
            errorMessage = self.__networkManager.sendPacket(serverData["ServerIP"], serverData["ServerPort"], p)    
            if (errorMessage != None) :
                p = self.__webPacketHandler.createVMBootFailurePacket(vmID, "The virtual machine server connection was lost", data["CommandID"])
                self.__networkManager.sendPacket('', self.__webPort, p)
                return              
            # Guardar la ubicación de la nueva máquina virtual. 
            # Importante: todas las máquinas virtuales se identifican de forma única con el ID
            # del comando que las crea
            self.__dbConnector.registerActiveVMLocation(data["CommandID"], serverID)
            # Registrar el comando de arranque para controlar el tiempo de respuesta
            self.__dbConnector.registerVMBootCommand(data["CommandID"], data["VMID"])
            
    def __destroyDomain(self, data):
        """
        Destruye una máquina virtual activa
        Argumentos:
            data: diccionario con los datos del paquete correspondiente
        Devuelve:
            Nada
        """
        # Comprobar si la máquina existe
        serverID = self.__dbConnector.getActiveVMHostID(data["DomainID"])
        if (serverID == None) :
            # Error
            packet = self.__webPacketHandler.createDomainDestructionErrorPacket("The domain does not exist", data["CommandID"])
            self.__networkManager.sendPacket('', self.__webPort, packet)
            return       
        
        # Averiguar los datos del servidor y pedirle que se la cargue
        connectionData = self.__dbConnector.getVMServerBasicData(serverID)
        packet = self.__vmServerPacketHandler.createVMShutdownPacket(data["DomainID"])
        errorMessage = self.__networkManager.sendPacket(connectionData["ServerIP"], connectionData["ServerPort"], packet)
        if (errorMessage != None) :
            packet = self.__webPacketHandler.createDomainDestructionErrorPacket("The connection was lost", data["CommandID"])
            self.__networkManager.sendPacket('', self.__webPort, packet)
        else :
            # Borrar la máquina virtual de la base de datos           
            self.__dbConnector.deleteActiveVMLocation(data["CommandID"])         
            # Indicar al endpoint que todo fue bien
            packet = self.__webPacketHandler.createExecutedCommandPacket(data["CommandID"])
            self.__networkManager.sendPacket('', self.__webPort, packet)
        
    def __changeVMServerConfiguration(self, data):
        serverID = self.__dbConnector.getVMServerID(data["ServerNameOrIPAddress"])
        
        if (serverID == None) :
            packet = self.__webPacketHandler.createVMServerConfigurationChangeErrorPacket(
                "The virtual machine server with name or IP address <<{0}>> is not registered".format(data["ServerNameOrIPAddress"]), data["CommandID"])
            self.__networkManager.sendPacket('', self.__webPort, packet)
            return
        
        status = self.__dbConnector.getVMServerBasicData(serverID)["ServerStatus"]
        
        if (status == SERVER_STATE_T.BOOTING or status == SERVER_STATE_T.READY) :
            packet = self.__webPacketHandler.createVMServerConfigurationChangeErrorPacket(
                "The virtual machine server with name or IP address <<{0}>> is active. You must shut it down before proceeding."
                    .format(data["ServerNameOrIPAddress"]), data["CommandID"])
            self.__networkManager.sendPacket('', self.__webPort, packet)
            return
            
        try :
            self.__dbConnector.setServerBasicData(serverID, data["NewVMServerName"], SERVER_STATE_T.SHUT_DOWN, 
                                                  data["NewVMServerIPAddress"], data["NewVMServerPort"], data["NewVanillaImageEditionBehavior"])
            packet = self.__webPacketHandler.createExecutedCommandPacket(data["CommandID"])
        
        except Exception :
            packet = self.__webPacketHandler.createVMServerConfigurationChangeErrorPacket(
                "The new virtual machine server name (<<{0}>>) or IP address and port (<<{1}:{2}>> are already in use."\
                .format(data["NewVMServerName"], data["NewVMServerIPAddress"], data["NewVMServerPort"]), data["CommandID"])
            
        self.__networkManager.sendPacket('', self.__webPort, packet)    
    
    def processVMServerIncomingPacket(self, packet):
        """
        Procesa un paquete enviado desde un servidor de máquinas virtuales
        Argumentos:
            packet: el paquete a procesar
        Devuelve:
            Nada
        """
        data = self.__vmServerPacketHandler.readPacket(packet)
        if (data["packet_type"] == VMSRVR_PACKET_T.SERVER_STATUS) :
            self.__updateVMServerStatus(data)
        elif (data["packet_type"] == VMSRVR_PACKET_T.DOMAIN_CONNECTION_DATA) :
            self.__sendVMConnectionData(data)
        elif (data["packet_type"] == VMSRVR_PACKET_T.ACTIVE_VM_DATA) :
            self.__sendDomainsVNCConnectionData(packet)
        elif (data["packet_type"] == VMSRVR_PACKET_T.ACTIVE_DOMAIN_UIDS) :
            self.__processActiveDomainUIDs(data)
        elif (data["packet_type"] == VMSRVR_PACKET_T.IMAGE_DEPLOYMENT_ERROR):
            self.__processImageDeploymentError(data)
        elif (data["packet_type"] == VMSRVR_PACKET_T.IMAGE_DEPLOYED):
            self.__processImageDeployment(data)
            
    def __processImageDeploymentError(self, data):
        p = self.__webPacketHandler.createVMServerGenericErrorPacket(WEB_PACKET_T.IMAGE_DEPLOYMENT_ERROR, 
                                                                     data["SenderIP"], data["ErrorMessage"], data["CommandID"])
        self.__networkManager.sendPacket('', self.__webPort, p)
        
    def __processImageDeployment(self, data):
        serverID = self.__dbConnector.getVMServerID(data["SenderIP"])
        self.__dbConnector.assignImageToServer(serverID, data["ImageID"])
        p = self.__webPacketHandler.createExecutedCommandPacket(data["CommandID"])
        self.__networkManager.sendPacket('', self.__webPort, p)
            
    def processVMServerReconnectionData(self, ipAddress, reconnection_status) :
        """
        Procesa una reconexión con un servidor de máquinas virtuales
        Argumentos:
            ipAddress: la dirección IP del servidor de máquinas virtuales
            port: el puerto en el que el servidor de máquinas virtuales está escuchando
            reconnection_status: el estado del proceso de reconexión
        Devuelve:
            Nada
        """
        if (reconnection_status == RECONNECTION_T.RECONNECTING) : 
            status = SERVER_STATE_T.RECONNECTING
        elif (reconnection_status == RECONNECTION_T.REESTABLISHED) :
            status = SERVER_STATE_T.READY
        else :
            status = SERVER_STATE_T.CONNECTION_TIMED_OUT
        
        serverID = self.__dbConnector.getVMServerID(ipAddress)
        self.__dbConnector.updateVMServerStatus(serverID, status)
        
    def processImageRepositoryReconnectionData(self, reconnection_status):
        if (reconnection_status == RECONNECTION_T.RECONNECTING) : 
            status = SERVER_STATE_T.RECONNECTING
        elif (reconnection_status == RECONNECTION_T.REESTABLISHED) :
            status = SERVER_STATE_T.READY
        else :
            status = SERVER_STATE_T.CONNECTION_TIMED_OUT
        self.__dbConnector.updateImageRepositoryConnectionStatus(self.__repositoryIP, self.__repositoryPort, status)
            
    def __sendDomainsVNCConnectionData(self, packet):
        """
        Envía al endpoint los datos de conexión VNC de todas las máquinas
        virtuales activas del servidor de máquinas virtuales
        Argumentos:
            packet: diccionario con los datos a procesar
        Devuelve:
            Nada
        """
        p = self.__webPacketHandler.createActiveVMsDataPacket(packet)
        self.__networkManager.sendPacket('', self.__webPort, p)
            
    def __sendVMConnectionData(self, data):
        """
        Envía al endpoint los datos de conexión VNC a UNA máquina
        virtual que se acaba de crear.
        Argumetnos:
            data: diccionario con los datos del paquete
        Devuelve:
            Nada
        """
        # El comando ya se ha ejecutado. No tenemos que seguir controlando el tiempo que tarda.
        self.__dbConnector.removeVMBootCommand(data["CommandID"])
        
        p = self.__webPacketHandler.createVMConnectionDataPacket(data["VNCServerIP"], 
                                                                 data["VNCServerPort"], data["VNCServerPassword"], data["CommandID"])
        self.__networkManager.sendPacket('', self.__webPort, p)        
        
    def processImageRepositoryIncomingPacket(self, packet):
        data = self.__imageRepositoryPacketHandler.readPacket(packet)
        if data['packet_type'] == REPOSITORY_PACKET_T.STATUS_DATA:
            self.__dbConnector.updateImageRepositoryStatus(self.__repositoryIP, self.__repositoryPort, data["FreeDiskSpace"], data["TotalDiskSpace"])
        # TODO: procesar errores de borrado
        
    def __processActiveDomainUIDs(self, data):
        vmServerID = self.__dbConnector.getVMServerID(data["VMServerIP"])
        self.__dbConnector.registerHostedVMs(vmServerID, data["Domain_UIDs"])
    
    def monitorVMBootCommands(self):
        """
        Elimina los comandos de arranque de máquinas virtuales que tardan demasiado tiempo en procesarse.
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        """
        errorMessage = "Could not boot up virtual machine (timeout error)"
        while not self.__finished :
            data = self.__dbConnector.getOldVMBootCommandID(self.__timeout)
            if (not self.__finished and data == None) :
                # Dormimos para no enviar demasiadas conexiones por segundo a MySQL
                sleep(1) 
            else :
                # Borramos la máquina activa (sabemos que no existe)
                self.__dbConnector.deleteActiveVMLocation(data[0])
                # Creamos el paquete de error y se lo enviamos al endpoint de la web
                p = self.__webPacketHandler.createVMBootFailurePacket(data[1], errorMessage, data[0])
                self.__networkManager.sendPacket('', self.__webPort, p)
    
    def hasFinished(self):
        """
        Indica al hilo principal si puede terminar o no.
        Argumentos:
            Ninguno
        Devuelve:
            True si se puede terminar, y false en caso contrario.
        """
        return self.__finished
    
    def closeNetworkConnections(self):
        """
        Cierra todas las conexiones de red del servidor de máquinas virtuales.
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        @attention: este método JAMÁS debe llamarse desde un hilo de red. 
        Si lo hacéis, la aplicación se colgará.
        """
        self.__networkManager.stopNetworkService()    