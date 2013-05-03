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
from virtualMachineServer.reactor.transfer_t import TRANSFER_T
from os import path, listdir

from time import sleep

class DomainHandler(object):
    """
    Clase del gestor de dominios. Estos objetos interactúan con libvirt para manipular dominios.
    """
    
    def __init__(self, dbConnector, vncServerIP, networkManager, packetManager, listenningPort, definitionFileDirectory,
                 sourceImageDirectory, executionImageDirectory, websockifyPath, vncPasswordLength, compressionQueue, imageRepositoryConnectionData):
        """
        Inicializa el estado del gestor de dominios
        Argumentos:
            dbConnector: conector con la base de datos del servidor de máquinas virtuales
            vncServerIP: la dirección IP del servidor VNC
            networkManager: gestor de red. Se usará para enviar los datos de conexión a los clientes.
            packetManager: gestor de paquetes. Se usará para enviar los datos de conexión a los clientes.
            listenningPort: el peurto en el que escucha el servidor de máquinas virtuales
            definitionFileDirectory: el directorio en el que se encuentran los ficheros de definición de las máquinas
            sourceImageDirectory: el directorio en el que se almacenan las imágenes de disco de las máquinas virtuales
            executionImageDirectory: el directorio en el que se almacenan las imágenes temporales de las máquinas virtuales
            websockifyPath: la ruta del binario websockify
            vncPasswordLength: la longitud de la contraseña del servidor VNC
            compressionQueue: la longitud de la cola de compresión
            imageRepositoryConnectionData: diccionario con los datos de conexión al repositorio
        """
        self.__dbConnector = dbConnector        
        self.__vncServerIP = vncServerIP
        self.__childProcessManager = ChildProcessManager()        
        self.__networkManager = networkManager
        self.__packetManager = packetManager
        self.__listenningPort = listenningPort
        self.__definitionFileDirectory = definitionFileDirectory
        self.__sourceImagePath = sourceImageDirectory
        self.__executionImagePath = executionImageDirectory
        self.__websockifyPath = websockifyPath
        self.__vncPasswordLength = vncPasswordLength
        self.__libvirtConnection = None
        self.__virtualNetworkManager = None
        self.__virtualNetworkName = None
        self.__compressionQueue = compressionQueue
        self.__editedImagesData = imageRepositoryConnectionData
    
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
        """
        Detiene los dominios activos.
        Argumentos:
            timeout: el número de segundos que se esperará antes de destruir todos
            los dominios.
        Devuelve:
            Nada
        """
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
        """
        Crea un dominio
        Argumentos:
            imageID: el identificador único de la imagen a usar
            userID: el identificador único del propietario de la nueva máquina virtual
            commandID: el identificador único del comando de arranque de la nueva máquina virtual
        Devuelve:
            Nada
        """
        definitionFile = self.__definitionFileDirectory + self.__dbConnector.getDefinitionFilePath(imageID)
        originalName = "{0}_".format(imageID)
        dataImagePath = self.__dbConnector.getDataImagePath(imageID)
        osImagePath = self.__dbConnector.getOSImagePath(imageID)
        isBootable = self.__dbConnector.getBootableFlag(imageID)        
           
        
        # Obtengo los parámetros de configuración de la máquina virtual
        newUUID, newMAC = self.__dbConnector.extractFreeMACAndUUID()
        newPort = self.__dbConnector.extractFreeVNCPort()
        newName = originalName + str(newPort)        
        newPassword = self.__generateVNCPassword()
        sourceOSDisk = self.__sourceImagePath + osImagePath                
        
        # Preparo los archivos
        
        if(isBootable):                           
            # Saco el nombre de los archivos (sin la extension)
            trimmedDataImagePath = dataImagePath
            try:
                trimmedDataImagePath = dataImagePath[0:dataImagePath.index(".qcow2")]
            except:
                pass
            trimmedOSImagePath = osImagePath
            try:
                trimmedOSImagePath = osImagePath[0:osImagePath.index(".qcow2")]
            except:
                pass   
            
            newDataDisk = self.__executionImagePath + trimmedDataImagePath + str(newPort) + ".qcow2"
            newOSDisk = self.__executionImagePath + trimmedOSImagePath + str(newPort) + ".qcow2"
                
            # Compruebo si ya existe alguno de los archivos. Si es el caso, me los cargo
            if (path.exists(newDataDisk)):
                print("Warning: the file " + newDataDisk + " already exists")
                ChildProcessManager.runCommandInForeground("rm " + newDataDisk, VMServerException)
            
            if (path.exists(newOSDisk)):
                print("Warning: the file " + newOSDisk + " already exists")
                ChildProcessManager.runCommandInForeground("rm " + newOSDisk, VMServerException)
            
            # Copio las imagenes
            ChildProcessManager.runCommandInForeground("cd " + self.__sourceImagePath + ";" + "cp --parents "+ dataImagePath + " " + self.__executionImagePath, VMServerException)
            ChildProcessManager.runCommandInForeground("mv " + self.__executionImagePath + dataImagePath +" " + newDataDisk, VMServerException)
            ChildProcessManager.runCommandInForeground("qemu-img create -b " + sourceOSDisk + " -f qcow2 " + newOSDisk, VMServerException)
        
        else :
            newDataDisk = path.join(self.__sourceImagePath, dataImagePath)
            newOSDisk = path.join(self.__sourceImagePath, osImagePath)            
        
        # Genero el fichero de definición
        xmlFile = ConfigurationFileEditor(definitionFile)
        xmlFile.setDomainIdentifiers(newName, newUUID)
        xmlFile.setImagePaths(newOSDisk, newDataDisk)            
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
        dataImagePath = self.__dbConnector.getDomainDataImagePath(domainName)
        osImagePath = self.__dbConnector.getDomainOSImagePath(domainName)   
        websockify_pid = self.__dbConnector.getWebsockifyDaemonPID(domainName)
        imageID = self.__dbConnector.getDomainImageID(domainName)
        isBootable = self.__dbConnector.getBootableFlag(imageID)        
        commandID = self.__dbConnector.getVMBootCommand(domainName)
        
        try :
            ChildProcessManager.runCommandInForeground("kill -s TERM " + str(websockify_pid))
        except Exception:
            pass    
        
        self.__dbConnector.unregisterDomainResources(domainName)     
        
        if isBootable :
            ChildProcessManager.runCommandInForeground("rm " + dataImagePath, VMServerException)
            ChildProcessManager.runCommandInForeground("rm " + osImagePath, VMServerException)
            dataDirectory = path.dirname(dataImagePath)
            osDirectory = path.dirname(osImagePath)
            if (listdir(dataDirectory) == []) :
                ChildProcessManager.runCommandInForeground("rm -rf " + dataDirectory, VMServerException)
            if (osDirectory != dataDirectory and listdir(osDirectory) == []) :
                ChildProcessManager.runCommandInForeground("rm -rf " + osDirectory, VMServerException)            
                    
        else :
            data = dict()            
            connectionData = self.__editedImagesData[commandID]
            data["Transfer_Type"] = TRANSFER_T.STORE_IMAGE
            data["DataImagePath"] = dataImagePath
            data["OSImagePath"] = osImagePath
            data["DefinitionFilePath"] = self.__dbConnector.getDefinitionFilePath(imageID)
            data["RepositoryIP"] = connectionData["RepositoryIP"]
            data["RepositoryPort"] = connectionData["RepositoryPort"]
            data["CommandID"] = commandID            
            data["TargetImageID"] = imageID
            self.__compressionQueue.queue(data)
            self.__editedImagesData.pop(commandID)
            self.__dbConnector.deleteImage(imageID)              
    
    def __waitForDomainsToTerminate(self, timeout):
        """
        Espera a que todos los dominios activos terminen o a que transcurran timeout segundos,
        lo que suceda antes.
        """
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