
from database.utils.connector import BasicDatabaseConnector

from ccutils.enums import enum

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
        update = "INSERT INTO Image(compressedFilePath, imageStatus) VALUES ('{0}', {1});".format("undefined", IMAGE_STATUS_T.NOT_RECEIVED)
        self._executeUpdate(update)
        query = "SELECT imageID FROM Image;"
        results = self._executeQuery(query, False)
        return int(results[len(results) - 1][0])
        
    def removeImage(self, imageID):        
        sqlQuery = "DELETE FROM Image WHERE imageID = " + str(imageID)
        self._executeUpdate(sqlQuery)