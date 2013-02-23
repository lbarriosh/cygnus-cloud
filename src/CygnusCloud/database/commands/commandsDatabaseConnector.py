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
    def __init__(self, sqlUser, sqlPassword, statusDBName, minCommandInterval):
        """
        Initializes the connector's state
        Args:
            sqlUser: the mysql user to use
            sqlPassword: the mysql password to use
            statusDBName: the mysql database name
            minCommandInterval: the time interval that separates two requests
            sent by the same user.
        """
        BasicDatabaseConnector.__init__(self, sqlUser, sqlPassword, statusDBName)
        self.__minCommandInterval = minCommandInterval
    
    def addCommand(self, userID, commandType, arguments):
        """
        Inserts a command in the commands table.
        Args:
            userID: an user ID. This user has requested the execution of the new command.
            commandType: the new command's type.
            arguments: the new command's arguments.
        Returns: None if the command could not be scheduled, and the command's ID if everything
        went OK. 
        @attention: DO NOT rely on the command ID's internal representation: it can change without
        prior notice.
        """
        # Get the current date
        timestamp = time.time()
        # Get the newest command that was submitted by the user
        query = "SELECT MIN(time) FROM PendingCommand WHERE userID = {0};".format(userID)
        result = self._executeQuery(query, True)[0]
        if (result == None or (timestamp - result >= self.__minCommandInterval))  :
            # Generate the updates
            command = "INSERT INTO PendingCommand VALUES ({0}, {1})".format(userID, timestamp)
            self._executeUpdate(command)
            command = "INSERT INTO QueuedCommand VALUES ({0}, {1}, {2}, '{3}');".format(userID, timestamp, commandType, arguments)
            self._executeUpdate(command)
            return (userID, timestamp)
        else :
            return None
        
    def popCommand(self):
        """
        Removes the oldest command from the commands table and returns it
        Args:
            None
        Returns:
            The tuple (commandID, commandType, commandArguments)
        """
        query = "SELECT * FROM QueuedCommand WHERE time = (SELECT MIN(time) FROM QueuedCommand) LIMIT 1;"
        result = self._executeQuery(query, True)
        if (result == None) :
            return None     
        userID = int(result[0])
        update = "DELETE FROM QueuedCommand WHERE userID = {0} AND TIME = {1};".format(userID, result[1])
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
        update = "DELETE FROM PendingCommand WHERE userID = {0} AND time = {1};".format(commandID[0], commandID[1])
        self._executeUpdate(update)
        update = "INSERT INTO RunCommandOutput VALUES ({0}, {1}, {2}, '{3}');".format(commandID[0], commandID[1], outputType, commandOutput)
        self._executeUpdate(update)
            
    def getCommandOutput(self, commandID):
        """
        Removes the requested command ouput from the database and returns it.
        Args:
            commandID: the command's unique identifier
        Returns:
            A tuple (command output type, command ouput) containig the command's output type and its content.
        """
        print commandID
        query = "SELECT outputType, commandOutput FROM RunCommandOutput WHERE userID = {0} AND time = {1};".format(commandID[0], commandID[1])
        result = self._executeQuery(query, True)
        if (result != None) :
            update = "DELETE FROM RunCommandOutput WHERE userID = {0} AND time = {1};".format(commandID[0], commandID[1])
            self._executeUpdate(update)
            return (int(result[0]), result[1])
        else:
            return None