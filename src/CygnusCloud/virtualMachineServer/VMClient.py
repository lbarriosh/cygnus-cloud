# -*- coding: utf8 -*-
'''
Created on 14/01/2013

@author: saguma
'''

from network.manager import NetworkManager, NetworkCallback
from libvirtConnector import libvirtConnector
from Constantes import *
from packets import VM_SERVER_PACKET_T, VMServerPacketHandler
from xmlEditor import ConfigurationFileEditor
from database.VMServerDB import ImageManager, RuntimeData
from utils.commands import runCommand, runCommandBackground
try :
    import etree.cElementTree as ET
except ImportError:
    import etree.ElementTree as ET

class VMClientException(Exception):
    pass

class VMClient(NetworkCallback):
    def __init__(self):
        self.__waitForShutdown = False
        self.__db = ImageManager(userDB, passwordDB, DBname)
        self.__MAC_UUID_table = RuntimeData(userDBMac, passwordDBMac, DBnameMac)
        self.__connector = libvirtConnector(libvirtConnector.KVM, self.__startedVM, self.__stoppedVM)
        VMClient.__connect()
            
    def __connect(self):
        self.__networkManager = NetworkManager()
        self.__networkManager.startNetworkService()
        self.__packetManager = VMServerPacketHandler(self.__networkManager)
        callback = self
        self.__networkManager.connectTo(serverIP, serverPort, listenPort, callback)

    def __startedVM(self, domain):
        # TODO: Añadir el PID a la base de datos

        self.__sendConnectionData(domain)
    
    def __getVNCaddress_port(self, domain):
        xml = ET.fromstring(domain.XMLDesc(0))
        graphic_element = xml.find('.//graphics')
        port = graphic_element.attrib['port']
        listen_element = graphic_element.find('.//listen')
        ip = listen_element.attrib['address']
        return ip, int(port)
    
    def __getVNCPassword(self, domain):
        xml = ET.fromstring(domain.XMLDesc(0))
        graphic_element = xml.find('.//graphics')
        password = graphic_element.attrib['passwd']
        return password
    
    def __sendConnectionData(self, domain):
        ip, port = self.__getVNCaddress_port(domain)
        password = self.__getVNCPassword(domain)
        packet = self.__packetManager.createVMConnectionParametersPacket(ip, port, password)
        self.__networkManager.sendPacket(serverPort, packet)
        
    def __stoppedVM(self, domain):
        if self.__waitForShutdown and (self.__connector.getNumberOfDomains == 0):
            self.__shutdown()
        # TODO: actualizar la base de datos
        (_ip, port) = self.__getVNCaddress_port(domain)
        pidToKill = self.__MAC_UUID_table.getVMPid(port)
        runCommand("kill " + pidToKill, VMClientException)
        
        self.__db.unRegisterVMResources(port)
    
    def __shutdown(self):
        # TODO: Destruir todos los dominios
        pass
        
    def processPacket(self, packet):
        packetType = self.__packetManager.readPacket(packet)
        processPacket = {
            VM_SERVER_PACKET_T.CREATE_DOMAIN: self.__createDomain, 
            VM_SERVER_PACKET_T.SERVER_STATUS_REQUEST: self.__serverStatusRequest,
            VM_SERVER_PACKET_T.USER_FRIENDLY_SHUTDOWN: self.__userFriendlyShutdown,
            VM_SERVER_PACKET_T.HALT: self.__halt}
        processPacket[packetType['packet_type']](packetType)

    def __createDomain(self, info):
        idVM = info["machineId"]
        userID = info["userId"]
        configFile = self.__db.getFileConfigPath(idVM)
        originalName = self.__db.getName(idVM)
        (osPath, dataPath) = self.__db.getImagePaths(idVM)
        
        # Calculo los nuevos parametros
        newUUID, newMAC = self.__getNewMAC_UUID()
        newName = originalName + newMAC
        newDataDisk = ExecutionImagePath + dataPath + ".qcow2"
        newOSDisk = ExecutionImagePath + osPath + ".qcow2"
        newPort = self.__getPort()
        newPassword = self.__getPassword()
        
        # Fichero de configuracion
        xmlFile = ConfigurationFileEditor(configFile)
        xmlFile.setDomainIdentifiers(newName, newUUID)
        xmlFile.setImagePaths(newOSDisk, newDataDisk)
        xmlFile.setNetworkConfiguration(VMClient.virtualNetwork, newMAC)
        xmlFile.setVNCServerConfiguration(serverIP, newPort, newPassword)
        
        # Copio las imagenes
        runCommand("cp "+ dataPath + " " + newDataDisk, VMClientException)
        runCommand("qemu-img create -b " + osPath + " -f qcow2 " + newOSDisk. VMClientException)
        
        # Inicio el websockify
        # Los puertos impares (por ejemplo) serán para KVM 
        # y los pares los websockets
        pidWS = runCommandBackground("python " + websockifyPath + " " 
                    + serverIP + ":" + newPort + " " 
                    + websocketServerIP + ":" + (newPort+1))
        # Actualizo la base de datos
        self.__MAC_UUID_table.registerVMresource(newPort, userID, idVM, pidWS, newDataDisk, newOSDisk, newMAC, newUUID, newPassword)
        
        self.__connector.startDomain(xmlFile.generateConfigurationString())
    
    def __serverStatusRequest(self, packet):
        activeDomains = self.__connector.getNumberOfDomains()
        packet = self.__packetManager.createVMServerStatusPacket(serverIP, activeDomains)
        self.__networkManager.sendPacket(serverPort, packet)
    
    def __userFriendlyShutdown(self, packet):
        self.__waitForShutdown = True
    
    def __halt(self, packet):
        # TODO:
        pass
    
    def __getNewMAC_UUID(self):
        return self.__MAC_UUID_table.extractfreeMac()
        
    def __getNewPort(self):
        return self.__MAC_UUID_table.extractfreeVNCPort()
        
    def __getNewPassword(self):
        return runCommand("openssl base64 -rand " + passwordLength, VMClientException)