# -*- coding: utf8 -*-
'''
Created on 14/01/2013

@author: saguma
'''

from network.manager.networkManager import NetworkManager
from virtualMachineServer.networking.callback import ClusterServerCallback
from network.interfaces.ipAddresses import get_ip_address 
from virtualMachineServer.libvirtInteraction.libvirtConnector import LibvirtConnector
from virtualMachineServer.networking.packets import VM_SERVER_PACKET_T, VMServerPacketHandler
from virtualMachineServer.libvirtInteraction.xmlEditor import ConfigurationFileEditor
from database.vmServer.vmServerDB import VMServerDBConnector
from virtualMachineServer.virtualNetwork.virtualNetworkManager import VirtualNetworkManager
from ccutils.processes.childProcessManager import ChildProcessManager
from ccutils.dataStructures.multithreadingQueue import GenericThreadSafeQueue
from network.ftp.ftpClient import FTPClient
from virtualMachineServer.networking.reactors import MainServerPacketReactor
from time import sleep
from virtualMachineServer.threads.fileTransferThread import FileTransferThread
from virtualMachineServer.threads.compressionThread import CompressionThread
import os
import multiprocessing
import sys

class VMServerException(Exception):
    """
    Clase de excepción que utiliza el servidor de máquinas virtuales
    """
    pass

