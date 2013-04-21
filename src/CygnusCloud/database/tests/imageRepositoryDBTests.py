# -*- coding: UTF8 -*-
'''
    Main server database unit tests.
    @author: Adrián Fernández Hernández
    @author: Luis Barrios Hernández
    @version: 2.2
'''
import unittest

from database.utils.configuration import DBConfigurator
from database.imageRepository.imageRepositoryDB import ImageRepositoryDBConnector, IMAGE_STATUS_T

class ClusterServerDBTests(unittest.TestCase):
    '''
        This class runs the unit tests.
    '''
    def setUp(self):
        '''
        This method will be ran before EVERY unit test.
        '''
        # Create the database
        dbConfigurator = DBConfigurator("")
        dbConfigurator.runSQLScript("ImageRepositoryDBTest", "./ImageRepositoryDBTest.sql")
        # Add a user to it
        dbConfigurator.addUser("cygnuscloud", "cygnuscloud", "ImageRepositoryDBTest")
        self.__connector = ImageRepositoryDBConnector("cygnuscloud", "cygnuscloud", "ImageRepositoryDBTest")     
        self.__connector.connect()   
        
    def tearDown(self):
        '''
        This method will be ran after EVERY unit test.
        '''
        self.__connector.disconnect()
        dbConfigurator = DBConfigurator("")
        dbConfigurator.dropDatabase("ImageRepositoryDBTest")
        
    def test_addImage(self):
        imageID = self.__connector.addImage(1)
        result = self.__connector.getImageData(imageID)
        expectedResult = {"compressedFilePath" : "undefined", "imageStatus" : IMAGE_STATUS_T.NOT_RECEIVED, "groupID":1}
        self.assertEquals(result, expectedResult, "addImage() error")
        
    def test_removeImage(self):
        imageID = self.__connector.addImage(1)
        self.__connector.removeImage(imageID)
        result = self.__connector.getImageData(imageID)
        expectedResult = None
        self.assertEquals(result, expectedResult, "removeImage() error")
        
if __name__ == "__main__":
    unittest.main()