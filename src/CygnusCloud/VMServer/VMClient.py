'''
Created on 14/01/2013

@author: saguma
'''

from network.manager import NetworkManager, NetworkCallback
from libvirtManager import libvirtConnector
from VMServer.Constantes import *
from packets.types import VM_SERVER_PACKET_T
from database.VMServerDB import ImageManager, RuntimeData
from utils.commands import runCommand, runCommandBackground
from xml.etree import ElementTree as ET

class VMClientException(Exception):
    pass

class VMClient(NetworkCallback):
    def __init__(self):
        # Diccionario que relaciona un id de un dominio 
        # con el PID de su correspondiente websockify
        self.ID_PIDWS = {}
        self.__waitForShutdown = False
        self.db = ImageManager(userDB, passwordDB, DBname)
        self.MAC_UUID_table = RuntimeData(userDBMac, passwordDBMac, DBnameMac)
        self.connector = libvirtConnector(libvirtConnector.KVM, self.__startedVM, self.__stoppedVM)
        VMClient.__connect()
            
    def __connect(self):
        self.networkManager = NetworkManager()
        self.networkManager.startNetworkService()
        callback = self
        self.networkManager.connectTo(serverIP, serverPort, listenPort, callback)

    def __startedVM(self, domain):
        ip, port = self.__getVNCaddress_port(domain)
        # Los puertos impares (por ejemplo) serán para KVM 
        # y los pares los websockets
        if (ip is None):
            ip = "127.0.0.1" 
        pidWS = runCommandBackground("python " + websockifyPath + " " 
                    + ip + ":" + port + " " 
                    + websocketServerIP + ":" + (port+1))
        # TODO: Añadirle al diccionario ID_PIDWS
        self.ID_PIDWS[domain.getID()] = pidWS
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
        dataPacket = self.networkManager.createPacket(ConnectionDataPriority)
        dataPacket.writeInt(VM_SERVER_PACKET_T.CONNECTION_DATA)
        ip, port = self.__getVNCaddress_port(domain)
        password = self.__getVNCPassword(domain)
        dataPacket.writeString(ip)
        dataPacket.writeInt(port+1)
        dataPacket.writeString(password)
        
    def __stoppedVM(self, domain):
        if self.__waitForShutdown and (self.connector.getNumberOfDomains == 0):
            self.__shutdown()
        pidToKill = self.ID_PIDWS[domain.getID()]
        runCommand("kill " + pidToKill, VMClientException)
    
    def __shutdown(self):
        # TODO:
        pass
        
    def processPacket(self, packet):
        processPacket = {
            VM_SERVER_PACKET_T.CREATE_DOMAIN: self.__createDomain, 
            VM_SERVER_PACKET_T.SERVER_STATUS_REQUEST: self.__serverStatusRequest,
            VM_SERVER_PACKET_T.USER_FRIENDLY_SHUTDOWN: self.__userFriendlyShutdown,
            VM_SERVER_PACKET_T.HALT: self.__halt}
        processPacket[VM_SERVER_PACKET_T.reverse_mapping[packet.readInt()]](packet)

    def __createDomain(self, packet):
        idVM = packet.readInt()
        configFile = self.db.getFileConfigPath(idVM)
        originalName = self.db.getName(idVM)
        
        # Calculo los nuevos parametros
        newUUID, newMAC = self.__getNewMAC_UUID()
        newName = originalName + newMAC
        newFileDisk = ExecutionImagePath + newName + ".vmdk"
        newPort = self.__getPort()
        newPassword = self.__getPassword()
        
        # TODO: Redirigir la salida estandar para leer el xml
        
        # Supongo que la variable "xml" contiene el xml
        # TODO: cambiar el puerto en la configuracion  y la contraseña
        #        (voto por modificar virt-clone (está escrito en python) 
        #        y añadir la opcion de cambiar puerto)
        xmlText = runCommand("virt-clone --original-xml=" + configFile +
                   " -u " + newUUID + " -m " + newMAC + " -n " + newName + 
                   " -f " + newFileDisk + " --print-xml")
        
        # Añado el puerto y la contraseña en el xml
        xml = ET.fromstring(xmlText)
        GE = xml.find('.//graphics')
        GE.attrib['port'] = str(newPort)
        GE.attrib['passwd'] = newPassword
        xmlText = ET.tostring(xml)
        self.connector.startDomain(xmlText)
    
    def __serverStatusRequest(self, packet):
        statusPacket = self.networkManager.createPacket(7)
        statusPacket.writeInt(VM_SERVER_PACKET_T.SERVER_STATUS)
        statusPacket.writeInt(self.connector.getNumberOfDomains())
    
    def __userFriendlyShutdown(self, packet):
        self.__waitForShutdown = True
    
    def __halt(self, packet):
        # TODO:
        pass
    
    def __getNewMAC_UUID(self):
        return self.MAC_UUID_table.extractfreeMac()
        
    def __getNewPort(self):
        # TODO: Conseguir puertos ¿como las macs?
        return 15000
        
    def __getNewPassword(self):
        # TODO: Conseguir passwords aleatorios
        return "Generad contraseñas aleatorias"