class VMServerReactor(MainServerPacketReactor):
    """
    Clase del reactor del servidor de máquinas virtuales
    """
    def __init__(self, constantManager):
        """
        Inicializa el estado del reactor, establece las conexiones con las bases de datos, arranca el conector de libvirt
        y empieza a atender las peticiones del servidor de máquinas virtuales.
        Argumentos:
            constantsManager: objeto del que se obtendrán los parámetros de configuración
        """        
        self.__shuttingDown = False
        self.__emergencyStop = False
        self.__fileTransferThread = None
        self.__compressionThread = None
        self.__libvirtConnection = None
        self.__networkManager = None
        self.__virtualNetworkManager = None
        self.__cManager = constantManager
        self.__ftp = FTPClient()
        self.__transferQueue = GenericThreadSafeQueue()
        self.__compressionQueue = GenericThreadSafeQueue()
        self.__mainServerCallback = ClusterServerCallback(self)
        self.__childProcessManager = ChildProcessManager()
        try :
            self.__connectToDatabases(self.__cManager.getConstant("databaseName"), self.__cManager.getConstant("databaseUserName"), self.__cManager.getConstant("databasePassword"))
            self.__connectToLibvirt(self.__cManager.getConstant("createVirtualNetworkAsRoot"))
            self.__doInitialCleanup()        
            self.__startListenning(self.__cManager.getConstant("vncNetworkInterface"), self.__cManager.getConstant("listenningPort"))
        except Exception as e:
            print e.message
            self.__emergencyStop = True
            self.__shuttingDown = True
        
    def __connectToDatabases(self, databaseName, user, password) :
        """
        Establece la conexión con la base de datos
        Argumentos:
            databaseName: el nombre de la base de datos
            user: el usuario a utilizar
            password: la contraseña a utilizar
        Devuelve:
            Nada
        """
        self.__dbConnector = VMServerDBConnector(user, password, databaseName)
        
    def __connectToLibvirt(self, createVirtualNetworkAsRoot) :
        """
        Establece la conexión con libvirt y crea la red virtual.
        Argumentos:
            createVirtualNetworkAsRoot: indica si hay que crear la red virtual como el superusuario o como
            un usuario normal.
        Devuelve:
            Nada
        """
        self.__libvirtConnection = LibvirtConnector(LibvirtConnector.KVM, self.__onDomainStart, self.__onDomainStop)
        self.__virtualNetworkManager = VirtualNetworkManager(createVirtualNetworkAsRoot)
        self.__virtualNetworkManager.createVirtualNetwork(self.__cManager.getConstant("vnName"), self.__cManager.getConstant("gatewayIP"), 
                                                          self.__cManager.getConstant("netMask"), self.__cManager.getConstant("dhcpStartIP"), 
                                                          self.__cManager.getConstant("dhcpEndIP"))
            
    def __startListenning(self, networkInterface, listenningPort):
        """
        Crea la conexión de red por la que se recibirán los comandos del servidor de cluster.
        """
        try :
            self.__vncServerIP = get_ip_address(networkInterface)
        except Exception :
            raise Exception("Error: the network interface '{0}' is not ready. Exiting now".format(networkInterface))
        self.__listenningPort = listenningPort
        self.__networkManager = NetworkManager(self.__cManager.getConstant("certificatePath"))
        self.__networkManager.startNetworkService()
        self.__packetManager = VMServerPacketHandler(self.__networkManager)        
        self.__networkManager.listenIn(self.__listenningPort, self.__mainServerCallback, True)
        self.__fileTransferThread = FileTransferThread(self.__networkManager, self.__listenningPort, self.__packetManager,
                                                       self.__transferQueue, self.__compressionQueue, self.__cManager.getConstant("TransferDirectory"),
                                                       self.__cManager.getConstant("FTPTimeout"))
        self.__fileTransferThread.start()
        self.__compressionThread = CompressionThread(self.__cManager.getConstant("sourceImagePath"), self.__cManager.getConstant("TransferDirectory"), 
                                                     self.__compressionQueue)
        self.__compressionThread.start()

    def __onDomainStart(self, domain):
        """
        Método que se ejecuta cuando una máquina virtual arranca.  Se limita a enviar los datos
        de conexión a los usuarios.
        Argumentos:
            domain: objeto que identifica a la máquina que se ha arrancado.
        Devuelve:
            Nada
        """
        self.__sendConnectionData(domain)
    
    def __sendConnectionData(self, domainInfo):
        """
        Envía al servidor de cluster los datos de conexión a una máquina virtual.
        Argumentos:
            domainInfo: diccionario con los datos de conexión al servidor VNC
        Devuelve:
            Nada
        """
        ip = domainInfo["VNCip"]
        port = domainInfo["VNCport"]
        password = domainInfo["VNCpassword"]
        domainName = domainInfo["name"]
        commandID = None
        while (commandID == None) :
            commandID = self.__dbConnector.getVMBootCommand(domainName)
            if (commandID == None) :
                sleep(0.1)
        packet = self.__packetManager.createVMConnectionParametersPacket(ip, port + 1, password, commandID)
        self.__networkManager.sendPacket('', self.__listenningPort, packet)
        
    def __onDomainStop(self, domainInfo):
        """
        Método que se ejecuta cuando una máquina virtual se apaga. Se limita a liberar sus recursos.
        Argumentos:
            domainInfo: diccionario con los datos de la máquina virtual
        Devuelve:
            Nada
        """
        # Se ha apagado una máquina virtual, borro sus datos
        if self.__shuttingDown and (self.__libvirtConnection.getNumberOfDomains() == 0):
            self.__shuttingDown = True
        if (self.__dbConnector.getVMBootCommand(domainInfo["name"]) != None) :
            # Al cargarnos manualmente el dominio, ya hemos liberado sus recursos. En estos
            # casos, no hay que hacer nada.
            self.__freeDomainResources(domainInfo["name"])
        
    def __freeDomainResources(self, domainName, deleteDiskImages=True):
        """
        Libera los recursos asignados a una máquina virtual
        Argumentos:
            domainName: el nombre de la máquina virtual
            deleteDiskImages: indica si hay que borrar o no las imágenes de disco.
        Devuelve:
            Nada
        """
        dataPath = self.__dbConnector.getDomainDataImagePath(domainName)
        osPath = self.__dbConnector.getDomainOSImagePath(domainName)   
        websockify_pid = self.__dbConnector.getWebsockifyDaemonPID(domainName)
        
        try :
            ChildProcessManager.runCommandInForeground("kill -s TERM " + str(websockify_pid))
        except Exception:
            pass    
        
        if deleteDiskImages :
            ChildProcessManager.runCommandInForeground("rm " + dataPath, VMServerException)
            ChildProcessManager.runCommandInForeground("rm " + osPath, VMServerException)
            dataDirectory = os.path.dirname(dataPath)
            osDirectory = os.path.dirname(osPath)
            if (os.listdir(dataDirectory) == []) :
                ChildProcessManager.runCommandInForeground("rm -rf " + dataDirectory, VMServerException)
            if (osDirectory != dataDirectory and os.listdir(osDirectory) == []) :
                ChildProcessManager.runCommandInForeground("rm -rf " + osDirectory, VMServerException)
                
        self.__dbConnector.unregisterDomainResources(domainName)        
    
    def shutdown(self):
        """
        Apaga el servidor de máquinas virtuales.
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        @attention: Para que no se produzcan cuelgues en la red, este método DEBE llamarse desde el hilo 
        principal.
        """
        if (self.__networkManager != None) :
            self.__networkManager.stopNetworkService() # Dejar de atender peticiones inmediatamente
        if (not self.__emergencyStop) :            
            timeout = 300 # 5 mins
            if (self.__destroyDomains) :
                self.__libvirtConnection.destroyAllDomains()
            else :
                wait_time = 0
                while (self.__libvirtConnection.getNumberOfDomains() != 0 and wait_time < timeout) :
                    sleep(0.5)
                    wait_time += 0.5
        self.__childProcessManager.waitForBackgroundChildrenToTerminate()
        if (self.__virtualNetworkManager != None) :
            try :
                self.__virtualNetworkManager.destroyVirtualNetwork(self.__cManager.getConstant("vnName"))  
            except Exception:
                pass
        if (self.__fileTransferThread != None) :
            self.__fileTransferThread.stop()
            self.__fileTransferThread.join()
        if (self.__compressionThread != None) :
            self.__compressionThread.stop()
            self.__compressionThread.join()
        sys.exit()   
           
        
    def processClusterServerIncomingPackets(self, packet):
        """
        Procesa un paquete enviado desde el servidor de cluster.
        Argumentos:
            packet: el paquete a procesar
        Devuelve:
            Nada
        """
        data = self.__packetManager.readPacket(packet)
        if (data["packet_type"] == VM_SERVER_PACKET_T.CREATE_DOMAIN) :
            self.__processVMBootPacket(data)
        elif (data["packet_type"] == VM_SERVER_PACKET_T.SERVER_STATUS_REQUEST) :
            self.__sendStatusData()
        elif (data["packet_type"] == VM_SERVER_PACKET_T.USER_FRIENDLY_SHUTDOWN) :
            self.__doUserFriendlyShutdown(data)
        elif (data["packet_type"] == VM_SERVER_PACKET_T.HALT) :
            self.__doImmediateShutdown()
        elif (data['packet_type'] == VM_SERVER_PACKET_T.QUERY_ACTIVE_VM_DATA) :
            self.__sendDomainsVNCConnectionData()
        elif (data['packet_type'] == VM_SERVER_PACKET_T.DESTROY_DOMAIN) :
            self.__destroyDomain(data)
        elif (data['packet_type'] == VM_SERVER_PACKET_T.QUERY_ACTIVE_DOMAIN_UIDS) :
            self.__sendActiveDomainUIDs()
        elif (data['packet_type'] == VM_SERVER_PACKET_T.IMAGE_EDITION) :
            self.__editImage(data)
        
    def __editImage(self, data):
        # Encolar la transferencia
        data.pop("packet_type")
        data["retrieve"] = True
        data["FTPTimeout"] = self.__cManager.getConstant("FTPTimeout")
        self.__transferQueue.queue(data)

    def __sendDomainsVNCConnectionData(self):
        '''
        Envía al servidor de cluster los datos de conexion de todas las máquinas virtuales
        que estén arrancadas
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        '''
        # Extraer los datos de la base de datos
        vncConnectionData = self.__dbConnector.getDomainsConnectionData()
        # Generar los segmentos en los que se dividirá la información
        segmentSize = 150
        segmentCounter = 1
        outgoingData = []
        if (len(vncConnectionData) == 0):
            segmentCounter = 0
        segmentNumber = (len(vncConnectionData) / segmentSize)
        if (len(vncConnectionData) % segmentSize != 0) :
            segmentNumber += 1
            sendLastSegment = True
        else :
            sendLastSegment = False # Para ahorrar tráfico
        for connectionParameters in vncConnectionData :
            outgoingData.append(connectionParameters)
            if (len(outgoingData) >= segmentSize) :
                # Flush
                packet = self.__packetManager.createActiveVMsDataPacket(self.__vncServerIP, segmentCounter, segmentNumber, outgoingData)
                self.__networkManager.sendPacket('', self.__listenningPort, packet)
                outgoingData = []
                segmentCounter += 1
        # Send the last segment
        if (sendLastSegment) :
            packet = self.__packetManager.createActiveVMsDataPacket(self.__vncServerIP, segmentCounter, segmentNumber, outgoingData)
            self.__networkManager.sendPacket('', self.__listenningPort, packet) 

    def __processVMBootPacket(self, data):
        """
        Arranca una máquina virtual
        Argumentos:
            data: un diccionario con los datos necesarios para arrancar la máquina virtual
        Devuelve:
            Nada
        """
        imageID = data["MachineID"]
        userID = data["UserID"]
        configFile = self.__cManager.getConstant("configFilePath") + self.__dbConnector.getDefinitionFilePath(imageID)
        originalName = "{0}_".format(imageID)
        dataPath = self.__dbConnector.getDataImagePath(imageID)
        osPath = self.__dbConnector.getOSImagePath(imageID)
        
        # Saco el nombre de los archivos (sin la extension)
        trimmedDataImagePath = dataPath
        try:
            trimmedDataImagePath = dataPath[0:dataPath.index(".qcow2")]
        except:
            pass
        trimmedOSImagePath = osPath
        try:
            trimmedOSImagePath = osPath[0:osPath.index(".qcow2")]
        except:
            pass       
        
        # Obtengo los parámetros de configuración de la máquina virtual
        newUUID, newMAC = self.__dbConnector.extractFreeMACAndUUID()
        newPort = self.__dbConnector.extractFreeVNCPort()
        newName = originalName + str(newPort)
        newDataDisk = self.__cManager.getConstant("executionImagePath") + trimmedDataImagePath + str(newPort) + ".qcow2"
        newOSDisk = self.__cManager.getConstant("executionImagePath") + trimmedOSImagePath + str(newPort) + ".qcow2"
        newPassword = self.__generateVNCPassword()
        sourceOSDisk = self.__cManager.getConstant("sourceImagePath") + osPath        
        
        # Preparo los archivos
                
        # Compruebo si ya existe alguno de los archivos. Si es el caso, me los cargo
        if (os.path.exists(newDataDisk)):
            print("Warning: the file " + newDataDisk + " already exists")
            ChildProcessManager.runCommandInForeground("rm " + newDataDisk, VMServerException)
            
        if (os.path.exists(newOSDisk)):
            print("Warning: the file " + newOSDisk + " already exists")
            ChildProcessManager.runCommandInForeground("rm " + newOSDisk, VMServerException)
            
        # Copio las imagenes
        ChildProcessManager.runCommandInForeground("cd " + self.__cManager.getConstant("sourceImagePath") + ";" + "cp --parents "+ dataPath + " " + 
                                                   self.__cManager.getConstant("executionImagePath"), VMServerException)
        ChildProcessManager.runCommandInForeground("mv " + self.__cManager.getConstant("executionImagePath") + dataPath +" " + newDataDisk, VMServerException)
        ChildProcessManager.runCommandInForeground("qemu-img create -b " + sourceOSDisk + " -f qcow2 " + newOSDisk, VMServerException)
        
        # Genero el fichero de definición
        xmlFile = ConfigurationFileEditor(configFile)
        xmlFile.setDomainIdentifiers(newName, newUUID)
        xmlFile.setImagePaths(newOSDisk, newDataDisk)
        xmlFile.setVirtualNetworkConfiguration(self.__cManager.getConstant("vnName"), newMAC)
        xmlFile.setVNCServerConfiguration(self.__vncServerIP, newPort, newPassword)
        
        string = xmlFile.generateConfigurationString()
        
        # Arranco la máquina
        self.__libvirtConnection.startDomain(string)
        
        # Inicio el demonio websockify
        # Los puertos impares serán para el socket que proporciona el hipervisor 
        # y los pares los websockets generados por websockify        
        
        webSockifyPID = self.__childProcessManager.runCommandInBackground([self.__cManager.getConstant("websockifyPath"),
                                    self.__vncServerIP + ":" + str(newPort + 1),
                                    self.__vncServerIP + ":" + str(newPort)])
        
        self.__dbConnector.registerVMResources(newName, imageID, newPort, newPassword, userID, webSockifyPID, newOSDisk,  newDataDisk, newMAC, newUUID)
        self.__dbConnector.addVMBootCommand(newName, data["CommandID"])
        
    def __destroyDomain(self, packet):
        """
        Destruye una máquina virtual por petición explícita de su propietario.
        Argumentos:
            packet: un diccionario con los datos del paquete de destrucción
        Devuelve:
            Nada
        """
        domainName = self.__dbConnector.getDomainNameFromVMBootCommand(packet["VMID"])
        if (domainName == None) :
            # No informamos del error: el servidor de máquinas virtuales siempre intenta
            # hacer lo que se le pide, y si no puede, no lo hace y no se queja.
            return 
        self.__libvirtConnection.destroyDomain(domainName)
        # Libvirt borra las imágenes de disco, por lo que sólo tenemos que encargarnos de actualizar
        # las bases de datos.
        self.__freeDomainResources(domainName, False)
        
    
    def __sendStatusData(self):
        """
        Recopila la información de estado del servidor de máquinas virtuales y se la envía al servidor de cluster.
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        """
        info = self.__libvirtConnection.getStatusInfo()
        realCPUNumber = multiprocessing.cpu_count()
        diskStats_storage = os.statvfs(self.__cManager.getConstant("sourceImagePath"))
        diskStats_temporaryData = os.statvfs(self.__cManager.getConstant("executionImagePath"))
        freeOutput = ChildProcessManager.runCommandInForeground("free -k", VMServerException)
        
        # free devuelve la siguiente salida
        #              total       used       free     shared    buffers     cached
        # Mem:    4146708480 3939934208  206774272          0  224706560 1117671424
        # -/+ buffers/cache: 2597556224 1549152256
        # Swap:   2046816256   42455040 2004361216
        #
        # Cogemos la tercera línea
           
        availableMemory = int(freeOutput.split("\n")[1].split()[1])
        freeMemory = int(freeOutput.split("\n")[2].split()[2])
        freeStorageSpace = diskStats_storage.f_bfree * diskStats_storage.f_frsize / 1024
        availableStorageSpace = diskStats_storage.f_bavail * diskStats_storage.f_frsize / 1024
        freeTemporaryStorage = diskStats_temporaryData.f_bfree * diskStats_temporaryData.f_frsize / 1024
        availableTemporaryStorage = diskStats_temporaryData.f_bavail * diskStats_temporaryData.f_frsize / 1024
        packet = self.__packetManager.createVMServerStatusPacket(self.__vncServerIP, info["#domains"], freeMemory, availableMemory, 
                                                                 freeStorageSpace, availableStorageSpace, 
                                                                 freeTemporaryStorage, availableTemporaryStorage,
                                                                 info["#vcpus"], realCPUNumber)
        self.__networkManager.sendPacket('', self.__listenningPort, packet)
    
    def __doUserFriendlyShutdown(self, packet):
        """
        Realiza un apagado amigable (es decir, espera a que los usuarios acaben).
        Argumentos:
            packet: no se usa (por ahora), pero se usará para resolver un issue.
        Devuelve:
            Nada
        """
        self.__shuttingDown = True
        self.__destroyDomains = False
    
    def __doImmediateShutdown(self):
        """
        Realiza el apagado inmediato del servidor de máquinas virtuales.
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        """
        self.__shuttingDown = True      
        self.__destroyDomains = True  
        
    def __generateVNCPassword(self):
        """
        Genera una contraseña para un servidor VNC
        Argumentos:
            Ninguno
        Devuelve:
            Un string con la contraseña generada
        """
        return ChildProcessManager.runCommandInForeground("openssl rand -base64 " + str(self.__cManager.getConstant("passwordLength")), VMServerException)
    
    def __sendActiveDomainUIDs(self):
        """
        Envía los UIDs de los dominios activos al servidor de cluster
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        """
        activeDomainUIDs = self.__dbConnector.getActiveDomainUIDs()
        packet = self.__packetManager.createActiveDomainUIDsPacket(self.__vncServerIP, activeDomainUIDs)
        self.__networkManager.sendPacket('', self.__listenningPort, packet)
    
    def has_finished(self):
        """
        Indica si el servidor de máquinas virtuales se ha apagado o no.
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        """
        return self.__shuttingDown
    
    def __doInitialCleanup(self):
        """
        Borra toda la basura que hay en el directorio de trabajo
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        """
        activeDomainNames = self.__libvirtConnection.getActiveDomainNames()
        registeredDomainNames = self.__dbConnector.getRegisteredDomainNames()
        for domainName in registeredDomainNames :
            if (not domainName in activeDomainNames) :
                self.__freeDomainResources(domainName)
        self.__dbConnector.allocateAssignedMACsUUIDsAndVNCPorts()