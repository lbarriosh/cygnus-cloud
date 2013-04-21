
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
        (imageID, compressedFilePath, imageStatus, groupId) = row[0]
        result = dict()
        result["compressedFilePath"] = compressedFilePath
        result["imageStatus"] = imageStatus
        result["groupID"] = int(groupId)
        return result
    
    def addImage(self, compressedFilePath, groupID):        
        update = "INSERT INTO Image(compressedFilePath, imageStatus, groupID) VALUES ('{0}', {1}, '{2}');".format(compressedFilePath, IMAGE_STATUS_T.NOT_RECEIVED, groupID)
        self._executeUpdate(update)
        query = "SELECT imageID FROM Image WHERE compressedFilePath = '{0}' AND imageStatus = {1} AND groupID = '{2}';".format(compressedFilePath, IMAGE_STATUS_T.NOT_RECEIVED, groupID)
        return self._executeQuery(query, True)[0]
        
    def removeImage(self, imageID):        
        sqlQuery = "DELETE FROM Image WHERE imageID = " + str(imageID)
        self._executeUpdate(sqlQuery)