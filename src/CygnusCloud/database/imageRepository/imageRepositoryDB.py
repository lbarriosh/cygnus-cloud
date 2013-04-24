
from database.utils.connector import BasicDatabaseConnector
from re import sub
from ccutils.enums import enum
from os import path

IMAGE_STATUS_T = enum("NOT_RECEIVED", "READY", "EDITION")

class ImageRepositoryDBConnector(BasicDatabaseConnector):
    
    def __init__(self, sqlUser, sqlPassword, databaseName):
        BasicDatabaseConnector.__init__(self, sqlUser, sqlPassword, databaseName)
    
    def getImageData(self, imageID):
        sqlQuery = "SELECT * FROM Image WHERE imageID = {0}".format(imageID)
        row = self._executeQuery(sqlQuery, False)
        if (row == ()) :
            return None
        (imageID, compressedFilePath, imageStatus) = row[0]
        result = dict()
        result["compressedFilePath"] = compressedFilePath
        result["imageStatus"] = imageStatus
        return result
    
    def addImage(self):        
        update = "INSERT INTO Image(compressedFilePath, imageStatus) VALUES (NULL, {0});".format(IMAGE_STATUS_T.NOT_RECEIVED)
        self._executeUpdate(update)
        query = "SELECT imageID FROM Image;"
        results = self._executeQuery(query, False)
        imageID = int(results[len(results) - 1][0])
        update = "UPDATE Image SET compressedFilePath = '{1}' WHERE imageID = {0};".format(imageID, "undefined" + str(imageID))
        self._executeUpdate(update)
        return imageID
    
    def addVanillaImage(self, compressedFilePath):
        update = "INSERT INTO Image(compressedFilePath, imageStatus) VALUES ('{0}', {1});".format("undefined", IMAGE_STATUS_T.READY)
        self._executeUpdate(update)
        
    def removeImage(self, imageID):        
        sqlQuery = "DELETE FROM Image WHERE imageID = " + str(imageID)
        self._executeUpdate(sqlQuery)
        
    def changeImageStatus(self, imageID, newStatus):
        update = "UPDATE Image SET imageStatus = {1} WHERE imageID = {0};".format(imageID, newStatus)
        self._executeUpdate(update)
        
    def processFinishedTransfer(self, fileName):
        imageID = sub("[^0-9]", "", path.basename(fileName))
        update = "UPDATE Image SET imageStatus = {1}, compressedFilePath = '{2}' WHERE imageID = {0};".format(imageID, IMAGE_STATUS_T.READY, fileName)
        self._executeUpdate(update)