# -*- coding: utf8 -*-
'''
Created on 14/01/2013

@author: saguma
'''

from network.manager.networkManager import NetworkManager
from virtualMachineServer.networking.callback import ClusterServerCallback
from virtualMachineServer.networking.packets import VM_SERVER_PACKET_T, VMServerPacketHandler
from database.vmServer.vmServerDB import VMServerDBConnector
from network.ftp.ftpClient import FTPClient
from virtualMachineServer.networking.reactors import MainServerPacketReactor
from virtualMachineServer.threads.fileTransferThread import FileTransferThread
from virtualMachineServer.threads.compressionThread import CompressionThread
from virtualMachineServer.exceptions.vmServerException import VMServerException
from virtualMachineServer.libvirtInteraction.domainHandler import DomainHandler
from ccutils.processes.childProcessManager import ChildProcessManager
from network.interfaces.ipAddresses import get_ip_address 
from virtualMachineServer.reactor.transfer_t import TRANSFER_T
import os
import multiprocessing
import sys

class VMServerReactor(MainServerPacketReactor):
    """
    Clase del reactor del servidor de máquinas virtuales
    """
    def __init__(self, constantManager):
        """
        Inicializa el estado del reactor, establece las conexiones con las bases de datos, arranca el conector de libvirt
        y empieza a atender las peticiones del servidor de máquinas virtuales.
        Argumentos:
            constantsManager: objeto del que se obtendrán los parámetros de configuración
        """        
        self.__finished = False
        self.__emergencyStop = False
        self.__fileTransferThread = None
        self.__compressionThread = None
        self.__networkManager = None
        self.__cManager = constantManager
        self.__ftp = FTPClient()        
        self.__mainServerCallback = ClusterServerCallback(self)
        self.__domainHandler = None
        self.__domainTimeout = 0
        try :
            self.__connectToDatabases(self.__cManager.getConstant("databaseName"), self.__cManager.getConstant("databaseUserName"), 
                                      self.__cManager.getConstant("databasePassword"), )
            self.__startListenning(self.__cManager.getConstant("vncNetworkInterface"), self.__cManager.getConstant("listenningPort"))
        except Exception as e:
            print e.message
            self.__emergencyStop = True
            self.__finished = True
        
    def __connectToDatabases(self, databaseName, user, password) :
        """
        Establece la conexión con la base de datos
        Argumentos:
            databaseName: el nombre de la base de datos
            user: el usuario a utilizar
            password: la contraseña a utilizar
        Devuelve:
            Nada
        """
        self.__dbConnector = VMServerDBConnector(user, password, databaseName)  
            
    def __startListenning(self, networkInterface, listenningPort):
        """
        Crea la conexión de red por la que se recibirán los comandos del servidor de cluster.
        """    
        try :
            self.__vncServerIP = get_ip_address(networkInterface)
        except Exception :
            raise Exception("Error: the network interface '{0}' is not ready. Exiting now".format(networkInterface))    
        self.__ftpTimeout = self.__cManager.getConstant("FTPTimeout")
        self.__listenningPort = listenningPort
        self.__networkManager = NetworkManager(self.__cManager.getConstant("certificatePath"))
        self.__networkManager.startNetworkService()
        self.__packetManager = VMServerPacketHandler(self.__networkManager)        
        self.__networkManager.listenIn(self.__listenningPort, self.__mainServerCallback, True)
        self.__fileTransferThread = FileTransferThread(self.__networkManager, self.__listenningPort, self.__packetManager,
                                                       self.__cManager.getConstant("TransferDirectory"),
                                                       self.__cManager.getConstant("FTPTimeout"), self.__dbConnector)
        self.__fileTransferThread.start()
        self.__connectToDatabases(self.__cManager.getConstant("databaseName"), self.__cManager.getConstant("databaseUserName"), self.__cManager.getConstant("databasePassword"))
            
        self.__domainHandler = DomainHandler(self.__dbConnector, self.__vncServerIP, self.__networkManager, self.__packetManager, self.__listenningPort, 
                                                 self.__cManager.getConstant("configFilePath"),
                                                 self.__cManager.getConstant("sourceImagePath"), self.__cManager.getConstant("executionImagePath"),
                                                 self.__cManager.getConstant("websockifyPath"), self.__cManager.getConstant("passwordLength"))
        self.__domainHandler.connectToLibvirt(self.__cManager.getConstant("vncNetworkInterface"), 
                                                  self.__cManager.getConstant("vnName"), self.__cManager.getConstant("gatewayIP"), 
                                                  self.__cManager.getConstant("netMask"), self.__cManager.getConstant("dhcpStartIP"), 
                                                  self.__cManager.getConstant("dhcpEndIP"), self.__cManager.getConstant("createVirtualNetworkAsRoot"))
            
        self.__domainHandler.doInitialCleanup()
        self.__compressionThread = CompressionThread(self.__cManager.getConstant("TransferDirectory"), self.__cManager.getConstant("sourceImagePath"),
                                                     self.__cManager.getConstant("configFilePath"),
                                                     self.__dbConnector, self.__domainHandler, self.__networkManager, self.__listenningPort, self.__packetManager)
        self.__compressionThread.start()
    
    def shutdown(self):
        """
        Apaga el servidor de máquinas virtuales.
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        @attention: Para que no se produzcan cuelgues en la red, este método DEBE llamarse desde el hilo 
        principal.
        """
        if (self.__networkManager != None) :
            self.__networkManager.stopNetworkService() # Dejar de atender peticiones inmediatamente
            
        if (self.__emergencyStop) :            
            self.__domainTimeout = 0
            
        self.__domainHandler.shutdown(self.__domainTimeout)                   
        
        if (self.__fileTransferThread != None) :
            self.__fileTransferThread.stop()
            self.__fileTransferThread.join()
        if (self.__compressionThread != None) :
            self.__compressionThread.stop()
            self.__compressionThread.join()
        sys.exit()              
        
    def processClusterServerIncomingPackets(self, packet):
        """
        Procesa un paquete enviado desde el servidor de cluster.
        Argumentos:
            packet: el paquete a procesar
        Devuelve:
            Nada
        """
        data = self.__packetManager.readPacket(packet)
        if (data["packet_type"] == VM_SERVER_PACKET_T.CREATE_DOMAIN) :
            self.__domainHandler.createDomain(data["MachineID"], data["UserID"], data["CommandID"])
        elif (data["packet_type"] == VM_SERVER_PACKET_T.SERVER_STATUS_REQUEST) :
            self.__sendStatusData()
        elif (data["packet_type"] == VM_SERVER_PACKET_T.USER_FRIENDLY_SHUTDOWN) :
            self.__domainTimeout = data["Timeout"]
            self.__finished = True
        elif (data["packet_type"] == VM_SERVER_PACKET_T.HALT) :
            self.__domainTimeout = 0
            self.__finished = True
        elif (data['packet_type'] == VM_SERVER_PACKET_T.QUERY_ACTIVE_VM_DATA) :
            self.__sendDomainsVNCConnectionData()
        elif (data['packet_type'] == VM_SERVER_PACKET_T.DESTROY_DOMAIN) :
            self.__domainHandler.destroyDomain(data["DomainID"])
        elif (data['packet_type'] == VM_SERVER_PACKET_T.QUERY_ACTIVE_DOMAIN_UIDS) :
            self.__sendActiveDomainUIDs()
        elif (data['packet_type'] == VM_SERVER_PACKET_T.IMAGE_EDITION) :
            self.__processImageEditionPacket(data)
        elif (data['packet_type'] == VM_SERVER_PACKET_T.DEPLOY_IMAGE) :
            self.__processDeployImagePacket(data)
        elif (data['packet_type'] == VM_SERVER_PACKET_T.DELETE_IMAGE) :
            self.__processDeleteImagePacket(data)
            
    def __processDeployImagePacket(self, data):
        """
        Procesa un paquete de despliegue de una imagen
        Argumentos:
            data: el paquete a procesar
        Devuelve:
            Nada
        """
        data.pop("packet_type")
        data["Transfer_Type"] = TRANSFER_T.DEPLOY_IMAGE
        self.__dbConnector.addToTransferQueue(data)
        
    def __processDeleteImagePacket(self, data):
        
        isBootable = self.__dbConnector.getBootableFlag(data["ImageID"])
        
        if(isBootable):            
            osImagePath = os.path.join(self.__cManager.getConstant("sourceImagePath") 
                                   ,self.__dbConnector.getOSImagePath(data["ImageID"]))
            definitionFilePath = os.path.join(self.__cManager.getConstant("configFilePath") 
                                   ,self.__dbConnector.getDefinitionFilePath(data["ImageID"]))
            
            try :
                
                self.__dbConnector.deleteImage(data["ImageID"])                
                ChildProcessManager.runCommandInForeground("rm -rf " + os.path.dirname(osImagePath), VMServerException)                
                ChildProcessManager.runCommandInForeground("rm -rf " + os.path.dirname(definitionFilePath), VMServerException)
                p = self.__packetManager.createConfirmationPacket(VM_SERVER_PACKET_T.IMAGE_DELETED, data["ImageID"], data["CommandID"])
            except Exception as e:
                p = self.__packetManager.createErrorPacket(VM_SERVER_PACKET_T.IMAGE_DELETION_ERROR, "Can't delete image: internal error ({0})".format(e.message), 
                                                            data["CommandID"])                
            
        else:
            if (isBootable != None) :
                errorMessage = "The image is being edited, so it cannot be deleted"
            else :
                errorMessage = "The image {0} does not exist".format(data["ImageID"])
            
            p = self.__packetManager.createErrorPacket(VM_SERVER_PACKET_T.IMAGE_DELETION_ERROR, errorMessage, 
                                                       data["CommandID"])
        
        self.__networkManager.sendPacket('', self.__listenningPort, p)
            
        
        
    def __processImageEditionPacket(self, data):
        """
        Procesa un paquete de edición de una imagen.
        Argumentos:
            data: el paquete a procesar
        Devuelve:
            Nada
        """
        data.pop("packet_type")
        if (data["Modify"]) :
            data["Transfer_Type"] = TRANSFER_T.EDIT_IMAGE
        else :
            data["Transfer_Type"] = TRANSFER_T.CREATE_IMAGE
        data.pop("Modify")
        self.__dbConnector.addToTransferQueue(data)

    def __sendDomainsVNCConnectionData(self):
        '''
        Envía al servidor de cluster los datos de conexion de todas las máquinas virtuales
        que estén arrancadas
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        '''
        # Extraer los datos de la base de datos
        vncConnectionData = self.__dbConnector.getDomainsConnectionData()
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
    
    def __sendStatusData(self):
        """
        Recopila la información de estado del servidor de máquinas virtuales y se la envía al servidor de cluster.
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        """
        info = self.__domainHandler.getLibvirtStatusInfo()
        realCPUNumber = multiprocessing.cpu_count()
        diskStats_storage = os.statvfs(self.__cManager.getConstant("sourceImagePath"))
        diskStats_temporaryData = os.statvfs(self.__cManager.getConstant("executionImagePath"))
        freeOutput = ChildProcessManager.runCommandInForeground("free -k", VMServerException)
        
        # free devuelve la siguiente salida
        #              total       used       free     shared    buffers     cached
        # Mem:    4146708480 3939934208  206774272          0  224706560 1117671424
        # -/+ buffers/cache: 2597556224 1549152256
        # Swap:   2046816256   42455040 2004361216
        #
        # Cogemos la tercera línea
           
        availableMemory = int(freeOutput.split("\n")[1].split()[1])
        freeMemory = int(freeOutput.split("\n")[2].split()[2])
        freeStorageSpace = diskStats_storage.f_bfree * diskStats_storage.f_frsize / 1024
        availableStorageSpace = diskStats_storage.f_bavail * diskStats_storage.f_frsize / 1024
        freeTemporaryStorage = diskStats_temporaryData.f_bfree * diskStats_temporaryData.f_frsize / 1024
        availableTemporaryStorage = diskStats_temporaryData.f_bavail * diskStats_temporaryData.f_frsize / 1024
        packet = self.__packetManager.createVMServerStatusPacket(self.__vncServerIP, info["#domains"], freeMemory, availableMemory, 
                                                                 freeStorageSpace, availableStorageSpace, 
                                                                 freeTemporaryStorage, availableTemporaryStorage,
                                                                 info["#vcpus"], realCPUNumber)
        self.__networkManager.sendPacket('', self.__listenningPort, packet)   
    
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
    
    def has_finished(self):
        """
        Indica si el servidor de máquinas virtuales se ha apagado o no.
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        """
        return self.__finished   