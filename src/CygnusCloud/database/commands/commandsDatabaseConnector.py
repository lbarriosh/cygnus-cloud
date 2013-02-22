# -*- coding: UTF8 -*-
'''
The commands database connector
@author: Luis Barrios Hernández
@version: 1.1
'''

from database.utils.connector import BasicDatabaseConnector
import time

class CommandsDatabaseConnector(BasicDatabaseConnector):
    """
    These objects register and delete commands (and their outputs)
    in the commands database.
    """
    def __init__(self, sqlUser, sqlPassword, databaseName):
        """
        Initializes the connector's state
        Args:
            sqlUser: the mysql user to use
            sqlPassword: the mysql password to use
            databaseName: the mysql database name
        """
        BasicDatabaseConnector.__init__(self, sqlUser, sqlPassword, databaseName)
    
    def addCommand(self, userID, commandType, arguments):
        """
        Inserts a command in the commands table.
        Args:
            userID: an user ID. This user has requested the execution of the new command.
            commandType: the new command's type.
            arguments: the new command's arguments.
        Returns:
            the command's ID. 
        @attention: DO NOT rely on the command ID's internal representation: it can change without
        prior notice.
        """
        # Get the current date
        timestamp = long(time.time() * 1e6)
        # Generate the query
        query = "INSERT INTO Command VALUES ({0}, {1}, {2}, '{3}');".format(userID, timestamp, commandType, arguments)
        self._executeUpdate(query)
        return (userID, timestamp)
        
    def popCommand(self):
        """
        Removes the oldest command from the commands table and returns it
        Args:
            None
        Returns:
            The tuple (commandID, commandType, commandArguments)
        """
        query = "SELECT * FROM Command WHERE time = (SELECT MIN(time) FROM Command) LIMIT 1;"
        result = self._executeQuery(query, True)
        userID = int(result[0])
        update = "DELETE FROM Command WHERE userID = {0} AND TIME = {1};".format(userID, result[1])
        self._executeUpdate(update)
        return ((userID, result[1]), int(result[2]), result[3])
    
    def addCommandOutput(self, commandID, outputType, commandOutput):
        """
        Registers a command's output
        Args:
            commandID: the command's unique identifier.
            outputType: the command output's type
            commandOutput: the command's output
        Returns:
            Nothing
        """
        update = "INSERT INTO CommandOutput VALUES ({0}, {1}, {2}, '{3}');".format(commandID[0], commandID[1], outputType, commandOutput)
        self._executeUpdate(update)
            
    def getCommandOutput(self, commandID):
        """
        Removes the requested command ouput from the database and returns it.
        Args:
            commandID: the command's unique identifier
        Returns:
            A tuple (command output type, command ouput) containig the command's output type and its content.
        """
        query = "SELECT outputType, commandOutput FROM CommandOutput WHERE userID = {0} AND time = {1};".format(commandID[0], commandID[1])
        result = self._executeQuery(query, True)
        if (result != None) :
            update = "DELETE FROM CommandOutput WHERE userID = {0} AND time = {1};".format(commandID[0], commandID[1])
            self._executeUpdate(update)
            return (int(result[0]), result[1])
        else:
            return None