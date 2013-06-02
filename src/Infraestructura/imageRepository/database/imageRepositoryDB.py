# -*- coding: UTF8 -*-

from ccutils.databases.connector import BasicDBConnector
from re import sub
from os import path

from imageRepository.database.image_status_t import IMAGE_STATUS_T

"""
Conector con la base de datos del repositorio
"""
class ImageRepositoryDBConnector(BasicDBConnector):
    
    """
    Establece la conexión con la base de datos
    Argumentos:
        sqlUser: usuario a utilizar
        sqlPassword: contraseña a utilizar
        databaseName: nombre de la base de datos
    """
    def __init__(self, sqlUser, sqlPassword, databaseName):
        BasicDBConnector.__init__(self, sqlUser, sqlPassword, databaseName)
    
    """
    Devuelve los datos asociados a una imagen
    Argumentos:
        imageID: el identificador de la imagen que nos interesa
    Devuelve:
        diccionario con los datos de la imagen. Si la imagen no existe, devuelve None.
    """
    def getImageData(self, imageID):
        sqlQuery = "SELECT * FROM Image WHERE imageID = {0}".format(imageID)
        row = self._executeQuery(sqlQuery, False)
        if (row == None) :
            return None
        (imageID, compressedFilePath, imageStatus) = row[0]
        result = dict()
        result["compressedFilePath"] = str(compressedFilePath)
        result["imageStatus"] = imageStatus
        return result
    
    """
    Añade una imagen a la base de datos
    Argumentos:
        Ninguno
    Devuelve:
        El identificador único de la imagen añadida
    """
    def addImage(self):        
        update = "INSERT INTO Image(compressedFilePath, imageStatus) VALUES (NULL, {0});".format(IMAGE_STATUS_T.NOT_RECEIVED)
        self._executeUpdate(update)
        query = "SELECT imageID FROM Image;"
        results = self._executeQuery(query, False)
        imageID = int(results[len(results) - 1])
        update = "UPDATE Image SET compressedFilePath = '{1}' WHERE imageID = {0};".format(imageID, "undefined" + str(imageID))
        self._executeUpdate(update)
        return imageID
    
    def cancelImageEdition(self, imageID):
        query = "SELECT compressedFilePath FROM Image WHERE imageID = {0};".format(imageID)
        result = self._executeQuery(query, True)
        if (result == None) :
            # La imagen no se está editando => nos limitamos a confirmar la petición
            return
        if ("undefined" in result) :
            self.deleteImage(imageID)
        else :
            self.changeImageStatus(imageID, IMAGE_STATUS_T.READY)
    
    """
    Borra una imagen de la base de datos
    Argumentos:
        imageID: el identificador único de la imagen
    Devuelve:
        Nada
    """
    def deleteImage(self, imageID):
        update = "DELETE FROM Image WHERE imageID = {0};".format(imageID)
        self._executeUpdate(update)
    
    """
    Añade una imagen vanilla a la base de datos. 
    Argumentos:
        compressedFilePath: la ruta del fichero comprimido con los datos de la imagen
    Devuelve:
        el identificador de la imagen
    """
    def addVanillaImage(self, compressedFilePath):
        update = "INSERT INTO Image(compressedFilePath, imageStatus) VALUES ('{0}', {1});".format("undefined", IMAGE_STATUS_T.READY)
        self._executeUpdate(update)
        
    """
    Cambia el estado de una imagen
    Argumentos:
        imageID: el identificador de la imagen
        newStatus: el nuevo estado de la imagen
    Devuelve:
        Nada
    """
    def changeImageStatus(self, imageID, newStatus):
        update = "UPDATE Image SET imageStatus = {1} WHERE imageID = {0};".format(imageID, newStatus)
        self._executeUpdate(update)
        
    """
    Actualiza el estado de una imagen que se acaba de subir.
    Argumentos:
        fileName: el nombre del fichero de la imagen
    Devuelve:
        Nada
    @attention: Por las limitaciones que nos impone el servidor FTP, el ID de la imagen DEBE aparecer UNA vez
    en el nombre del fichero.
    """
    def handleFinishedUploadTransfer(self, fileName):
        imageID = sub("[^0-9]", "", path.basename(fileName))
        update = "UPDATE Image SET imageStatus = {1}, compressedFilePath = '{2}' WHERE imageID = {0};".format(imageID, IMAGE_STATUS_T.READY, fileName)
        self._executeUpdate(update)    