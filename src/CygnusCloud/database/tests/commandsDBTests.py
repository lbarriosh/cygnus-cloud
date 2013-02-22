'''
Created on Feb 21, 2013

@author: luis
'''

import unittest

from database.commands.commandsDatabaseConnector import CommandsDatabaseConnector
from database.utils.configuration import DBConfigurator


class CommandsDBTests(unittest.TestCase):
    
    '''
        This class runs the unit tests.
    '''
    def setUp(self):
        '''
        This method will be ran before EVERY unit test.
        '''
        # Create the database
        self.__dbConfigurator = DBConfigurator("")
        self.__dbConfigurator.runSQLScript("CommandsDBTest", "./CommandsDBTest.sql")
        # Add a user to it
        self.__dbConfigurator.addUser("cygnuscloud", "cygnuscloud", "CommandsDBTest")
        self.__connector = CommandsDatabaseConnector("cygnuscloud", "cygnuscloud", "CommandsDBTest")     
        self.__connector.connect()   
        
    def tearDown(self):
        '''
        This method will be ran after EVERY unit test.
        '''
        self.__connector.disconnect()
        self.__dbConfigurator.dropDatabase("CommandsDBTest")
        
    def test_addAndRemoveCommands(self):
        self.__connector.addCommand(1, 0, "command arguments")
        result = self.__connector.popCommand()
        expectedResult = (1, 0, 'command arguments')
        self.assertEquals(result[0], expectedResult[0], "either addCommand or popCommand does not work")
        self.assertEquals(result[2], expectedResult[1], "either addCommand or popCommand does not work")
        self.assertEquals(result[3], expectedResult[2], "either addCommand or popCommand does not work")
        self.__connector.addCommand(1, 0, "command1 arguments")
        self.__connector.addCommand(1, 1, "command2 arguments")
        self.__connector.addCommand(1, 3, "command3 arguments")
        self.__connector.addCommand(2, 2, "command4 arguments")
        self.__connector.addCommand(3, 3, "command5 arguments")
        expectedResults = [(1, 0, "command1 arguments"), (1, 1, "command2 arguments"), (1, 3, "command3 arguments"),
                           (2, 2, "command4 arguments"), (3, 3, "command5 arguments")]
        for expectedResult in expectedResults :
            result = self.__connector.popCommand()
            self.assertEquals(result[0], expectedResult[0], "either addCommand or popCommand does not work")
            self.assertEquals(result[2], expectedResult[1], "either addCommand or popCommand does not work")
            self.assertEquals(result[3], expectedResult[2], "either addCommand or popCommand does not work")
            
    def test_addAndRemoveCommandOutputs(self):
        self.__connector.addCommandOutput(1, 1, 0, "commandOutput")
        result = self.__connector.getCommandOutput((1, 1))
        expectedResult = (0, "commandOutput")
        self.assertEquals(result, expectedResult, "either addCommandOutput or getCommandOutput does not work")
       
    
if __name__ == "__main__" :
    unittest.main()
    