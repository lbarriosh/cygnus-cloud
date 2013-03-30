# -*- coding: utf8 -*-
'''
Created on 14/01/2013

@author: saguma
'''

from network.manager.networkManager import NetworkManager
from virtualMachineServer.callback import MainServerCallback
from network.interfaces.ipAddresses import get_ip_address 
from libvirtConnector import libvirtConnector
from constantes import databaseName, databaseUserName, databasePassword, vncNetworkInterface, listenningPort, \
    vnName, gatewayIP, netMask, dhcpStartIP, dhcpEndIP, configFilePath, certificatePath, sourceImagePath, executionImagePath,\
    passwordLength, websockifyPath, createVirtualNetworkAsRoot
from packets import VM_SERVER_PACKET_T, VMServerPacketHandler
from xmlEditor import ConfigurationFileEditor
from database.vmServer.vmServerDB import VMServerDBConnector
from virtualNetwork.virtualNetworkManager import VirtualNetworkManager
from ccutils.processes.childProcessManager import ChildProcessManager 
import os

class VMServerException(Exception):
    pass

class MainServerPacketReactor():
    
    def processClusterServerIncomingPackets(self, packet):
        raise NotImplementedError

class VMServer(MainServerPacketReactor):
    def __init__(self):
        # Inicializo las variables para saber cuando hay que apagarlo todo
        self.__shutDown = False
        self.__shuttingDown = False
        self.__mainServerCallback = MainServerCallback(self)
        self.__childProcessManager = ChildProcessManager()
        self.__connectToDatabases(databaseName, databaseUserName, databasePassword)
        self.__connectToLibvirt(createVirtualNetworkAsRoot)
        self.__doInitialCleanup()
        self.__startListenning(vncNetworkInterface, listenningPort)
        
    def __connectToDatabases(self, databaseName, user, password) :
        self.__dbConnector = VMServerDBConnector(user, password, databaseName)
        
    def __connectToLibvirt(self, createVirtualNetworkAsRoot) :
        # Inicializo la librería libvirt y creo la red virtual que da acceso por red a las máquinas virtuales.
        self.__libvirtConnector = libvirtConnector(libvirtConnector.KVM, self.__startedVM, self.__stoppedVM)
        self.__virtualNetworkManager = VirtualNetworkManager(createVirtualNetworkAsRoot)
        self.__virtualNetworkManager.createVirtualNetwork(vnName, gatewayIP, netMask,
                                    dhcpStartIP, dhcpEndIP)
            
    def __startListenning(self, networkInterface, listenningPort):
        # Inicializo la red que comunicará el servidor de máquinas virtuales
        # con el servidor principal
        self.__vncServerIP = get_ip_address(networkInterface)
        self.__listenningPort = listenningPort
        self.__networkManager = NetworkManager(certificatePath)
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
            self.__shutDown = True
        self.__freeDomainResources(domainInfo["name"])
        
    def __freeDomainResources(self, domainName):
        dataPath = self.__dbConnector.getDomainImageDataPath(domainName)
        osPath = self.__dbConnector.getOsImagePathInDomain(domainName)
        pidToKill = self.__dbConnector.getVMPidInDomain(domainName)
        
        ChildProcessManager.runCommandInForeground("rm " + dataPath, VMServerException)
        ChildProcessManager.runCommandInForeground("rm " + osPath, VMServerException)
        
        try :        
            ChildProcessManager.terminateProcess(pidToKill, VMServerException)
        except Exception as e :
            print("Unable to terminate websockify process: " + str(e))
                
        self.__dbConnector.unregisterVMResources(domainName)
        
    
    def shutdown(self):
        # Cosas a hacer cuando se desea apagar el servidor.
        # Importante: esto debe llamarse desde el hilo principal
        self.__childProcessManager.waitForBackgroundChildrenToTerminate()
        self.__virtualNetworkManager.destroyVirtualNetwork(vnName)
        self.__networkManager.stopNetworkService()
        
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
            self.__sendVNCConnectionData()
        
    def __sendVNCConnectionData(self):
        '''
        Envía la informacion de conexion de todas las máquinas virtuales
        que estén arrancadas
        '''
        # Extraer los datos de la base de datos
        vncConnectionData = self.__dbConnector.getVMsConnectionData()
        # Generar los segmentos en los que se dividirá la información
        segmentSize = 5
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
        configFile = configFilePath + self.__dbConnector.getFileConfigPath(vmID)
        originalName = self.__dbConnector.getName(vmID)
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
        newDataDisk = executionImagePath + dataPathStripped + str(newPort) + ".qcow2"
        newOSDisk = executionImagePath + osPathStripped + str(newPort) + ".qcow2"
        newPassword = self.__getNewPassword()
        # Esta variable no se está utilizando
        #sourceDataDisk = sourceImagePath + dataPath
        sourceOSDisk = sourceImagePath + osPath        
        
        # Preparo los archivos
                
        # Compruebo si ya existe alguno de los archivos
        if (os.path.exists(newDataDisk)):
            print("The file " + newDataDisk + " already exists")
            return
        if (os.path.exists(newOSDisk)):
            print("The file " + newOSDisk + " already exists")
            return
        # Copio las imagenes
        ChildProcessManager.runCommandInForeground("cd " + sourceImagePath + ";" + "cp --parents "+ dataPath + " " + executionImagePath, VMServerException)
        ChildProcessManager.runCommandInForeground("mv " + executionImagePath + dataPath +" " + newDataDisk, VMServerException)
        ChildProcessManager.runCommandInForeground("qemu-img create -b " + sourceOSDisk + " -f qcow2 " + newOSDisk, VMServerException)
        #runCommand("chmod -R 777 " + executionImagePath, VMServerException)
        
        # Fichero de configuracion
        xmlFile = ConfigurationFileEditor(configFile)
        xmlFile.setDomainIdentifiers(newName, newUUID)
        xmlFile.setImagePaths(newOSDisk, newDataDisk)
        xmlFile.setNetworkConfiguration(vnName, newMAC)
        xmlFile.setVNCServerConfiguration(self.__vncServerIP, newPort, newPassword)
        
        string = xmlFile.generateConfigurationString()
        
        # Arranco la máquina
        self.__libvirtConnector.startDomain(string)
        
        # Inicio el websockify
        # Los puertos impares serán para el socket que proporciona el hipervisor 
        # y los pares los websockets generados por websockify        
        
        webSockifyPID = self.__childProcessManager.runCommandInBackground([websockifyPath,
                                    self.__vncServerIP + ":" + str(newPort + 1),
                                    self.__vncServerIP + ":" + str(newPort)])
        
        self.__dbConnector.registerVMResources(newName, vmID, newPort, newPassword, userID, webSockifyPID, newDataDisk, newOSDisk, newMAC, newUUID)
        self.__dbConnector.addVMBootCommand(newName, info["CommandID"])
        
    
    def __serverStatusRequest(self, packet):
        activeDomains = self.__libvirtConnector.getNumberOfDomains()
        packet = self.__packetManager.createVMServerStatusPacket(self.__vncServerIP, activeDomains)
        self.__networkManager.sendPacket('', self.__listenningPort, packet)
    
    def __userFriendlyShutdown(self, packet):
        self.__shuttingDown = True
    
    def __halt(self, packet):
        # Destruyo los dominios
        self.__libvirtConnector.stopAllDomains()
        self.__shutDown = True
    
    def __getNewMAC_UUID(self):
        return self.__dbConnector.extractFreeMACAndUUID()
        
    def __getNewPort(self):
        return self.__dbConnector.extractFreeVNCPort()
        
    def __getNewPassword(self):
        return ChildProcessManager.runCommandInForeground("openssl rand -base64 " + str(passwordLength), VMServerException)
    
    def hasFinished(self):
        return self.__shutDown
    
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