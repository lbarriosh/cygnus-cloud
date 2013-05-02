# -*- coding: utf8 -*-
'''
Created on Apr 29, 2013

@author: luis
'''

from virtualMachineServer.virtualNetwork.virtualNetworkManager import VirtualNetworkManager
from ccutils.processes.childProcessManager import ChildProcessManager
from virtualMachineServer.libvirtInteraction.libvirtConnector import LibvirtConnector
from virtualMachineServer.exceptions.vmServerException import VMServerException
from virtualMachineServer.libvirtInteraction.xmlEditor import ConfigurationFileEditor
from os import path, listdir

from time import sleep

class DomainHandler(object):
    
    def __init__(self, dbConnector, vncServerIP, networkManager, packetManager, listenningPort, definitionFileDirectory,
                 sourceImagePath, executionImagePath, websockifyPath, vncPasswordLength):
        self.__dbConnector = dbConnector        
        self.__vncServerIP = vncServerIP
        self.__childProcessManager = ChildProcessManager()        
        self.__networkManager = networkManager
        self.__packetManager = packetManager
        self.__listenningPort = listenningPort
        self.__definitionFileDirectory = definitionFileDirectory
        self.__sourceImagePath = sourceImagePath
        self.__executionImagePath = executionImagePath
        self.__websockifyPath = websockifyPath
        self.__vncPasswordLength = vncPasswordLength
        self.__libvirtConnection = None
        self.__virtualNetworkManager = None
        self.__virtualNetworkName = None
    
    def connectToLibvirt(self, networkInterface, virtualNetworkName, gatewayIP, netmask, 
                         dhcpStartIP, dhcpEndIP, createVirtualNetworkAsRoot) :
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
        self.__virtualNetworkManager.createVirtualNetwork(virtualNetworkName, gatewayIP, 
                                                          netmask, dhcpStartIP, 
                                                          dhcpEndIP)
        self.__virtualNetworkName = virtualNetworkName
    
    def doInitialCleanup(self):
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
        
    def shutdown(self, timeout):
        if (self.__libvirtConnection != None) :
            if (timeout == 0) :
                self.__libvirtConnection.destroyAllDomains()
            else :
                self.__waitForDomainsToTerminate(timeout)
        try :
            self.__virtualNetworkManager.destroyVirtualNetwork(self.__virtualNetworkName)  
        except Exception:
            pass
        self.__childProcessManager.waitForBackgroundChildrenToTerminate()
        
    def createDomain(self, imageID, userID, commandID):
        configFile = self.__definitionFileDirectory + self.__dbConnector.getDefinitionFilePath(imageID)
        originalName = "{0}_".format(imageID)
        dataPath = self.__dbConnector.getDataImagePath(imageID)
        osPath = self.__dbConnector.getOSImagePath(imageID)
        isBootable = self.__dbConnector.getBootableFlag(imageID)
        
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
        newDataDisk = self.__executionImagePath + trimmedDataImagePath + str(newPort) + ".qcow2"
        newOSDisk = self.__executionImagePath + trimmedOSImagePath + str(newPort) + ".qcow2"
        newPassword = self.__generateVNCPassword()
        sourceOSDisk = self.__sourceImagePath + osPath    
            
        
        # Preparo los archivos
        
        if(isBootable):        
            # Compruebo si ya existe alguno de los archivos. Si es el caso, me los cargo
            if (path.exists(newDataDisk)):
                print("Warning: the file " + newDataDisk + " already exists")
                ChildProcessManager.runCommandInForeground("rm " + newDataDisk, VMServerException)
            
            if (path.exists(newOSDisk)):
                print("Warning: the file " + newOSDisk + " already exists")
                ChildProcessManager.runCommandInForeground("rm " + newOSDisk, VMServerException)
            
            # Copio las imagenes
            ChildProcessManager.runCommandInForeground("cd " + self.__sourceImagePath + ";" + "cp --parents "+ dataPath + " " + self.__executionImagePath, VMServerException)
            ChildProcessManager.runCommandInForeground("mv " + self.__executionImagePath + dataPath +" " + newDataDisk, VMServerException)
            ChildProcessManager.runCommandInForeground("qemu-img create -b " + sourceOSDisk + " -f qcow2 " + newOSDisk, VMServerException)
        
        # Genero el fichero de definición
        xmlFile = ConfigurationFileEditor(configFile)
        xmlFile.setDomainIdentifiers(newName, newUUID)
        # Elegimos la ruta del fichero a utilizar
        if(isBootable):
            xmlFile.setImagePaths(newOSDisk, newDataDisk)
        else:
            xmlFile.setImagePaths(self.__sourceImagePath + osPath,self.__sourceImagePath +  dataPath)
            
        xmlFile.setVirtualNetworkConfiguration(self.__virtualNetworkName, newMAC)
        xmlFile.setVNCServerConfiguration(self.__vncServerIP, newPort, newPassword)
        
        string = xmlFile.generateConfigurationString()
        
        # Arranco la máquina
        self.__libvirtConnection.startDomain(string)
        
        # Inicio el demonio websockify
        # Los puertos impares serán para el socket que proporciona el hipervisor 
        # y los pares los websockets generados por websockify        
        
        webSockifyPID = self.__childProcessManager.runCommandInBackground([self.__websockifyPath,
                                    self.__vncServerIP + ":" + str(newPort + 1),
                                    self.__vncServerIP + ":" + str(newPort)])
        
        self.__dbConnector.registerVMResources(newName, imageID, newPort, newPassword, userID, webSockifyPID, newOSDisk,  newDataDisk, newMAC, newUUID)
        self.__dbConnector.addVMBootCommand(newName, commandID)
        
    def destroyDomain(self, domainUID):
        """
        Destruye una máquina virtual por petición explícita de su propietario.
        Argumentos:
            packet: un diccionario con los datos del paquete de destrucción
        Devuelve:
            Nada
        """
        domainName = self.__dbConnector.getDomainNameFromVMBootCommand(domainUID)
        if (domainName == None) :
            # No informamos del error: el servidor de máquinas virtuales siempre intenta
            # hacer lo que se le pide, y si no puede, no lo hace y no se queja.
            return 
        self.__libvirtConnection.destroyDomain(domainName)
        # Libvirt borra las imágenes de disco, por lo que sólo tenemos que encargarnos de actualizar
        # las bases de datos.
        self.__freeDomainResources(domainName, False)
        
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
        imageID = self.__dbConnector.getDomainImageID(domainName)
        isBootable = self.__dbConnector.getBootableFlag(imageID)
        definitionPath = self.__dbConnector.getDefinitionFilePath(imageID)
        
        try :
            ChildProcessManager.runCommandInForeground("kill -s TERM " + str(websockify_pid))
        except Exception:
            pass    
        
        if deleteDiskImages and isBootable:
            ChildProcessManager.runCommandInForeground("rm " + dataPath, VMServerException)
            ChildProcessManager.runCommandInForeground("rm " + osPath, VMServerException)
            dataDirectory = path.dirname(dataPath)
            osDirectory = path.dirname(osPath)
            if (listdir(dataDirectory) == []) :
                ChildProcessManager.runCommandInForeground("rm -rf " + dataDirectory, VMServerException)
            if (osDirectory != dataDirectory and listdir(osDirectory) == []) :
                ChildProcessManager.runCommandInForeground("rm -rf " + osDirectory, VMServerException)
                
            self.__dbConnector.unregisterDomainResources(domainName)    
        
        # si no es bootable añadimos el mensaje a la cola de compresion
        # Añadimos el fichero a la cola de compresión/descompresión
        if(not isBootable):
            data = dict()
            data["Retrieve"] = False
            data["DataPath"] = dataPath
            data["OSPath"] = osPath
            data["DefinitionPath"] = definitionPath 
            self.__compressionQueue.queue(data)
    
    def __waitForDomainsToTerminate(self, timeout):
        wait_time = 0
        while (self.__libvirtConnection.getNumberOfDomains() != 0 and wait_time < timeout) :
            sleep(0.5)
            wait_time += 0.5
            
    def __generateVNCPassword(self):
        """
        Genera una contraseña para un servidor VNC
        Argumentos:
            Ninguno
        Devuelve:
            Un string con la contraseña generada
        """
        return ChildProcessManager.runCommandInForeground("openssl rand -base64 " + str(self.__vncPasswordLength), VMServerException)