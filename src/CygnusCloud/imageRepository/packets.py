# -*- coding: utf8 -*-
'''
Created on Apr 21, 2013

@author: luis
'''

from ccutils.enums import enum

PACKET_T = enum("HALT", "ADD_IMAGE", "ADDED_IMAGE_ID", "RETR_REQUEST", "RETR_REQUEST_RECVD", "RETR_REQUEST_ERROR", "RETR_START", "RETR_ERROR",
                "STOR_REQUEST", "STOR_REQUEST_RECVD", "STOR_REQUEST_ERROR", "STOR_START", "STOR_ERROR",
                "DELETE_REQUEST", "DELETE_REQUEST_RECVD", "DELETE_REQUEST_ERROR")

class ImageRepositoryPacketHandler(object):
    """
    Gestor de paquetes del repositorio
    """    
    
    def __init__(self, packetCreator):
        """
        Inicializa el estado
        Argumentos:
            packetCreator: objeto que se usará para crear los paquetes
        """
        self.__packetCreator = packetCreator
            
    def createHaltPacket(self):
        """
        Crea un paquete de apagado
        Argumentos:
            Ninguno
        Devuelve:
            un paquete del tipo especificado cuyo contenido se fija a partir de los argumentos
        """
        p = self.__packetCreator.createPacket(1)
        p.writeInt(PACKET_T.HALT)
        return p
    
    def createRetrieveRequestPacket(self, imageID, modify):
        """
        Crea un paquete de solicitud de descarga
        Argumentos:
            imageID: el identificador único de la imagen
            modify: si es True, se va a editar una imagen. Si es False, se va a crear una imagen a partir de otra.
        Devuelve:
            un paquete del tipo especificado cuyo contenido se fija a partir de los argumentos
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(PACKET_T.RETR_REQUEST)
        p.writeInt(imageID)
        p.writeBool(modify)
        return p
    
    def createStoreRequestPacket(self, imageID):
        """
        Crea un paquete de solicitud de subida
        Argumentos:
            imageID: el identificador único de la imagen cuyo fichero vamos a subir
        Devuelve:
            un paquete del tipo especificado cuyo contenido se fija a partir de los argumentos
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(PACKET_T.STOR_REQUEST)
        p.writeInt(imageID)
        return p
    
    def createImageRequestReceivedPacket(self, packet_t):
        """
        Crea un paquete que indica la recepción de una petición de subida, descarga o borrado
        Argumentos:
            packet_t: el tipo de paquete, que se corresponde con la confirmación a enviar
        Devuelve:
            un paquete del tipo especificado cuyo contenido se fija a partir de los argumentos
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(packet_t)
        return p
    
    def createTransferEnabledPacket(self, packet_t, imageID, FTPServerPort, username, password, serverDirectory, fileName):
        """
        Crea un paquete que indica que una transferencia puede comenzar
        Argumentos:
            packet_t: el tipo de paquete, que se corresponde con el tipo de transferencia (STORE o RETRIEVE)
            imageID: el identificador único de la imagen
            FTPServerPort: el puerto de escucha del servidor FTP
            username: el usuario del servidor FTP
            password: la contraseña del servidor FTP
            serverDirectory: el directorio del servidor donde se encuentra el fichero
            fileName: el nombre del fichero
        Devuelve:
            un paquete del tipo especificado cuyo contenido se fija a partir de los argumentos
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(packet_t)
        p.writeInt(imageID)
        p.writeInt(FTPServerPort)
        p.writeString(username)
        p.writeString(password)
        p.writeString(serverDirectory)
        p.writeString(fileName)
        return p
    
    def createErrorPacket(self, packet_t, errorMessage):
        """
        Crea un paquete de error.
        Argumentos:
            packet_t: el tipo de paquete, que se corresponde con el tipo del error
            errorMessage: un mensaje de error
        Devuelve:
            un paquete del tipo especificado cuyo contenido se fija a partir de los argumentos
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(packet_t)
        p.writeString(errorMessage)
        return p
    
    def createAddImagePacket(self):
        """
        Crea un paquete de adición de imagen
        Argumentos:
        Devuelve:
            un paquete del tipo especificado cuyo contenido se fija a partir de los argumentos
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(PACKET_T.ADD_IMAGE)
        return p
    
    def createAddedImagePacket(self, imageID):
        """
        Crea un paquete de confirmación de adición de imagen.
        Argumentos:
            imageID: el identificador único de la nueva imagen
        Devuelve:
            un paquete del tipo especificado cuyo contenido se fija a partir de los argumentos
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(PACKET_T.ADDED_IMAGE_ID)
        p.writeInt(imageID)
        return p
    
    def createDeleteRequestPacket(self, imageID):
        """
        Crea un paquete de borrado de una imagen
        Argumentos:
            imageID: el identificador único de la imagen a borrar
        Devuelve:
            un paquete del tipo especificado cuyo contenido se fija a partir de los argumentos
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(PACKET_T.DELETE_REQUEST)
        p.writeInt(imageID)
        return p
    
    def readPacket(self, p):
        """
        Vuelca el contenido de un paquete en un diccionario
        Argumentos:
            p: el paquete cuyo contenido queremos extraer
        Devuelve:
            Nada
        """
        data = dict()
        packet_type = p.readInt()
        data['packet_type'] = packet_type
        (data['clientIP'], data['clientPort']) = p.getSenderData()
        if (packet_type == PACKET_T.ADDED_IMAGE_ID):
            data['addedImageID'] = p.readInt()
        elif (packet_type == PACKET_T.RETR_REQUEST) :
            data['imageID'] = p.readInt()
            data['modify'] = p.readBool()
        elif (packet_type == PACKET_T.STOR_REQUEST) :
            data['imageID'] = p.readInt()
        elif (packet_type == PACKET_T.RETR_REQUEST_ERROR or packet_type == PACKET_T.STOR_REQUEST_ERROR or 
              packet_type == PACKET_T.DELETE_REQUEST_ERROR or packet_type == PACKET_T.RETR_ERROR or 
              packet_type == PACKET_T.STOR_ERROR) :
            data['errorMessage'] = p.readString()
        elif (packet_type == PACKET_T.RETR_START or packet_type == PACKET_T.STOR_START) :
            data['imageID'] = p.readInt()
            data['FTPServerPort'] = p.readInt()
            data['username'] = p.readString()
            data['password'] = p.readString()
            data['serverDirectory'] = p.readString()
            data['fileName'] = p.readString()
        elif (packet_type == PACKET_T.DELETE_REQUEST):
            data['imageID'] = p.readInt()
        return data 