# -*- coding: utf8 -*-
'''
Gestor de paquetes del servidor de cluster
@author: Luis Barrios Hernández
@version: 4.0
'''

from ccutils.enums import enum
from database.clusterServer.clusterServerDB import SERVER_STATE_T

MAIN_SERVER_PACKET_T = enum("REGISTER_VM_SERVER", "VM_SERVER_REGISTRATION_ERROR", "QUERY_VM_SERVERS_STATUS",
                            "VM_SERVERS_STATUS_DATA", "QUERY_VM_DISTRIBUTION", "VM_DISTRIBUTION_DATA",
                            "UNREGISTER_OR_SHUTDOWN_VM_SERVER", "BOOTUP_VM_SERVER",
                            "VM_SERVER_BOOTUP_ERROR", "VM_BOOT_REQUEST", "VM_CONNECTION_DATA", "VM_BOOT_FAILURE", 
                            "HALT", "QUERY_ACTIVE_VM_DATA", "ACTIVE_VM_DATA", "COMMAND_EXECUTED", "VM_SERVER_SHUTDOWN_ERROR",
                            "VM_SERVER_UNREGISTRATION_ERROR", "DOMAIN_DESTRUCTION", "DOMAIN_DESTRUCTION_ERROR")

class ClusterServerPacketHandler(object):
    """
    Estos objetos leen y escriben los paquetes que el endpoint y el servidor de cluster utilizan para
    comunicarse.
    """    
    def __init__(self, networkManager):
        """
        Inicializa el estado del gestor de paquetes
        Argumentos:
            networkManager: el objeto NetworkManager que utilizaremos para crear los paquetes
        """
        self.__packetCreator = networkManager
            
    def createVMServerRegistrationPacket(self, IPAddress, port, name, commandID):
        """
        Crea un paquete de registro de una máquina virtual
        Argumentos:
            IPAddress: la dirección IP del servidor
            port: su puerto
            name: el nombre del servidor de máquinas virtuales
            commandID: el identificador único del comando de arranque
        Devuelve:
            un paquete con los datos de los argumentos
        """
        p = self.__packetCreator.createPacket(3)
        p.writeInt(MAIN_SERVER_PACKET_T.REGISTER_VM_SERVER)
        p.writeString(IPAddress)
        p.writeInt(port)
        p.writeString(name)
        p.writeString(commandID)
        return p
    
    def createExecutedCommandPacket(self, commandID):
        """
        Crea un paquete que indica que un comando se ha ejecutado.
        Argumentos:
            commandID: el identificador único del comando
        Devuelve:
            un paquete con los datos de los argumentos
        """
        p = self.__packetCreator.createPacket(3)
        p.writeInt(MAIN_SERVER_PACKET_T.COMMAND_EXECUTED)
        p.writeString(commandID)
        return p
    
    def createVMServerRegistrationErrorPacket(self, IPAddress, port, name, reason, commandID):
        """
        Crea un paquete de error de registro de un servidor de máquinas virtuales
        Argumentos:
            IPAddress: la dirección IP del servidor
            port: su puerto
            name: el nombre del servidor de máquinas virtuales
            commandID: el identificador único del comando de arranque
            reason: mensaje de error
        Devuelve:
            un paquete con los datos de los argumentos
        """
        p = self.__packetCreator.createPacket(3)
        p.writeInt(MAIN_SERVER_PACKET_T.VM_SERVER_REGISTRATION_ERROR)
        p.writeString(IPAddress)
        p.writeInt(port)
        p.writeString(name)
        p.writeString(reason)        
        p.writeString(commandID)
        return p        
    
    def createDataRequestPacket(self, query):
        """
        Crea un paquete de solicitud de estado
        Argumentos:
            query: la información de estado que queremos recuperar
            (p.e. máquinas virtuales activas, imágenes que se pueden arrancar,...)
         Devuelve:
            un paquete con los datos de los argumentos
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(query)
        return p
    
    def createVMServerStatusPacket(self, segment, sequenceSize, data):
        """
        Crea un paquete con el estado de un servidor de máquinas virtuales
        Argumentos:
            segment: posición del segmento en la secuencia
            sequenceSize: tamaño de la secuencia (en segmentos)
            data: los datos del segmento
        Devuelve:
            un paquete con los datos de los argumentos
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(MAIN_SERVER_PACKET_T.VM_SERVERS_STATUS_DATA)
        p.writeInt(segment)
        p.writeInt(sequenceSize)
        for row in data :
            p.writeString(row["ServerName"])
            p.writeString(ClusterServerPacketHandler.__vm_server_status_to_string(row["ServerStatus"]))
            p.writeString(row["ServerIP"])
            p.writeInt(int(row["ServerPort"]))            
        return p
    
    def createVMDistributionPacket(self, segment, sequenceSize, data):
        """
        Crea un paquete que contiene la distribución de las máquinas virtuales
        Argumentos:
            segment: posición del segmento en la secuencia
            sequenceSize: tamaño de la secuencia (en segmentos)
            data: los datos del segmento
        Devuelve:
            un paquete con los datos de los argumentos
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(MAIN_SERVER_PACKET_T.VM_DISTRIBUTION_DATA)
        p.writeInt(segment)
        p.writeInt(sequenceSize)
        for row in data :
            p.writeString(row["ServerName"])
            p.writeInt(row["VMID"])
        return p
    
    def createVMServerUnregistrationOrShutdownPacket(self, serverNameOrIPAddress, halt, unregister, commandID):
        """
        Crea un paquete de apagado o borrado de un servidor de máquinas virtuales
        Argumentos:
            serverNameOrIPAddress: el nombre del servidor o su dirección IP
            halt: Si es True, los dominios se destuirán inmediatamente. Si es False, se esparará a que
            los usuarios los apaguen. 
            unregister: Si es True el servidor se borrará; si es False sólo se apagará
            commandID: el identificador único del comando
        Devuelve:
            un paquete con los datos de los argumentos
        """
        p = self.__packetCreator.createPacket(3)
        p.writeInt(MAIN_SERVER_PACKET_T.UNREGISTER_OR_SHUTDOWN_VM_SERVER)
        p.writeString(serverNameOrIPAddress)
        p.writeBool(halt)
        p.writeBool(unregister)
        p.writeString(commandID)
        return p
    
    def createVMServerBootUpPacket(self, serverNameOrIPAddress, commandID):
        """
        Crea un paquete de arranque de un servidor de máquinas virtuales
        Argumentos:
            serverNameOrIPAddress: el nombre o la IP del servidor
            commandID: el identificador único del comando
        Devuelve:
            un paquete con los datos de los argumentos
        """
        p = self.__packetCreator.createPacket(3)
        p.writeInt(MAIN_SERVER_PACKET_T.BOOTUP_VM_SERVER)
        p.writeString(serverNameOrIPAddress)
        p.writeString(commandID)
        return p
    
    def createVMServerGenericErrorPacket(self, packet_type, serverNameOrIPAddress, reason, commandID):
        """
        Crea un paquete de error relacionado con un servidor de máquinas virtuales
        Argumentos:
            packet_type: tipo del paquete de error
            serverNameOrIPAddress: la IP o el nombre del servidor
            reason: un mensaje de error
            commandID: el identificador único del comando
        Devuelve:
            un paquete con los datos de los argumentos
        """
        p = self.__packetCreator.createPacket(3)
        p.writeInt(packet_type)
        p.writeString(serverNameOrIPAddress)
        p.writeString(reason)
        p.writeString(commandID)
        return p
    
    def createVMBootRequestPacket(self, imageID, userID, commandID):
        """
        Crea un paquete de arranque de máuqina virtual
        Argumentos:
            imageID: identificador de la imagen a arrancar
            userID: identificador del propietario de la máquina
            commandID: el identificador único del comando
        Devuelve:
            un paquete con los datos de los argumentos
        """
        p = self.__packetCreator.createPacket(4)
        p.writeInt(MAIN_SERVER_PACKET_T.VM_BOOT_REQUEST)
        p.writeInt(imageID)
        p.writeInt(userID)
        p.writeString(commandID)
        return p
    
    def createVMBootFailurePacket(self, imageID, reason, commandID):
        """
        Crea un paquete que indica un error al arrancar una máquina virtual
        Argumentos:
            imageID: el identificador de la imagen que se intentó arrancar
            reason: un mensaje de error
            commandID: el identificador único del comando
        Devuelve:
            un paquete con los datos de los argumentos
        """
        p = self.__packetCreator.createPacket(4)
        p.writeInt(MAIN_SERVER_PACKET_T.VM_BOOT_FAILURE)
        p.writeInt(imageID)
        p.writeString(reason)
        p.writeString(commandID)
        return p
    
    def createVMConnectionDataPacket(self, IPAddress, port, password, commandID):
        """
        Crea un paquete con los datos de conexión a una máquina virtual
        Argumentos:
            IPAddress: dirección IP del servidor VNC
            port: puerto del servidor VNC
            password: contraseña del servidor VNC
            commandID: identificador único del comando
        Devuelve:
            un paquete con los datos de los argumentos
        """
        p = self.__packetCreator.createPacket(4)
        p.writeInt(MAIN_SERVER_PACKET_T.VM_CONNECTION_DATA)
        p.writeString(IPAddress)
        p.writeInt(port)
        p.writeString(password)
        p.writeString(commandID)
        return p
    
    def createActiveVMsDataPacket(self, data):
        """
        Crea un paquete que contiene los datos de conexión de varias máquinas virtuales
        del mismo servidor
        Argumentos:
            data: un string con los datos a enviar
        Devuelve:
            un paquete con los datos de los argumentos
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(MAIN_SERVER_PACKET_T.ACTIVE_VM_DATA)
        p.dumpData(data)
        return p
    
    def createHaltPacket(self, haltServers):
        """
        Crea un paquete que apagará el servidor de cluster.
        Argumentos:
            haltServers: si es True, los servidores de máquinas virtuales se cargarán todos los
            dominios inmediatamente. Si es False, esperarán a que los usuarios los apaguen.
        Devuelve:
            un paquete con los datos de los argumentos
        """
        p = self.__packetCreator.createPacket(1)
        p.writeInt(MAIN_SERVER_PACKET_T.HALT)
        p.writeBool(haltServers)
        return p
    
    def createDomainDestructionPacket(self, domainID, commandID):
        """
        Crea un paquete de destrucción de dominios
        Argumentos:
            domainID: el identificador único del dominio a destruir
            commandID: el identificador único del comando
        Devuelve:
            un paquete con los datos de los argumentos
        """
        p = self.__packetCreator.createPacket(4) # Todo lo que sea liberar carga es bueno. Por eso es ligeramente más prioritario que los otros
        p.writeInt(MAIN_SERVER_PACKET_T.DOMAIN_DESTRUCTION)
        p.writeString(domainID)
        p.writeString(commandID)
        return p

    def createDomainDestructionErrorPacket(self, errorMessage, commandID):
        """
        Crea un paquete de error asociado a la destrucción de un dominio.
        Argumentos:
            errorMessage: mensaje de error
            commandID: identificador único del comando
        Devuelve:
            un paquete con los datos de los argumentos
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(MAIN_SERVER_PACKET_T.DOMAIN_DESTRUCTION_ERROR)
        p.writeString(errorMessage)
        p.writeString(commandID)
        return p
    
    @staticmethod
    def __vm_server_status_to_string(status):
        """
        Convierte a string el código de estado de un servidor de máquinas virtuales.
        Argumentos:
            status: código de estado.
        Devuelve:
            string correspondiente al código de estado
        """
        if (status == SERVER_STATE_T.BOOTING) :
            return "Booting"
        elif (status == SERVER_STATE_T.READY) :
            return "Ready"
        elif (status == SERVER_STATE_T.SHUT_DOWN) :
            return "Shut down"
        elif (status == SERVER_STATE_T.RECONNECTING) :
            return "Reconnecting"
        else :
            return "Connection lost"
        
    
    def readPacket(self, p):
        """
        Lee un paquete intercambiado por el endpoint y el servidor de cluster
        Argumentos:
            p: el paquete a leer
        Devuelve:
            Un diccionario con el contenido del paquete. El tipo del paquete se guardará bajo la clave
            packet_type.
        """
        result = dict()
        packet_type = p.readInt()
        result["packet_type"] = packet_type
        if (packet_type == MAIN_SERVER_PACKET_T.REGISTER_VM_SERVER) :
            result["VMServerIP"] = p.readString()
            result["VMServerPort"] = p.readInt()
            result["VMServerName"] = p.readString()
            result["CommandID"] = p.readString()
        elif (packet_type == MAIN_SERVER_PACKET_T.VM_SERVER_REGISTRATION_ERROR) :
            result["VMServerIP"] = p.readString()
            result["VMServerPort"] = p.readInt()
            result["VMServerName"] = p.readString()
            result["ErrorMessage"] = p.readString()            
            result["CommandID"] = p.readString()
            
        elif (packet_type == MAIN_SERVER_PACKET_T.VM_SERVERS_STATUS_DATA) :
            result["Segment"] = p.readInt()
            result["SequenceSize"] = p.readInt()
            data = []
            while (p.hasMoreData()) :
                data.append((p.readString(), p.readString(), p.readString(), p.readInt()))
            result["Data"] = data
            
        elif (packet_type == MAIN_SERVER_PACKET_T.VM_DISTRIBUTION_DATA) :
            result["Segment"] = p.readInt()
            result["SequenceSize"] = p.readInt()
            data = []
            while (p.hasMoreData()) :
                data.append((p.readString(), p.readInt()))
            result["Data"] = data
            
        elif (packet_type == MAIN_SERVER_PACKET_T.ACTIVE_VM_DATA) :
            result["Segment"] = p.readInt()
            result["SequenceSize"] = p.readInt()
            result["VMServerIP"] = p.readString()
            data = []
            while (p.hasMoreData()) :
                data.append((p.readString(), p.readInt(), p.readInt(), p.readString(), p.readInt(), p.readString()))
            result["Data"] = data
                
        elif (packet_type == MAIN_SERVER_PACKET_T.UNREGISTER_OR_SHUTDOWN_VM_SERVER) :
            result["ServerNameOrIPAddress"] = p.readString()
            result["Halt"] =  p.readBool()
            result["Unregister"] = p.readBool()
            result["CommandID"] = p.readString()
            
        elif (packet_type == MAIN_SERVER_PACKET_T.BOOTUP_VM_SERVER) :
            result["ServerNameOrIPAddress"] = p.readString()
            result["CommandID"] = p.readString()
            
        elif (packet_type == MAIN_SERVER_PACKET_T.VM_SERVER_BOOTUP_ERROR or 
              packet_type == MAIN_SERVER_PACKET_T.VM_SERVER_UNREGISTRATION_ERROR or 
              packet_type == MAIN_SERVER_PACKET_T.VM_SERVER_SHUTDOWN_ERROR) :
            result["ServerNameOrIPAddress"] = p.readString()
            result["ErrorMessage"] = p.readString()
            result["CommandID"] = p.readString()
            
        elif (packet_type == MAIN_SERVER_PACKET_T.VM_BOOT_REQUEST):
            result["VMID"] = p.readInt()
            result["UserID"] = p.readInt()
            result["CommandID"] = p.readString()
            
        elif (packet_type == MAIN_SERVER_PACKET_T.VM_BOOT_FAILURE):
            result["VMID"] = p.readInt()
            result["ErrorMessage"] = p.readString()
            result["CommandID"] = p.readString()
            
        elif (packet_type == MAIN_SERVER_PACKET_T.VM_CONNECTION_DATA):
            result["VNCServerIPAddress"] = p.readString()
            result["VNCServerPort"] = p.readInt()
            result["VNCServerPassword"] = p.readString()
            result["CommandID"] = p.readString()
            
        elif (packet_type == MAIN_SERVER_PACKET_T.HALT) :
            result["HaltVMServers"] = p.readBool()
            
        elif (packet_type == MAIN_SERVER_PACKET_T.COMMAND_EXECUTED) :
            result["CommandID"] = p.readString()
            
        elif (packet_type == MAIN_SERVER_PACKET_T.DOMAIN_DESTRUCTION) :
            result["DomainID"] = p.readString()
            result["CommandID"] = p.readString()
        
        elif (packet_type == MAIN_SERVER_PACKET_T.DOMAIN_DESTRUCTION_ERROR) :
            result["ErrorMessage"] = p.readString()
            result["CommandID"] = p.readString()        
                      
        return result