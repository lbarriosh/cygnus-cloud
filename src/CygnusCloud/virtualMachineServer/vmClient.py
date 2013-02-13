# -*- coding: utf8 -*-
'''
Created on 14/01/2013

@author: saguma
'''

from network.manager.networkManager import NetworkManager, NetworkCallback
from network.interfaces.ipAddresses import get_ip_address 
from libvirtConnector import libvirtConnector
from constantes import databaseName, databaseUserName, databasePassword, vncNetworkInterface, listenningPort, \
    vnName, gatewayIP, netMask, dhcpStartIP, dhcpEndIP, configFilePath, certificatePath, sourceImagePath, executionImagePath,\
    passwordLength, websockifyPath
from packets import VM_SERVER_PACKET_T, VMServerPacketHandler
from xmlEditor import ConfigurationFileEditor
from database.vmServer.imageManager import ImageManager
from database.vmServer.runtimeData import RuntimeData
from virtualNetwork.virtualNetworkManager import VirtualNetworkManager
from time import sleep

from ccutils.commands import runCommand, runCommandInBackground
import os

class VMClientException(Exception):
    pass

class VMClient(NetworkCallback):
    def __init__(self):
        self.__shutDown = False
        self.__shuttingDown = False
        self.__connectToDatabases(databaseName, databaseUserName, databasePassword)
        self.__connectToLibvirt()
        self.__startListenning(vncNetworkInterface, listenningPort)
        
    def __connectToDatabases(self, databaseName, user, password):
        self.__imageManager = ImageManager(user, password, databaseName)
        self.__runningImageData = RuntimeData(user, password, databaseName)
        
    def __connectToLibvirt(self) :
        self.__connector = libvirtConnector(libvirtConnector.KVM, self.__startedVM, self.__stoppedVM)
        self.__virtualNetworkManager = VirtualNetworkManager()
        self.__virtualNetworkManager.createVirtualNetwork(vnName, gatewayIP, netMask,
                                    dhcpStartIP, dhcpEndIP)
            
    def __startListenning(self, networkInterface, listenningPort):
        self.__vncServerIP = get_ip_address(networkInterface)
        self.__listenningPort = listenningPort
        self.__networkManager = NetworkManager(certificatePath)
        self.__networkManager.startNetworkService()
        self.__packetManager = VMServerPacketHandler(self.__networkManager)
        self.__networkManager.listenIn(self.__listenningPort, self, True) # Usamos SSL

    def __startedVM(self, domain):
        self.__sendConnectionData(domain)
    
    def __sendConnectionData(self, domainInfo):
        ip = domainInfo["VNCip"]
        port = domainInfo["VNCport"]
        password = domainInfo["VNCpassword"]
        domainName = domainInfo["name"]
        userID = None
        while (userID == None) :
            userID = self.__runningImageData.getAssignedUserInDomain(domainName)
            sleep(0.1)
        packet = self.__packetManager.createVMConnectionParametersPacket(userID, ip, port + 1, password)
        self.__networkManager.sendPacket('', self.__listenningPort, packet)
        
    def __stoppedVM(self, domainInfo):
        if self.__shuttingDown and (self.__connector.getNumberOfDomains() == 0):
            self.__shutDown = True

        name = domainInfo["name"]
        dataPath = self.__runningImageData.getMachineDataPathinDomain(name)
        osPath = self.__runningImageData.getOsImagePathinDomain(name)
        pidToKill = self.__runningImageData.getVMPidinDomain(name)
        
        # Delete the virtual machine images disk
        runCommand("rm " + dataPath, VMClientException)
        runCommand("rm " + osPath, VMClientException)
        
        # Kill websockify process
        runCommand("kill -s TERM " + str(pidToKill), VMClientException)
        
        # Update the database
        self.__runningImageData.unRegisterVMResources(name)
    
    def shutdown(self):
        # Cosas a hacer cuando se desea apagar el servidor.
        # Importante: esto debe llamarse desde el hilo principal
        self.__virtualNetworkManager.destroyVirtualNetwork(vnName)
        self.__networkManager.stopNetworkService()
        
    def processPacket(self, packet):
        packetData = self.__packetManager.readPacket(packet)
        print "paquete recibido " + str(packetData['packet_type'])
        processPacket = {
            VM_SERVER_PACKET_T.CREATE_DOMAIN: self.__createDomain, 
            VM_SERVER_PACKET_T.SERVER_STATUS_REQUEST: self.__serverStatusRequest,
            VM_SERVER_PACKET_T.USER_FRIENDLY_SHUTDOWN: self.__userFriendlyShutdown,
            VM_SERVER_PACKET_T.HALT: self.__halt}
        if (packetData['packet_type'] == VM_SERVER_PACKET_T.QUERY_ACTIVE_VM_DATA) :
            self.__sendVNCConnectionData()
        else :
            processPacket[packetData['packet_type']](packetData)
        
    def __sendVNCConnectionData(self):
        # Extraer los datos de la base de datos
        vncConnectionData = self.__runningImageData.getVMsConnectionData()
        # Generar los segmentos
        segmentSize = 5
        segmentCounter = 1
        outgoingData = []
        if (len(vncConnectionData) == 0) :
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
        idVM = info["MachineID"]
        userID = info["UserID"]
        configFile = configFilePath + self.__imageManager.getFileConfigPath(idVM)
        originalName = self.__imageManager.getName(idVM)
        dataPath = self.__imageManager.getImagePath(idVM)
        osPath = self.__imageManager.getOsImagePath(idVM)
        
        # Calculo los nuevos parametros
        newUUID, newMAC = self.__getNewMAC_UUID()
        newPort = self.__getNewPort()
        newName = originalName + str(newPort)
        newDataDisk = executionImagePath + dataPath + str(newPort) + ".qcow2"
        newOSDisk = executionImagePath + osPath + str(newPort) + ".qcow2"
        newPassword = self.__getNewPassword()
        # Esta variable no se está utilizando
        #sourceDataDisk = sourceImagePath + dataPath
        sourceOSDisk = sourceImagePath + osPath        
        
        # Preparo los archivos
                
        # Compruebo si ya existe alguno de los archivos
        if (os.path.exists(newDataDisk)):
            print("The file " + newDataDisk + " already exist")
            return
        if (os.path.exists(newOSDisk)):
            print("The file " + newOSDisk + " already exist")
            return
        # Copio las imagenes
        runCommand("cd " + sourceImagePath + ";" + "cp --parents "+ dataPath + " " + executionImagePath, VMClientException)
        runCommand("mv " + executionImagePath + dataPath +" " + newDataDisk, VMClientException)
        runCommand("qemu-img create -b " + sourceOSDisk + " -f qcow2 " + newOSDisk, VMClientException)
        #runCommand("chmod -R 777 " + executionImagePath, VMClientException)
        
        # Fichero de configuracion
        xmlFile = ConfigurationFileEditor(configFile)
        xmlFile.setDomainIdentifiers(newName, newUUID)
        xmlFile.setImagePaths(newOSDisk, newDataDisk)
        xmlFile.setNetworkConfiguration(vnName, newMAC)
        xmlFile.setVNCServerConfiguration(self.__vncServerIP, newPort, newPassword)
        
        string = xmlFile.generateConfigurationString()
        
        # Arranco la máquina
        self.__connector.startDomain(string)
        
        # Inicio el websockify
        # Los puertos impares (por ejemplo) serán para KVM 
        # y los pares los websockets
        pidWS = runCommandInBackground([websockifyPath,
                    self.__vncServerIP + ":" + str(newPort + 1),
                    self.__vncServerIP + ":" + str(newPort)])
        
        # Actualizo la base de datos
        self.__runningImageData.registerVMResources(newName, newPort, userID, idVM, pidWS, newDataDisk, newOSDisk, newMAC, newUUID, newPassword)
        
    
    def __serverStatusRequest(self, packet):
        activeDomains = self.__connector.getNumberOfDomains()
        packet = self.__packetManager.createVMServerStatusPacket(self.__vncServerIP, activeDomains)
        self.__networkManager.sendPacket('', self.__listenningPort, packet)
    
    def __userFriendlyShutdown(self, packet):
        self.__shuttingDown = True
    
    def __halt(self, packet):
        # Destruyo los dominios
        self.__connector.stopAllDomain()
        self.__shutDown = True
    
    def __getNewMAC_UUID(self):
        return self.__runningImageData.extractfreeMacAndUuid()
        
    def __getNewPort(self):
        return self.__runningImageData.extractfreeVNCPort()
        
    def __getNewPassword(self):
        return runCommand("openssl rand -base64 " + str(passwordLength), VMClientException)
    
    def hasFinished(self):
        return self.__shutDown