# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: commandsDatabaseConnector.py    
    Version: 2.0
    Description: commands database connector
    
    Copyright 2012-13 Luis Barrios Hernández, Adrián Fernández Hernández,
        Samuel Guayerbas Martín
        
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
'''

from ccutils.databases.connector import BasicDBConnector
import time

class CommandsDatabaseConnector(BasicDBConnector):
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
        BasicDBConnector.__init__(self, sqlUser, sqlPassword, statusDBName)
        self.__minCommandInterval = minCommandInterval
    
    def addCommand(self, userID, commandType, arguments, timestamp = None):
        """
        Inserts a command in the commands table.
        Args:
            userID: an user ID. This user has requested the execution of the new command.
            commandType: the new command's type.
            arguments: the new command's arguments.
            timestamp: the timestamp to use. If it's none, the current time will be used.
        Returns: None if the command could not be scheduled, and the command's ID if everything
        went OK. 
        @attention: DO NOT rely on the command ID's internal representation: it can change without
        prior notice.
        """
        if (timestamp == None) :
            # Get the current date
            timestamp = time.time()
            # Get the newest command that was submitted by the user
            query = "SELECT MIN(time) FROM PendingCommand WHERE userID = {0};".format(userID)
            result = self._executeQuery(query, True)
            if (result == None or (timestamp - result >= self.__minCommandInterval))  :
                # Generate the updates
                command = "INSERT INTO PendingCommand VALUES ({0}, {1}, {2}, '{3}')".format(userID, timestamp, commandType, arguments)
                self._executeUpdate(command)    
                command = "INSERT INTO QueuedCommand VALUES ({0}, {1});".format(userID, timestamp)
                self._executeUpdate(command)
                return (userID, timestamp)
            else :
                return None
        else :
            command = "INSERT INTO PendingCommand VALUES ({0}, {1}, {2}, '{3}')".format(userID, timestamp, commandType, arguments)
            self._executeUpdate(command)    
            command = "INSERT INTO QueuedCommand VALUES ({0}, {1});".format(userID, timestamp)
            self._executeUpdate(command)
            return (userID, timestamp)
        
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
        commandData = self.getCommandData((userID, result[1]))
        return ((userID, result[1]), int(commandData["CommandType"]), commandData["CommandArgs"])
    
    def getCommandData(self, commandID):
        """
        Returns a command's data
        Args:
            commandID: a commandID:
        Returns:
            the command's data
        """
        query = "SELECT commandType, commandArgs FROM PendingCommand WHERE userID = {0} AND time = {1};".format(commandID[0], commandID[1])
        result = self._executeQuery(query, True)     
        return {"CommandType": result[0], "CommandArgs": result[1]}   
    
    def addCommandOutput(self, commandID, outputType, commandOutput, isNotification = False):
        """
        Registers a command's output
        Args:
            commandID: the command's unique identifier.
            outputType: the command output's type
            commandOutput: the command's output
        Returns:
            Nothing
        """
        if (isNotification) :
            flag = 1
        else :
            flag = 0
        update = "REPLACE RunCommandOutput VALUES ({0}, {1}, {2}, '{3}', {4});".format(commandID[0], commandID[1], outputType, commandOutput, flag)
        self._executeUpdate(update)
        update = "DELETE FROM PendingCommand WHERE userID = {0} AND time = {1};".format(commandID[0], commandID[1])
        self._executeUpdate(update)
        
    def removeOldCommands(self, timeout):     
        """
        Removes the old commands from the database
        Args:
            timeout: the timeout to use
        Returns:
            A list containing the removed commands' IDs
        """   
        query = "SELECT * FROM PendingCommand WHERE time - {0} >= {1};".format(time.time(), timeout)
        results = self._executeQuery(query, False)
        if (results == None) :
            return []
        oldCommands = []
        for row in results :
            oldCommands.append((row[0], row[1]), int(row[2]), row[3])
            update = "DELETE FROM PendingCommand WHERE userID = {0} AND time = {1};".format(row[0], row[1])
            self._executeUpdate(update)
        return oldCommands        
        
    def removeExecutedCommand(self, commandID):
        """
        Removes an executed command from the database
        Args:
            commandID: the executed command's ID
        Returns:
            Nothing
        """
        data = self.getCommandData(commandID)
        update = "DELETE FROM PendingCommand WHERE userID = {0} AND time = {1};".format(commandID[0], commandID[1])
        self._executeUpdate(update)
        return data
            
    def getCommandOutput(self, commandID):
        """
        Removes the requested command ouput from the database and returns it.
        Args:
            commandID: the command's unique identifier
        Returns:
            A tuple (command output type, command ouput) containig the command's output type and its content.
        """
        query = "SELECT outputType, commandOutput FROM RunCommandOutput WHERE userID = {0} AND time = {1};".format(commandID[0], commandID[1])
        result = self._executeQuery(query, True)
        if (result != None) :
            update = "DELETE FROM RunCommandOutput WHERE userID = {0} AND time = {1};".format(commandID[0], commandID[1])
            self._executeUpdate(update)
            return (int(result[0]), result[1])
        else:
            return None
        
    def getPendingNotifications(self, userID):
        """
        Returns an user's pending notifications
        Args:
            userID: an userID
        Returns:
            A list of strings containing the user's pending notifications.
        """
        query = "SELECT MAX(time) FROM RunCommandOutput WHERE userID = {0} AND isNotification = 1".format(userID)
        max_time = self._executeQuery(query, True)
        if (max_time == None) :
            return []
        
        query = "SELECT outputType, commandOutput FROM RunCommandOutput WHERE userID = {0} AND isNotification = 1 AND time <= {1};"\
            .format(userID, max_time)
        results = self._executeQuery(query, False)
           
        update = "DELETE FROM RunCommandOutput WHERE userID = {0} AND isNotification = 1 AND time <= {1};".format(userID, max_time)
        self._executeUpdate(update)
            
        return results
    
    def countPendingNotifications(self, userID):
        """
        Counts an user's pending notifications
        Args:
            userID: an user ID
        Returns:
            the given user's pending notification number
        """
        query = "SELECT MAX(time) FROM RunCommandOutput WHERE userID = {0} AND isNotification = 1".format(userID)
        max_time = self._executeQuery(query, True)
        if (max_time == None) :
            return 0
         
        query = "SELECT COUNT(*) FROM RunCommandOutput WHERE userID = {0} AND isNotification = 1 AND time <= {1};" \
            .format(userID, max_time)
        count = self._executeQuery(query, True)             
        return count
        
    def isRunning(self, commandID):
        """
        Determines whether a command is running or not.
        Args:
            commandID: the command's unique identifier
        Returns:
            True if the command is still running, and false if it's not.
        """
        query = "SELECT * FROM PendingCommand WHERE userID = {0} AND time = {1};"\
            .format(commandID[0], commandID[1])
        result = self._executeQuery(query, True)
        return result != None