# -*- coding: UTF8 -*-
'''
Commands database connector unit tests.
@author: Luis Barrios Hernández
@version: 1.1
'''

import unittest

from clusterEndpoint.databases.commandsDatabaseConnector import CommandsDatabaseConnector
from ccutils.databases.configuration import DBConfigurator

class CommandsDBTests(unittest.TestCase):
    
    def setUp(self):
        # Create the database
        self.__dbConfigurator = DBConfigurator("")
        self.__dbConfigurator.runSQLScript("CommandsDBTest", "./CommandsDBTest.sql")
        # Add a user to it
        self.__dbConfigurator.addUser("cygnuscloud", "cygnuscloud", "CommandsDBTest")
        self.__connector = CommandsDatabaseConnector("cygnuscloud", "cygnuscloud", "CommandsDBTest", 1)    
        
    def tearDown(self):
        #self.__dbConfigurator.dropDatabase("CommandsDBTest")
        pass
        
    def test_addAndRemoveCommands(self):
        self.__connector.addCommand(1, 0, "command arguments")
        result = self.__connector.popCommand()
        expectedResult = (1, 0, 'command arguments')
        self.assertEquals(result[0][0], expectedResult[0], "either addCommand or popCommand does not work")
        self.assertEquals(result[1], expectedResult[1], "either addCommand or popCommand does not work")
        self.assertEquals(result[2], expectedResult[2], "either addCommand or popCommand does not work")
        result = self.__connector.addCommand(1, 1, "command2 arguments")
        self.assertEquals(result, None, "addCommand does not work")
        self.__connector.addCommand(2, 2, "command4 arguments")
        self.__connector.addCommand(3, 3, "command5 arguments")
        expectedResults = [(2, 2, "command4 arguments"), (3, 3, "command5 arguments")]
        for expectedResult in expectedResults :
            result = self.__connector.popCommand()
            self.assertEquals(result[0][0], expectedResult[0], "either addCommand or popCommand does not work")
            self.assertEquals(result[1], expectedResult[1], "either addCommand or popCommand does not work")
            self.assertEquals(result[2], expectedResult[2], "either addCommand or popCommand does not work")
            
    def test_addAndRemoveCommandOutputs(self):
        commandID = self.__connector.addCommand(1, 0, "command arguments")
        self.__connector.popCommand()
        self.__connector.addCommandOutput(commandID, 0, "commandOutput")
        result = self.__connector.getCommandOutput(commandID)
        expectedResult = (0, "commandOutput")
        self.assertEquals(result, expectedResult, "either addCommandOutput or getCommandOutput does not work")       

    def test_getPendingNotifications(self):
        commandID = self.__connector.addCommand(1, 0, "commandArguments")
        self.__connector.popCommand()
        self.__connector.addCommandOutput(commandID, 0, "Args1", False, True)
        commandID = self.__connector.addCommand(1, 0, "commandArguments1")
        self.__connector.popCommand()
        self.__connector.addCommandOutput(commandID, 0, "Args2", False, True)
        result = self.__connector.getPendingNotifications(1)
        expectedResult = [(0, u'Args1'), (0, u'Args2')]
        self.assertEquals(result, expectedResult, "getPendingNotifications() error")
        
    
if __name__ == "__main__" :
    unittest.main()
    