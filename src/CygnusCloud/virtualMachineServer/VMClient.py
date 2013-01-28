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
from database.vmServer.imageManager import ImageManager
from database.vmServer.runtimeData import RuntimeData
from virtualNetwork.VirtualNetworkManager import VirtualNetworkManager

from utils.commands import runCommand, runCommandInBackground
from time import sleep
import os

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
        packet = self.__packetManager.createVMConnectionParametersPacket(ip, port + 1, password)
        self.__networkManager.sendPacket(serverPort, packet)
        
    def __stoppedVM(self, domainInfo):
        if self.__waitForShutdown and (self.__connector.getNumberOfDomains == 0):
            self.__shutdown()

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
    
    def __shutdown(self):
        # Cosas a hacer cuando se desea apagar el servidor
        #self.__virtualNetwork.destroyVirtualNetwork(VNName)
        pass
        
    def processPacket(self, packet):
        packetType = self.__packetManager.readPacket(packet)
        print "paquete recibido " + str(packetType['packet_type'])
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
        
        # Preparo los archivos
                
        # Compruebo si ya existe alguno de los archivos
        if (os.path.exists(newDataDisk)):
            print("The file " + newDataDisk + " already exist")
            return
        if (os.path.exists(newOSDisk)):
            print("The file " + newOSDisk + " already exist")
            return
        # Copio las imagenes
        runCommand("cd " + SourceImagePath + ";" + "cp --parents "+ dataPath + " " + ExecutionImagePath, VMClientException)
        runCommand("mv " + ExecutionImagePath + dataPath +" " + newDataDisk, VMClientException)
        runCommand("qemu-img create -b " + sourceOSDisk + " -f qcow2 " + newOSDisk, VMClientException)
        #runCommand("chmod -R 777 " + ExecutionImagePath, VMClientException)
        
        # Fichero de configuracion
        xmlFile = ConfigurationFileEditor(configFile)
        xmlFile.setDomainIdentifiers(newName, newUUID)
        xmlFile.setImagePaths(newOSDisk, newDataDisk)
        xmlFile.setNetworkConfiguration(VNName, newMAC)
        xmlFile.setVNCServerConfiguration(serverIP, newPort, newPassword)
        
        string = xmlFile.generateConfigurationString()
        
        # Arranco la máquina
        self.__connector.startDomain(string)
        
        # Inicio el websockify
        # Los puertos impares (por ejemplo) serán para KVM 
        # y los pares los websockets
        pidWS = runCommandInBackground([websockifyPath,
                    websocketServerIP + ":" + str(newPort + 1),
                    serverIP + ":" + str(newPort)])
        
        # Actualizo la base de datos
        self.__runningImageData.registerVMResources(newName, newPort, userID, idVM, pidWS, newDataDisk, newOSDisk, newMAC, newUUID, newPassword)
        
    
    def __serverStatusRequest(self, packet):
        activeDomains = self.__connector.getNumberOfDomains()
        packet = self.__packetManager.createVMServerStatusPacket(serverIP, activeDomains)
        self.__networkManager.sendPacket(serverPort, packet)
    
    def __userFriendlyShutdown(self, packet):
        self.__waitForShutdown = True
    
    def __halt(self, packet):
        # Destruyo los dominios
        self.__connector.stopAllDomain()
        self.__shutdown()
    
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