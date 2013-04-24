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
        imageID = self.__connector.addImage()
        result = self.__connector.getImageData(imageID)
        expectedResult = {"compressedFilePath" : "undefined" + str(imageID), "imageStatus" : IMAGE_STATUS_T.NOT_RECEIVED}
        self.assertEquals(result, expectedResult, "addImage() error")
        
    def test_removeImage(self):
        imageID = self.__connector.addImage()
        self.__connector.removeImage(imageID)
        result = self.__connector.getImageData(imageID)
        expectedResult = None
        self.assertEquals(result, expectedResult, "removeImage() error")
        
    def test_changeImageStatus(self):
        imageID = self.__connector.addImage()
        self.__connector.changeImageStatus(imageID, IMAGE_STATUS_T.READY)
        result = self.__connector.getImageData(imageID)
        expectedResult = {"compressedFilePath" : "undefined" + str(imageID), "imageStatus" : IMAGE_STATUS_T.READY}
        self.assertEquals(result, expectedResult, "changeImageStatus() error")
        
    def test_processFinishedTransfer(self):
        imageID = self.__connector.addImage()
        self.__connector.processFinishedTransfer(str(imageID) + ".zip")
        result = self.__connector.getImageData(imageID)
        expectedResult = {"compressedFilePath" : str(imageID) + ".zip", "imageStatus" : IMAGE_STATUS_T.READY}
        self.assertEquals(result, expectedResult, "processFinishedTransfer() error")
        
        
if __name__ == "__main__":
    unittest.main()