# -*- coding: utf8 -*-
'''
Created on 14/01/2013

@author: saguma
'''

from network.manager.networkManager import NetworkManager
from virtualMachineServer.callback import MainServerCallback
from network.interfaces.ipAddresses import get_ip_address 
from libvirtConnector import libvirtConnector
from packets import VM_SERVER_PACKET_T, VMServerPacketHandler
from xmlEditor import ConfigurationFileEditor
from database.vmServer.vmServerDB import VMServerDBConnector
from virtualNetwork.virtualNetworkManager import VirtualNetworkManager
from ccutils.processes.childProcessManager import ChildProcessManager 
from time import sleep
import os

class VMServerException(Exception):
    pass

class MainServerPacketReactor():
    
    def processClusterServerIncomingPackets(self, packet):
        raise NotImplementedError

class VMServer(MainServerPacketReactor):
    def __init__(self, constantManager):
        # Inicializo las variables para saber cuando hay que apagarlo todo
        self.__shuttingDown = False
        self.__shuttingDown = False
        self.__cManager = constantManager
        self.__mainServerCallback = MainServerCallback(self)
        self.__childProcessManager = ChildProcessManager()
        self.__connectToDatabases("VMServerDB", self.__cManager.getConstant("databaseUserName"), self.__cManager.getConstant("databasePassword"))
        self.__connectToLibvirt(self.__cManager.getConstant("createVirtualNetworkAsRoot"))
        self.__doInitialCleanup()
        self.__startListenning(self.__cManager.getConstant("vncNetworkInterface"), self.__cManager.getConstant("listenningPort"))
        
    def __connectToDatabases(self, databaseName, user, password) :
        self.__dbConnector = VMServerDBConnector(user, password, databaseName)
        
    def __connectToLibvirt(self, createVirtualNetworkAsRoot) :
        # Inicializo la librería libvirt y creo la red virtual que da acceso por red a las máquinas virtuales.
        self.__libvirtConnector = libvirtConnector(libvirtConnector.KVM, self.__startedVM, self.__stoppedVM)
        self.__virtualNetworkManager = VirtualNetworkManager(createVirtualNetworkAsRoot)
        self.__virtualNetworkManager.createVirtualNetwork(self.__cManager.getConstant("vnName"), self.__cManager.getConstant("gatewayIP"), 
                                                          self.__cManager.getConstant("netMask"), self.__cManager.getConstant("dhcpStartIP"), 
                                                          self.__cManager.getConstant("dhcpEndIP"))
            
    def __startListenning(self, networkInterface, listenningPort):
        # Inicializo la red que comunicará el servidor de máquinas virtuales
        # con el servidor principal
        self.__vncServerIP = get_ip_address(networkInterface)
        self.__listenningPort = listenningPort
        self.__networkManager = NetworkManager(self.__cManager.getConstant("certificatePath"))
        self.__networkManager.startNetworkService()
        self.__packetManager = VMServerPacketHandler(self.__networkManager)
        self.__networkManager.listenIn(self.__listenningPort, self.__mainServerCallback, True)

    def __startedVM(self, domain):
        # Se ha iniciado una máquina virtual -> envio sus datos de conexion
        self.__sendConnectionData(domain)
    
    def __sendConnectionData(self, domainInfo):
        ip = domainInfo["VNCip"]
        port = domainInfo["VNCport"]
        password = domainInfo["VNCpassword"]
        domainName = domainInfo["name"]
        commandID = None
        while (commandID == None) :
            commandID = self.__dbConnector.getVMBootCommand(domainName)
        packet = self.__packetManager.createVMConnectionParametersPacket(ip, port + 1, password, commandID)
        self.__networkManager.sendPacket('', self.__listenningPort, packet)
        
    def __stoppedVM(self, domainInfo):
        # Se ha apagado una máquina virtual, borro sus datos
        if self.__shuttingDown and (self.__libvirtConnector.getNumberOfDomains() == 0):
            self.__shuttingDown = True
        self.__freeDomainResources(domainInfo["name"])
        
    def __freeDomainResources(self, domainName, deleteDiskImages=True):
        dataPath = self.__dbConnector.getDomainImageDataPath(domainName)
        osPath = self.__dbConnector.getOsImagePathFromDomainName(domainName)
        pidToKill = self.__dbConnector.getVMPIDFromDomainName(domainName)
        
        if (deleteDiskImages) :
            ChildProcessManager.runCommandInForeground("rm " + dataPath, VMServerException)
            ChildProcessManager.runCommandInForeground("rm " + osPath, VMServerException)
        
        try :        
            ChildProcessManager.terminateProcess(pidToKill, VMServerException)
        except Exception as e :
            print("Unable to terminate websockify process: " + e.message)
                
        self.__dbConnector.unregisterVMResources(domainName)
        
    
    def shutdown(self):
        # Cosas a hacer cuando se desea apagar el servidor.
        # Importante: esto debe llamarse desde el hilo principal
        self.__networkManager.stopNetworkService() # Dejar de atender peticiones inmediatamente
        timeout = 300 # 5 mins
        if (self.__destroyDomains) :
            self.__libvirtConnector.stopAllDomains()
        else :
            wait_time = 0
            while (self.__libvirtConnector.getNumberOfDomains() != 0 and wait_time < timeout) :
                sleep(0.5)
                wait_time += 0.5
        self.__childProcessManager.waitForBackgroundChildrenToTerminate()
        self.__virtualNetworkManager.destroyVirtualNetwork(self.__cManager.getConstant("vnName"))        
        
    def processClusterServerIncomingPackets(self, packet):
        data = self.__packetManager.readPacket(packet)
        if (data["packet_type"] == VM_SERVER_PACKET_T.CREATE_DOMAIN) :
            self.__createDomain(data)
        elif (data["packet_type"] == VM_SERVER_PACKET_T.SERVER_STATUS_REQUEST) :
            self.__serverStatusRequest(data)
        elif (data["packet_type"] == VM_SERVER_PACKET_T.USER_FRIENDLY_SHUTDOWN) :
            self.__userFriendlyShutdown(data)
        elif (data["packet_type"] == VM_SERVER_PACKET_T.HALT) :
            self.__halt(data)
        elif (data['packet_type'] == VM_SERVER_PACKET_T.QUERY_ACTIVE_VM_DATA) :
            self.__sendActiveVMsVNCConnectionData()
        elif (data['packet_type'] == VM_SERVER_PACKET_T.DESTROY_DOMAIN) :
            self.__destroyDomain(data)
        elif (data['packet_type'] == VM_SERVER_PACKET_T.QUERY_ACTIVE_DOMAIN_UIDS) :
            self.__sendActiveDomainUIDs()
        
    def __sendActiveVMsVNCConnectionData(self):
        '''
        Envía la informacion de conexion de todas las máquinas virtuales
        que estén arrancadas
        '''
        # Extraer los datos de la base de datos
        vncConnectionData = self.__dbConnector.getVMsConnectionData()
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

    def __createDomain(self, info):
        vmID = info["MachineID"]
        userID = info["UserID"]
        configFile = self.__cManager.getConstant("configFilePath") + self.__dbConnector.getImgDefFilePath(vmID)
        originalName = self.__dbConnector.getImageName(vmID)
        dataPath = self.__dbConnector.getImagePath(vmID)
        osPath = self.__dbConnector.getOsImagePath(vmID)
        
        #Saco el nombre de los archivos (sin la extension)
        dataPathStripped = dataPath
        try:
            dataPathStripped = dataPath[0:dataPath.index(".qcow2")]
        except:
            pass
        osPathStripped = osPath
        try:
            osPathStripped = osPath[0:osPath.index(".qcow2")]
        except:
            pass
        # Obtengo los nuevos parámetros de la máquina virtual
        newUUID, newMAC = self.__getNewMAC_UUID()
        newPort = self.__getNewPort()
        newName = originalName + str(newPort)
        newDataDisk = self.__cManager.getConstant("executionImagePath") + dataPathStripped + str(newPort) + ".qcow2"
        newOSDisk = self.__cManager.getConstant("executionImagePath") + osPathStripped + str(newPort) + ".qcow2"
        newPassword = self.__getNewPassword()
        # Esta variable no se está utilizando
        #sourceDataDisk = sourceImagePath + dataPath
        sourceOSDisk = self.__cManager.getConstant("sourceImagePath") + osPath        
        
        # Preparo los archivos
                
        # Compruebo si ya existe alguno de los archivos
        if (os.path.exists(newDataDisk)):
            print("The file " + newDataDisk + " already exists")
            return
        if (os.path.exists(newOSDisk)):
            print("The file " + newOSDisk + " already exists")
            return
        # Copio las imagenes
        ChildProcessManager.runCommandInForeground("cd " + self.__cManager.getConstant("sourceImagePath") + ";" + "cp --parents "+ dataPath + " " + 
                                                   self.__cManager.getConstant("executionImagePath"), VMServerException)
        ChildProcessManager.runCommandInForeground("mv " + self.__cManager.getConstant("executionImagePath") + dataPath +" " + newDataDisk, VMServerException)
        ChildProcessManager.runCommandInForeground("qemu-img create -b " + sourceOSDisk + " -f qcow2 " + newOSDisk, VMServerException)
        #runCommand("chmod -R 777 " + executionImagePath, VMServerException)
        
        # Fichero de configuracion
        xmlFile = ConfigurationFileEditor(configFile)
        xmlFile.setDomainIdentifiers(newName, newUUID)
        xmlFile.setImagePaths(newOSDisk, newDataDisk)
        xmlFile.setNetworkConfiguration(self.__cManager.getConstant("vnName"), newMAC)
        xmlFile.setVNCServerConfiguration(self.__vncServerIP, newPort, newPassword)
        
        string = xmlFile.generateConfigurationString()
        
        # Arranco la máquina
        self.__libvirtConnector.startDomain(string)
        
        # Inicio el websockify
        # Los puertos impares serán para el socket que proporciona el hipervisor 
        # y los pares los websockets generados por websockify        
        
        webSockifyPID = self.__childProcessManager.runCommandInBackground(["../../utils/websockify",
                                    self.__vncServerIP + ":" + str(newPort + 1),
                                    self.__vncServerIP + ":" + str(newPort)])
        
        self.__dbConnector.registerVMResources(newName, vmID, newPort, newPassword, userID, webSockifyPID, newDataDisk, newOSDisk, newMAC, newUUID)
        self.__dbConnector.addVMBootCommand(newName, info["CommandID"])
        
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
        self.__libvirtConnector.destroyDomain(domainName)
        # Libvirt borra las imágenes de disco, por lo que sólo tenemos que encargarnos de actualizar
        # las bases de datos.
        self.__freeDomainResources(domainName, False)
        
    
    def __serverStatusRequest(self, packet):
        activeDomains = self.__libvirtConnector.getNumberOfDomains()
        packet = self.__packetManager.createVMServerStatusPacket(self.__vncServerIP, activeDomains)
        self.__networkManager.sendPacket('', self.__listenningPort, packet)
    
    def __userFriendlyShutdown(self, packet):
        self.__shuttingDown = True
        self.__destroyDomains = False
    
    def __halt(self, packet):
        self.__shuttingDown = True      
        self.__destroyDomains = True  
    
    def __getNewMAC_UUID(self):
        return self.__dbConnector.extractFreeMACAndUUID()
        
    def __getNewPort(self):
        return self.__dbConnector.extractFreeVNCPort()
        
    def __getNewPassword(self):
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
    
    def halt(self):
        return self.__shuttingDown
    
    def __doInitialCleanup(self):
        """
        Deletes all the garbage that is stored in the temporary folders.
        Args:
            None
        Returns:
            Nothing
        """
        activeDomainNames = self.__libvirtConnector.getActiveDomainNames()
        registeredDomainNames = self.__dbConnector.getRegisteredDomainNames()
        for domainName in registeredDomainNames :
            if (not domainName in activeDomainNames) :
                self.__freeDomainResources(domainName)
        self.__dbConnector.allocateAssignedResources()