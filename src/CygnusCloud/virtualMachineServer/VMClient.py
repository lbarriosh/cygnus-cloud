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
from database.VMServerDB.ImageManager import ImageManager
from database.VMServerDB.RuntimeData import RuntimeData
from virtualNetwork.VirtualNetworkManager import VirtualNetworkManager

from utils.commands import runCommand, runCommandBackground
from time import sleep

class VMClientException(Exception):
    pass

class VMClient(NetworkCallback):
    def __init__(self):
        self.__waitForShutdown = False
        self.__db = ImageManager(userDB, passwordDB, DBname)
        self.__runningImageData = RuntimeData(userDBMac, passwordDBMac, DBnameMac)
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
        self.__sendConnectionData(domain)
    
    def __sendConnectionData(self, domainInfo):
        ip = domainInfo["VNCip"]
        port = domainInfo["VNCport"]
        password = domainInfo["VNCpassword"]
        packet = self.__packetManager.createVMConnectionParametersPacket(ip, port+1, password)
        self.__networkManager.sendPacket(serverPort, packet)
        
    def __stoppedVM(self, domainInfo):
        if self.__waitForShutdown and (self.__connector.getNumberOfDomains == 0):
            self.__shutdown()

        name = domainInfo["name"]
        dataPath = self.__runningImageData.getMachineDataPath(name)
        osPath = self.__runningImageData.getOsImagePath(name)
        pidToKill = self.__runningImageData.getVMPid(name)
        
        # Delete the virtual machine images disk
        runCommand("rm " + dataPath, VMClientException)
        runCommand("rm " + osPath, VMClientException)
        
        # Kill websockify process
        runCommand("kill " + str(pidToKill), VMClientException)
        
        # Update the database
        self.__runningImageData.unRegisterVMResources(name)
    
    def __shutdown(self):
        # TODO: Destruir todos los dominios
        pass
        
    def processPacket(self, packet):
        print "paquete recibido"
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
        pidWS = 0
        #pidWS = runCommandBackground("python " + websockifyPath + " " 
        #            + websocketServerIP + ":" + str(newPort + 1) + " " 
        #            + serverIP + ":" + str(newPort))
        # Actualizo la base de datos
        self.__runningImageData.registerVMResources(newPort, userID, idVM, pidWS, newDataDisk, newOSDisk, newMAC, newUUID, newPassword)
        
        string = xmlFile.generateConfigurationString()
        
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
        return self.__runningImageData.extractfreeMacAndUuid()
        
    def __getNewPort(self):
        return self.__runningImageData.extractfreeVNCPort()
        
    def __getNewPassword(self):
        return runCommand("openssl rand -base64 " + str(passwordLength), VMClientException)
        
if __name__ == "__main__" :
    VMClient()
    while True :
        print "Running"
        sleep(1000)