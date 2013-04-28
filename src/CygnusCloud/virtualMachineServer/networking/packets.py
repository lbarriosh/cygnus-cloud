# -*- coding: utf8 -*-
'''
Gestor de paquetes del servidor de máquinas virtuales
@author: Luis Barrios Hernández
@version: 4.0
'''

from ccutils.enums import enum

VM_SERVER_PACKET_T = enum("CREATE_DOMAIN", "DESTROY_DOMAIN", "DOMAIN_CONNECTION_DATA", "SERVER_STATUS",
                          "SERVER_STATUS_REQUEST", "USER_FRIENDLY_SHUTDOWN", 
                          "QUERY_ACTIVE_VM_DATA", "ACTIVE_VM_DATA", "HALT", "QUERY_ACTIVE_DOMAIN_UIDS", "ACTIVE_DOMAIN_UIDS",
                          "IMAGE_EDITION", "IMAGE_EDITION_ERROR")

class VMServerPacketHandler(object):
    """
    Gestor de paquetes del servidor de máquinas virtuales
    """
    
    def __init__(self, packetCreator):
        """
        Inicializa el estado del gestor de paquetes.
        Argumentos:
            packetCreator: objeto que se usará para crear paquetes.
        Devuelve:
            Nada
        """
        self.__packetCreator = packetCreator
    
    def createVMBootPacket(self, machineId, userId, commandID):
        """
        Crea un paquete de arranque de una máquina virtual
        Argumentos:
            machineId: el identificador único de la máquina virtual a arrancar
            userId: el identificador único del usuario que quiere arrancarla
            commandID: el identificador único del comando de arranque
        Devuelve:
            Un paquete construido a partir de sus argumentos.
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(VM_SERVER_PACKET_T.CREATE_DOMAIN)
        p.writeInt(machineId)
        p.writeInt(userId)
        p.writeString(commandID)
        return p
    
    def createVMShutdownPacket(self, domainUID):
        """
        Crea un paquete para apagar una máquina virtual
        Argumentos:
            domainUID: el identificador único de la máquina virtual a apager
        Devuelve:
            Un paquete que contiene los datos especificados
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(VM_SERVER_PACKET_T.DESTROY_DOMAIN)
        p.writeString(domainUID) # domainUID es el identificador del comando de arranque de la máquina. Por eso
                            # es un string.
        return p
    
    def createVMConnectionParametersPacket(self, vncServerIP, vncServerPort, password, commandID):
        """
        Crea un paquete que contiene los datos de conexión VNC de una máquina virtual
        Argumentos:
            vncServerIP: la dirección IP del servidor VNC
            vncServerPort: el puerto de escucha del servidor VNC
            password: la contraseña del servidor VNC
            commandID: el identificador único del comando de arranque de la máquina virtual
        Devuelve:
            Un paquete construido a partir de sus argumentos.
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(VM_SERVER_PACKET_T.DOMAIN_CONNECTION_DATA)
        p.writeString(vncServerIP)
        p.writeInt(vncServerPort)
        p.writeString(password)
        p.writeString(commandID)
        return p
    
    def createVMServerDataRequestPacket(self, packet_type):
        """
        Crea un paquete que permite solicitar datos al servidor de máquinas virtuales.
        Argumentos:
            packet_type: un tipo de paquete, que fijará la información que solicitamos al servidor
            de máquinas virtuales
        Devuelve:
            Un paquete construido a partir de sus argumentos.
        """
        p = self.__packetCreator.createPacket(7)
        p.writeInt(packet_type)
        return p
    
    def createVMServerStatusPacket(self, vmServerIP, activeDomains, ramInUse, availableRAM, freeStorageSpace, availableStorageSpace, 
                                   freeTemporarySpace, availableTemporarySpace, activeVCPUs, physicalCPUs):
        """
        Crea un paquete que contiene el estado del servidor de máquinas virtuales
        Argumentos:
            vmServerIP: la dirección IP del servidor de máquinas virtuales
            activeDomains: el número de máquinas virtuales activas
            ramInUse: la cantidad de RAM usada (en kilobytes)
            availableRAM: la cantidad total de RAM (en kilobytes)
            freeStorageSpace: el espacio en disco disponible para almacenar imágenes (en kilobytes)
            availableStorageSpace: el espacio total en disco que puede usare para almacenar imágenes (en kilobytes)
            freeTemporarySpace: el espacio en disco disponible para almacenar datos temporales (en kilobytes)
            availableTemporarySpace: el espacio total en disco que puede usarse para almacenar datos temporales (en kilobytes)
            activeVCPUs: el número de CPUs virtuales activas
            physicalCPUs: el número de CPUs físicas de la máquina
        Devuelve:
            Un paquete construido a partir de sus argumentos.
        """
        p = self.__packetCreator.createPacket(7)
        p.writeInt(VM_SERVER_PACKET_T.SERVER_STATUS)
        p.writeString(vmServerIP)
        p.writeInt(activeDomains)
        p.writeInt(ramInUse)
        p.writeInt(availableRAM)
        p.writeInt(freeStorageSpace)
        p.writeInt(availableStorageSpace)
        p.writeInt(freeTemporarySpace)
        p.writeInt(availableTemporarySpace)
        p.writeInt(activeVCPUs)
        p.writeInt(physicalCPUs)
        return p
    
    def createVMServerShutdownPacket(self):
        """
        Crea un paquete de apagado (amigable) de un servidor de máquinas virtuales
        Argumentos:
            Ninguno
        Devuelve:
            Un paquete construido a partir de sus argumentos.
        """
        p = self.__packetCreator.createPacket(3)
        p.writeInt(VM_SERVER_PACKET_T.USER_FRIENDLY_SHUTDOWN)
        return p
    
    def createVMServerHaltPacket(self):
        """
        Crea un paquete de apagado inmediato de un servidor de máquinas virtuales
        Argumentos:
            Ninguno
        Devuelve:
            Un paquete construido a partir de sus argumentos.
        """
        p = self.__packetCreator.createPacket(3)
        p.writeInt(VM_SERVER_PACKET_T.HALT)
        return p
    
    def createActiveVMsDataPacket(self, serverIPAddress, segment, sequenceSize, data):
        """
        Crea un paquete que contiene los datos de conexión VNC de varias máquinas virtuales activas.
        Argumentos:
            serverIPAddress: la dirección IP del servidor de máquinas virtuales
            segment: la posición que ocupan los datos de este paquete en todo el flujo de paquetes
            sequenceSize: el número de segmentos de la secuencia
            data: los datos del segmento
        """
        p = self.__packetCreator.createPacket(6)
        p.writeInt(VM_SERVER_PACKET_T.ACTIVE_VM_DATA)
        p.writeInt(segment)
        p.writeInt(sequenceSize)
        p.writeString(serverIPAddress)
        for row in data :
            p.writeString(row["DomainID"])
            p.writeInt(row["UserID"])
            p.writeInt(row["ImageID"])
            p.writeString(row["VMName"])
            p.writeInt(row["VNCPort"])
            p.writeString(row["VNCPass"])
        return p    
    
    def createActiveDomainUIDsPacket(self, vmServerIP, data):
        """
        Crea un paquete que contiene los identificadores únicos de todas las máquinas virtuales
        Argumentos:
            vmServerIP: la dirección IP del servidor de máquinas virtuales.
            data: lista con los identificadores únicos de las máquinas virtuales
        Devuelve:
            un paquete con los datos de los argumentos
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(VM_SERVER_PACKET_T.ACTIVE_DOMAIN_UIDS)
        p.writeString(vmServerIP)
        for domain_uid in data :
            p.writeString(domain_uid)
        return p
    
    def createImageEditionPacket(self, repositoryIP, repositoryPort, sourceImageID, modify, commandID, userID):
        """
        Crea un paquete que contiene los datos para descargarse una imagen del repositorio
        Argumentos:
           FIXME: actualizar
        Devuelve:
            Un paquete construido a partir de sus argumentos.
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(VM_SERVER_PACKET_T.IMAGE_EDITION)
        p.writeString(repositoryIP)
        p.writeInt(repositoryPort)
        p.writeInt(sourceImageID)
        p.writeBool(modify)
        p.writeString(commandID)
        p.writeInt(userID)
        return p
    
    def createErrorPacket(self, packet_type, errorMessage, commandID):
        p = self.__packetCreator.createPacket(5)
        p.writeInt(VM_SERVER_PACKET_T.IMAGE_EDITION_ERROR)
        p.writeString(errorMessage)
        p.writeString(commandID)
        return p
    
    def readPacket(self, p):
        """
        Lee un paquete del servidor de máquinas virtuales y vuelca sus datos a un diccionario.
        Argumentos:
            p: el paquete a leer
        Devuelve:
            Un diccionario con los datos del paquete. El tipo del paquete estará asociado a la clave
            packet_type.
        """
        result = dict()
        packet_type = p.readInt()
        result["packet_type"] = packet_type
        if (packet_type == VM_SERVER_PACKET_T.CREATE_DOMAIN) :
            result["MachineID"] = p.readInt()
            result["UserID"] = p.readInt()
            result["CommandID"] = p.readString()
        elif (packet_type == VM_SERVER_PACKET_T.DESTROY_DOMAIN) :
            result["VMID"] = p.readString()
        elif (packet_type == VM_SERVER_PACKET_T.DOMAIN_CONNECTION_DATA):
            result["VNCServerIP"] = p.readString()
            result["VNCServerPort"] = p.readInt()
            result["VNCServerPassword"] = p.readString()
            result["CommandID"] = p.readString()
            result["Modify"] = p.readBool()
        elif (packet_type == VM_SERVER_PACKET_T.SERVER_STATUS and p.hasMoreData()) :
            result["VMServerIP"] = p.readString()
            result["ActiveDomains"] = p.readInt()
            result["RAMInUse"] = p.readInt()
            result["RAMSize"] = p.readInt()
            result["FreeStorageSpace"] = p.readInt()
            result["AvailableStorageSpace"] = p.readInt()
            result["FreeTemporarySpace"] = p.readInt()
            result["AvailableTemporarySpace"] = p.readInt()
            result["ActiveVCPUs"] = p.readInt()
            result["PhysicalCPUs"] = p.readInt()
        elif (packet_type == VM_SERVER_PACKET_T.ACTIVE_DOMAIN_UIDS) :
            ac = []
            result["VMServerIP"] = p.readString()
            while (p.hasMoreData()):
                ac.append(p.readString())
            result["Domain_UIDs"] = ac    
        elif (packet_type == VM_SERVER_PACKET_T.IMAGE_EDITION) :
            result["repositoryIP"] = p.readString()
            result["repositoryPort"] = p.readInt()
            result["sourceImageID"] = p.readInt()
            result["modify"] = p.readBool()   
            result["CommandID"] = p.readString()
            result["UserID"] = p.readInt()
        elif (packet_type == VM_SERVER_PACKET_T.IMAGE_EDITION_ERROR) :
            result["errorMessage"] = p.readString()
            result["CommandID"] = p.readString()
        # Importante: los segmentos que transportan los datos de conexión se reenviarán, por lo que no tenemos que
        # leerlos para ganar en eficiencia.
        return result