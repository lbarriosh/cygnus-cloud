
from database.utils.connector import BasicDatabaseConnector

class RepositoryDatabaseConnector(BasicDatabaseConnector):
    
    def __init__(self, sqlUser, sqlPassword, databaseName):
        BasicDatabaseConnector.__init__(self, sqlUser, sqlPassword, databaseName)
    
    def getImage(self, imageID):
        sqlQuery = "SELECT * FROM Images WHERE imageID = " + str(imageID)
        results = self._executeQuery(sqlQuery, False)
        (imageID, dataImagePath, osImagePath, configFilePath, groupId) = results
        data = dict()
        data["dataPath"] = dataImagePath
        data["osPath"] = osImagePath
        data["configFilePath"] = configFilePath
        data["groupID"] = groupId
        
        return data
    
    def addImage(self, imageID, compressImagePath, groupID):
        
        sqlQuery = "INSERT INTO Images(imageID, compressImagePath, groupID) VALUES (" + str(imageID) + ", '" + compressImagePath + "', " + str(groupID)
        self._executeUpdate(sqlQuery)