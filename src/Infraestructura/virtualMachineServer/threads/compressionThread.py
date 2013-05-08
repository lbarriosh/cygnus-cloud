# -*- coding: utf8 -*-
'''
Created on Apr 28, 2013

@author: luis
'''

from ccutils.threads import BasicThread
from ccutils.compression.zipBasedCompressor import ZipBasedCompressor
from virtualMachineServer.exceptions.vmServerException import VMServerException
from os import path, listdir, makedirs
import shutil
from ccutils.processes.childProcessManager import ChildProcessManager
from virtualMachineServer.reactor.transfer_t import TRANSFER_T
from virtualMachineServer.networking.packets import VM_SERVER_PACKET_T
from time import sleep

class CompressionThread(BasicThread):
    """
    Clase del hilo de descompresión y compresión de ficheros
    """
    
    def __init__(self, transferDirectory, workingDirectory, definitionFileDirectory, dbConnector, domainHandler,
                 networkManager, serverListenningPort, packetHandler):
        """
        Inicializa el estado del hilo
        Argumentos:
            transferDirectory: el directorio de trabajo del hilo de transferencias
            workingDirectory: el directorio en el que se almacenan las imágenes de disco
            definitionFileDirectory: el directorio en el que se almacenan los ficheros de definición de las máquinas
            dbConnector: conector con la base de datos
            domainHandler: objeto que interactúa con libvirt para manipular máquinas virtuales
            único de la máquina virtual
        """
        BasicThread.__init__(self, "File compression thread")
        self.__workingDirectory = workingDirectory
        self.__transferDirectory = transferDirectory
        self.__definitionFileDirectory = definitionFileDirectory
        self.__dbConnector = dbConnector
        self.__domainHandler = domainHandler
        self.__compressor = ZipBasedCompressor()
        self.__networkManager = networkManager
        self.__serverListenningPort = serverListenningPort
        self.__packetHandler = packetHandler
        
    def run(self):
        while not self.finish() :
            data = self.__dbConnector.peekFromCompressionQueue()
            if (data == None):
                sleep(0.5)
            else:
                self.__processElement(data)
                self.__dbConnector.removeFirstElementFromCompressionQueue()

        
    def __processElement(self, data):
        """
        Procesa una petición de compresión o descompresión.
        Argumentos:
            data: diccionario con los datos de la petición a procesar
        Devuelve:
            Nada
        """        
        try :
            
            if(data["Transfer_Type"] != TRANSFER_T.STORE_IMAGE):            
                if (data["Transfer_Type"] == TRANSFER_T.EDIT_IMAGE) :
                    # Borramos la imagen de la base de datos (si existe)
                    self.__dbConnector.deleteImage(data["SourceImageID"])
                    
                # Extraemos el fichero en el directorio que alberga las imágenes
                imageDirectory = path.join(self.__workingDirectory, str(data["TargetImageID"]))
                # Cambiamos los permisos de los ficheros y buscamos el fichero de definición
                definitionFileDirectory = path.join(self.__definitionFileDirectory, str(data["TargetImageID"]))            
                
                try :
                    ChildProcessManager.runCommandInForeground("rm -rf " + imageDirectory, Exception)
                    ChildProcessManager.runCommandInForeground("rm -rf " + definitionFileDirectory, Exception)
                except Exception:
                    pass
                compressedFilePath = path.join(self.__transferDirectory, str(data["SourceImageID"]) + ".zip")
                self.__compressor.extractFile(compressedFilePath, imageDirectory)            
                
                
                
                # Creamos el directorio de definicion en el caso de que no exista
                if not path.exists(definitionFileDirectory):
                    makedirs(definitionFileDirectory)
            
                definitionFileFound = False
                for fileName in listdir(imageDirectory):
                    ChildProcessManager.runCommandInForegroundAsRoot("chmod 666 " + path.join(imageDirectory, fileName), VMServerException)
                    if fileName.endswith(".xml"):
                        # movemos el fichero al directorio
                        definitionFile = fileName
                        shutil.move(path.join(imageDirectory, fileName), definitionFileDirectory)
                        definitionFileFound = True
                if(not definitionFileFound):
                    raise Exception("The definition file was not found")
    
                # Registramos la máquina virtual
                self.__dbConnector.createImage(data["TargetImageID"], path.join(str(data["TargetImageID"]), "OS.qcow2"),
                                               path.join(str(data["TargetImageID"]), "Data.qcow2"),
                                               path.join(str(data["TargetImageID"]), definitionFile), data["Transfer_Type"] == TRANSFER_T.DEPLOY_IMAGE)
                
                if (data["Transfer_Type"] != TRANSFER_T.DEPLOY_IMAGE):                
                    # Guardamos los datos de conexión al repositorio  
                    self.__dbConnector.addValueToConnectionDataDictionary(data["CommandID"], {"RepositoryIP": data["RepositoryIP"], "RepositoryPort" : data["RepositoryPort"]})                
                    # Arrancamos la máquina virtual
                    self.__domainHandler.createDomain(data["TargetImageID"], data["UserID"], data["CommandID"])        
                else :
                    p = self.__packetHandler.createConfirmationPacket(VM_SERVER_PACKET_T.IMAGE_DEPLOYED, data["TargetImageID"], data["CommandID"])
                    self.__networkManager.sendPacket('', self.__serverListenningPort, p)
                    
                # Borramos el fichero .zip
                ChildProcessManager.runCommandInForeground("rm " + compressedFilePath, VMServerException)    
            else:        
                # Comprimimos los ficheros
                
                zipFilePath = path.join(self.__transferDirectory, str(data["TargetImageID"]) + ".zip")                
                
                self.__compressor.createCompressedFile(zipFilePath, [data["OSImagePath"], 
                    data["DataImagePath"], path.join(self.__definitionFileDirectory, data["DefinitionFilePath"])])
                
                
                # Borramos los ficheros fuente
                ChildProcessManager.runCommandInForeground("rm -rf " + path.dirname(path.join(self.__definitionFileDirectory, data["DefinitionFilePath"])), Exception)
                ChildProcessManager.runCommandInForeground("rm -rf " + path.dirname(data["OSImagePath"]), Exception)
                
                # Encolamos la petición
                
                data.pop("DataImagePath")
                data.pop("OSImagePath")
                data.pop("DefinitionFilePath")
               
                data["SourceFilePath"] = path.basename(zipFilePath)        
                
                self.__dbConnector.addToTransferQueue(data)
        except Exception as e:
            if (data["Transfer_Type"] == TRANSFER_T.DEPLOY_IMAGE):
                packet_type = VM_SERVER_PACKET_T.IMAGE_DEPLOYMENT_ERROR
            else :
                packet_type = VM_SERVER_PACKET_T.IMAGE_EDITION_ERROR
                
            p = self.__packetHandler.createErrorPacket(packet_type, "Compression error: " + e.message, data["CommandID"])
            self.__networkManager.sendPacket('', self.__serverListenningPort, p)
            
            # Generar una transferencia especial para dejar de editar la imagen
            transfer = dict()
            transfer["Transfer_Type"] = TRANSFER_T.CANCEL_EDITION
            transfer["RepositoryIP"] = data["RepositoryIP"]
            transfer["RepositoryPort"] = data["RepositoryPort"]
            transfer["CommandID"] = data["CommandID"]
            transfer["ImageID"] = data["TargetImageID"]
            self.__dbConnector.addToTransferQueue(transfer)