# -*- coding: utf8 -*-
'''
Created on 14/01/2013

@author: saguma
'''

from network.manager import NetworkManager, NetworkCallback
from libvirtConnector import libvirtConnector
import libvirt
from Constantes import *
from packets import VM_SERVER_PACKET_T, VMServerPacketHandler
from xmlEditor import ConfigurationFileEditor
from database.VMServerDB.ImageManager import ImageManager
from database.VMServerDB.RuntimeData import RuntimeData
from virtualNetwork.VirtualNetworkManager import VirtualNetworkManager

from utils.commands import runCommand, runCommandBackground
from time import sleep

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
        # TODO: esto debe ejecutarse como root
        #self.__virtualNetwork = VirtualNetworkManager()
        #self.__virtualNetwork.createVirtualNetwork(VNName, gatewayIP, NetMask,
        #                            DHCPStartIP, DHCPEndIP)
        self.__connector = libvirtConnector(libvirtConnector.KVM, self.__startedVM, self.__stoppedVM)
        self.__connect()
            
    def __connect(self):
        self.__networkManager = NetworkManager()
        self.__networkManager.startNetworkService()
        self.__packetManager = VMServerPacketHandler(self.__networkManager)
        callback = self
        self.__networkManager.listenIn(listenPort, callback)

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
        xml = ET.fromstring(domain.XMLDesc(libvirt.VIR_DOMAIN_XML_SECURE))
        graphic_element = xml.find('.//graphics')
        print ET.tostring(graphic_element)
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
        configFile = ConfigFilePath + self.__db.getFileConfigPath(idVM)
        originalName = self.__db.getName(idVM)
        dataPath = self.__db.getImagePath(idVM)
        osPath = self.__db.getOsImagePath(idVM)
        
        # Calculo los nuevos parametros
        newUUID, newMAC = self.__getNewMAC_UUID()
        newPort = self.__getNewPort()
        newName = originalName + str(newPort)
        newDataDisk = ExecutionImagePath + dataPath + str(newPort) + ".qcow2"
        newOSDisk = ExecutionImagePath + osPath + str(newPort) + ".qcow2"
        newPassword = self.__getNewPassword()
        sourceDataDisk = SourceImagePath + dataPath
        sourceOSDisk = SourceImagePath + osPath        
        
        # Fichero de configuracion
        xmlFile = ConfigurationFileEditor(configFile)
        xmlFile.setDomainIdentifiers(newName, newUUID)
        xmlFile.setImagePaths(newOSDisk, newDataDisk)
        xmlFile.setNetworkConfiguration(VNName, newMAC)
        xmlFile.setVNCServerConfiguration(serverIP, newPort, newPassword)
                
        # Copio las imagenes
        runCommand("cd " + SourceImagePath + ";" + "cp --parents "+ dataPath + " " + ExecutionImagePath, VMClientException)
        runCommand("mv " + ExecutionImagePath + dataPath +" " + newDataDisk, VMClientException)
        runCommand("qemu-img create -b " + sourceOSDisk + " -f qcow2 " + newOSDisk, VMClientException)
        #runCommand("chmod -R 777 " + ExecutionImagePath, VMClientException)
        
        # Inicio el websockify
        # Los puertos impares (por ejemplo) serán para KVM 
        # y los pares los websockets
        pidWS = runCommandBackground("python " + websockifyPath + " " 
                    + serverIP + ":" + str(newPort) + " " 
                    + websocketServerIP + ":" + str(newPort+1))
        # Actualizo la base de datos
        self.__MAC_UUID_table.registerVMResources(newPort, userID, idVM, pidWS, newDataDisk, newOSDisk, newMAC, newUUID, newPassword)
        
        string = xmlFile.generateConfigurationString()
        print string
        
        self.__connector.startDomain(string)
    
    def __serverStatusRequest(self, packet):
        activeDomains = self.__connector.getNumberOfDomains()
        packet = self.__packetManager.createVMServerStatusPacket(serverIP, activeDomains)
        self.__networkManager.sendPacket(serverPort, packet)
    
    def __userFriendlyShutdown(self, packet):
        self.__waitForShutdown = True
    
    def __halt(self, packet):
        # TODO:
        self.__virtualNetwork.destroyVirtualNetwork(VNName)
        pass
    
    def __getNewMAC_UUID(self):
        return self.__MAC_UUID_table.extractfreeMacAndUuid()
        
    def __getNewPort(self):
        return self.__MAC_UUID_table.extractfreeVNCPort()
        
    def __getNewPassword(self):
        return runCommand("openssl rand -base64 " + str(passwordLength), VMClientException)
        
if __name__ == "__main__" :
    VMClient()
    while True :
        print "Running"
        sleep(1000)