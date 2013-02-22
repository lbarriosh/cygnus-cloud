'''
Created on Feb 21, 2013

@author: luis
'''

from database.utils.connector import BasicDatabaseConnector
import time

class CommandsDatabaseConnector(BasicDatabaseConnector):
    
    def __init__(self, sqlUser, sqlPassword, databaseName):
        BasicDatabaseConnector.__init__(self, sqlUser, sqlPassword, databaseName)
    
    def addCommand(self, userID, commandType, arguments):
        # Get the current date
        timestamp = long(time.time() * 1e6)
        # Generate the query
        query = "INSERT INTO Command VALUES ({0}, {1}, {2}, '{3}');".format(userID, timestamp, commandType, arguments)
        self._executeUpdate(query)
        return (userID, timestamp)
        
    def popCommand(self):
        query = "SELECT * FROM Command WHERE time = (SELECT MIN(time) FROM Command) LIMIT 1;"
        result = self._executeQuery(query, True)
        userID = int(result[0])
        update = "DELETE FROM Command WHERE userID = {0} AND TIME = {1};".format(userID, result[1])
        self._executeUpdate(update)
        return (userID, result[1], int(result[2]), result[3])
    
    def addCommandOutput(self, userID, timestamp, resultType, commandOutput):
        update = "INSERT INTO CommandOutput VALUES ({0}, {1}, {2}, '{3}');".format(userID, timestamp, resultType, commandOutput)
        self._executeUpdate(update)
            
    def getCommandOutput(self, commandID):
        query = "SELECT outputType, commandOutput FROM CommandOutput WHERE userID = {0} AND time = {1};".format(commandID[0], commandID[1])
        result = self._executeQuery(query, True)
        if (result != None) :
            update = "DELETE FROM CommandOutput WHERE userID = {0} AND time = {1};".format(commandID[0], commandID[1])
            self._executeUpdate(update)
            return (int(result[0]), result[1])
        else:
            return None