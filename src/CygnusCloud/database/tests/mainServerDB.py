# -*- coding: UTF8 -*-
'''
    Main server database unit tests.
    @author: Adrián Fernández Hernández
    @author: Luis Barrios Hernández
    @version: 2.0
'''
import MySQLdb
import os
import unittest

from database.utils.configuration import DBConfigurator
from database.mainServer.vmServerDB import SERVER_STATE_T
from database.mainServer.vmServerDB import VMServerDatabaseConnector

class MainServerDBTests(unittest.TestCase):
    '''
        This class runs the unit tests.
    '''
    def setUp(self):
        '''
        This method will be ran before EVERY unit test.
        '''
        # Create the database
        dbConfigurator = DBConfigurator("")
        dbConfigurator.runSQLScript("./MainServerDB.sql")
        # Add a user to it
        dbConfigurator.addUser("cygnuscloud", "cygnuscloud", "MainServerDB")
        self.__connector = VMServerDatabaseConnector("cygnuscloud", "cygnuscloud", "MainServerDB")     
        self.__connector.connect()   
        
    def tearDown(self):
        '''
        This method will be ran after EVERY unit test.
        '''
        self.__connector.disconnect()
        
    def test_getBasicServerData(self):
        '''
        Retrieves basic information about a virtual machine server
        '''
        result = self.__connector.getVMServerBasicData(1)
        expectedResult = {'ServerName':'Server1', 'ServerStatus':SERVER_STATE_T.BOOTING, 
                          'ServerIP':'1.2.3.4', 'ServerPort':8080}
        self.assertEquals(result, expectedResult, 'getVMServerBasicData does not work')
        
    
    def test_getVMServerStatistics(self):
        '''
        Determines how many virtual machines are running on a virtual machine server
        '''
        result = self.__connector.getVMServerStatistics(100)
        expectedResult = {}
        self.assertEquals(result, expectedResult, 'getVMServerStatistics does not work')
        result = self.__connector.getVMServerStatistics(2)
        expectedResult = {'ActiveHosts': 10}
        self.assertEquals(result, expectedResult, 'getVMServerStatistics does not work')
        
    def test_getVMServerIDs(self):
        '''
        Obtains the registerd virtual machine servers' IDs
        '''
        result = self.__connector.getVMServerIDs()
        expectedResult = [1,2,3,4]
        self.assertEquals(result, expectedResult, 'getVMServerIDs does not work')
        
    def test_registerVMServer(self):
        '''
        Tests the registration of a new virtual machine server
        '''
        self.__connector.registerVMServer('A new server', '100.101.102.103', 89221)
        ids = self.__connector.getVMServerIDs()
        expectedIds = [1,2,3,4, ids[len(ids) - 1]]
        self.assertEquals(ids, expectedIds, 'registerVMServer does not work')
        
    def test_unregisterVMServer(self):
        '''
        Tests the deletion of a virtual machine server
        '''
        self.__connector.unregisterVMServer(1)
        ids = self.__connector.getVMServerIDs()
        expectedIds = [2,3,4]
        self.assertEquals(ids, expectedIds, 'unregisterVMServer does not work')
       
    def test_getAvailableVMServers(self):
        '''
        Tries to retrieve the virtual machine servers that can host an image.
        '''
        result = self.__connector.getAvailableVMServers(1)
        expectedResult = [2,3]
        self.assertEquals(result, expectedResult, 'getAvailableVMServers does not work')
        
    def test_updateVMServerStatus(self):
        '''
        Updates a virtual machine server's status
        '''
        self.__connector.updateVMServerStatus(1, SERVER_STATE_T.READY)
        d = self.__connector.getVMServerBasicData(1)
        self.assertEquals(d['ServerStatus'], SERVER_STATE_T.READY, "updateVMServerStatus does not work")
    
    def test_getImages(self):
        '''
        Tries to retrieve the images that can be hosted on a virtual machine server
        '''
        result = self.__connector.getImages(1)
        expectedResult = [1,2,3]
        self.assertEquals(result, expectedResult, 'getImages does not work')
        
    def test_getImageData(self):
        '''
        Tries to retrieve an image's data
        '''
        result = self.__connector.getImageData(1)
        expectedResult = {'ImageName':'Ubuntu', 'ImageDescription':'Ubuntu GNU/Linux x64'}
        self.assertEquals(result, expectedResult, 'getImageData does not work')
        
    def test_createNewImage(self):
        '''
        Tries to create a new image
        '''
        imageID = self.__connector.createNewImage('Windows XP', 'Windows XP Professional')
        result = self.__connector.getImageData(imageID)
        expectedResult = {'ImageName':'Windows XP', 'ImageDescription':'Windows XP Professional'}
        self.assertEquals(result, expectedResult, 'createNewImage does not work')
        
    def test_assignImageToServer(self):
        '''
        Tries to assign an image to a virtual machine server
        '''
        self.__connector.assignImageToServer(4, 2)
        result = self.__connector.getImages(4)
        expectedResult = [2]
        self.assertEquals(result, expectedResult, 'assignImageToServer does not work')
        
    def test_setImageData(self):
        '''
        Tries to modify an image's data
        '''
        self.__connector.setImageData(1, 'Ubuntu Natty', 'Ubuntu GNU/Linux 12.04 x64')
        result = self.__connector.getImageData(1)
        expectedResult = {'ImageName':'Ubuntu Natty', 'ImageDescription':'Ubuntu GNU/Linux 12.04 x64'}
        self.assertEquals(result, expectedResult, 'setImageData does not work')
        
    def test_setServerBasicData(self):
        '''
        Tries to modify a virtual machine server's data
        '''
        self.__connector.setServerBasicData(1, 'Foo', SERVER_STATE_T.BOOTING, '192.168.1.1', 9000)
        result = self.__connector.getVMServerBasicData(1)
        expectedResult = {'ServerName':'Foo', 'ServerStatus':SERVER_STATE_T.BOOTING, 
                          'ServerIP':'192.168.1.1', 'ServerPort':9000}
        self.assertEquals(result, expectedResult, 'setServerBasicData does not work')
        
if __name__ == "__main__":
    unittest.main()
