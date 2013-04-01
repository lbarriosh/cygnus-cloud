# -*- coding: utf8 -*-
'''
Definiciones del reactor del servidor de cluster
@author: Luis Barrios Hernández
@version: 4.0
'''

from clusterServer.networking.callbacks import VMServerCallback, WebCallback
from database.utils.configuration import DBConfigurator
from database.clusterServer.clusterServerDB import ClusterServerDatabaseConnector, SERVER_STATE_T
from network.manager.networkManager import NetworkManager
from clusterServer.networking.packets import ClusterServerPacketHandler, MAIN_SERVER_PACKET_T as WEB_PACKET_T
from virtualMachineServer.packets import VMServerPacketHandler, VM_SERVER_PACKET_T as VMSRVR_PACKET_T
from time import sleep
from clusterServer.loadBalancing.simpleLoadBalancer import SimpleLoadBalancer
from network.twistedInteraction.clientConnection import RECONNECTION_T

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
    def __init__(self, timeout):
        """
        Inicializa el estado del reactor
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        """
        self.__webCallback = WebCallback(self)
        self.__finished = False
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
        self.__dbConnector.connect()
        self.__dbConnector.resetVMServersStatus()
        
    def startListenning(self, certificatePath, port):
        """
        Hace que el reactor comience a escuchar las peticiones del endpoint.
        Argumentos:
            certificatePath: ruta de los ficheros server.crt y server.key
            port: el puerto en el que se escuchará
        Devuelve:
            Nada
        """
        self.__loadBalancer = SimpleLoadBalancer(self.__dbConnector)
        self.__networkManager = NetworkManager(certificatePath)
        self.__webPort = port
        self.__networkManager.startNetworkService()        
        self.__webPacketHandler = ClusterServerPacketHandler(self.__networkManager)
        self.__vmServerPacketHandler = VMServerPacketHandler(self.__networkManager)
        self.__networkManager.listenIn(port, self.__webCallback, True)
        self.__vmServerCallback = VMServerCallback(self)
        
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
            self.__halt(data)
        elif (data["packet_type"] == WEB_PACKET_T.QUERY_VM_DISTRIBUTION) :
            self.__sendVMDistributionData()
        elif (data["packet_type"] == WEB_PACKET_T.QUERY_ACTIVE_VM_DATA) :
            self.__requestVNCConnectionData()
        elif (data["packet_type"] == WEB_PACKET_T.DOMAIN_DESTRUCTION) :
            self.__destroyDomain(data)
            
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
            self.__networkManager.sendPacket(cd["ServerIP"], cd["ServerPort"], p)
            
    def __halt(self, data):
        """
        Apaga TODAS las máquinas del cluster, incluyendo los servidores de máquinas virtuales.
        Argumentos:
            data: diccionario con los datos del paquete
        Devuelve:
            Nada
        """    
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
                                                    data["VMServerPort"])
            
            self.__sendStatusRequestPackets(data["VMServerIP"], data["VMServerPort"])
            
            
            # Indicar al endpoint de la web que el comando se ha ejecutado con éxito
            p = self.__webPacketHandler.createExecutedCommandPacket(data["CommandID"])
        except Exception as e:                
            p = self.__webPacketHandler.createVMServerRegistrationErrorPacket(data["VMServerIP"], 
                                                                            data["VMServerPort"], 
                                                                            data["VMServerName"], str(e), data["CommandID"])        
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
        self.__networkManager.sendPacket(vmServerIP, vmServerPort, p)
        p = self.__vmServerPacketHandler.createVMServerDataRequestPacket(VMSRVR_PACKET_T.QUERY_ACTIVE_DOMAIN_UIDS)            
        self.__networkManager.sendPacket(vmServerIP, vmServerPort, p)
            
    def __unregisterOrShutdownVMServer(self, data):
        """
        Procesa un paquete de apagado o borrado de un servidor de máquinas virtuales
        Argumentos:
            data: diccionario con los datos del paquete
        Devuelve:
            nada
        """
        key = data["ServerNameOrIPAddress"] 
        halt = data["Halt"]
        unregister = data["Unregister"]
        if data.has_key("CommandID") :
            useCommandID = True 
            commandID = data["CommandID"]
        else :
            useCommandID = False
        # Empezamos apagando el servidor si está arrancado
        serverId = self.__dbConnector.getVMServerID(key)
        if (serverId != None) :
            # Las máquinas virtuales activas que alberga ese servidor se destruirán => las borramos
            self.__dbConnector.deleteHostedVMs(serverId)
            serverData = self.__dbConnector.getVMServerBasicData(serverId)
            
            status = serverData["ServerStatus"]
            if (status == SERVER_STATE_T.READY or status == SERVER_STATE_T.BOOTING) :
                if not halt :
                    p = self.__vmServerPacketHandler.createVMServerShutdownPacket()
                else :
                    p = self.__vmServerPacketHandler.createVMServerHaltPacket()
                self.__networkManager.sendPacket(serverData["ServerIP"], serverData["ServerPort"], p)
                # Cerrar la conexión 
                self.__networkManager.closeConnection(serverData["ServerIP"], serverData["ServerPort"])            
            if (not unregister) :
                self.__dbConnector.updateVMServerStatus(serverId, SERVER_STATE_T.SHUT_DOWN)
                self.__dbConnector.deleteVMServerStatistics(serverId)
            else :
                # Actualizar el estado del servidor de máquinas virtuales
                self.__dbConnector.deleteVMServer(key)
            if (useCommandID) :
                # Hay que enviar una respuesta al servidor de máquinas virtuales
                p = self.__webPacketHandler.createExecutedCommandPacket(commandID)
                self.__networkManager.sendPacket('', self.__webPort, p)
        else :
            # Error
            if (unregister) :
                packet_type = WEB_PACKET_T.VM_SERVER_UNREGISTRATION_ERROR
            else :
                packet_type = WEB_PACKET_T.VM_SERVER_SHUTDOWN_ERROR
            errorMessage = "The virtual machine server with name or IP address <<{0}>> is not registered".format(key)
            p = self.__webPacketHandler.createVMServerGenericErrorPacket(packet_type, key, errorMessage, commandID)
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
        self.__dbConnector.setVMServerStatistics(serverID, data["ActiveDomains"])
        
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
                                                                         serverNameOrIPAddress, str(e), data["CommandID"])
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
            # Guardar la ubicación de la nueva máquina virtual. 
            # Importante: todas las máquinas virtuales se identifican de forma única con el ID
            # del comando que las crea
            self.__dbConnector.registerActiveVMLocation(data["CommandID"], serverID)
            # Enviar la petición de arranque al servidor de máquinas virtuales
            p = self.__vmServerPacketHandler.createVMBootPacket(vmID, userID, data["CommandID"])
            serverData = self.__dbConnector.getVMServerBasicData(serverID)
            self.__networkManager.sendPacket(serverData["ServerIP"], serverData["ServerPort"], p)    
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
        
        # Averiguar los datos del servidor y pedirle que se la cargue
        connectionData = self.__dbConnector.getVMServerBasicData(serverID)
        packet = self.__vmServerPacketHandler.createVMShutdownPacket(data["DomainID"])
        self.__networkManager.sendPacket(connectionData["ServerIP"], connectionData["ServerPort"], packet)
        
        # Indicar al endpoint que todo fue bien
        packet = self.__webPacketHandler.createExecutedCommandPacket(data["CommandID"])
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
            self.__sendActiveVMsVNCConnectionData(packet)
        elif (data["packet_type"] == VMSRVR_PACKET_T.ACTIVE_DOMAIN_UIDS) :
            self.__processActiveDomainUIDs(data)
            
    def processServerReconnectionData(self, ipAddress, reconnection_status) :
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
            
    def __sendActiveVMsVNCConnectionData(self, packet):
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