
# -*- coding: UTF8 -*-
import unittest

from database.vmServer.vmServerDB import VMServerDBConnector
from database.utils.configuration import DBConfigurator

class DBWebServerTests(unittest.TestCase):
    '''
        Clase encargada de realizar los test unitarios asociados 
    '''
    
    def setUp(self):
        self.__dbConfigurator = DBConfigurator("")
        self.__dbConfigurator.runSQLScript("VMServerDBTest", "./VMServerDBTest.sql")
        self.__dbConfigurator.addUser("CygnusCloud", "cygnuscloud2012", "VMServerDBTest", True)
        self.__dbConnector = VMServerDBConnector("CygnusCloud", "cygnuscloud2012", "VMServerDBTest")
    
    def tearDown(self):
        self.__dbConnector.disconnect()
        self.__dbConfigurator.dropDatabase("VMServerDBTest")
    
    def test_getImages(self):
        # Instanciamos la clase
        l1 = self.__dbConnector.getImageIDs()
        l2 = [1, 2, 3, 4]
        self.assertEquals(l1, l2, "getImageIDs() error")
        
    def test_getName(self):
        # Instanciamos la clase
        n1 = self.__dbConnector.getImageName(1)
        n2 = "VMName1"
        self.assertEquals(n1, n2, "getImageName() error")
        
    def test_getImagePath(self):
        # Instanciamos la clase
        n1 = self.__dbConnector.getImagePath(1)
        n2 = "./VMName1/"
        self.assertEquals(n1, n2, "getImagePath() error")   
        
    def test_getFileConfigPath(self):
        # Instanciamos la clase
        n1 = self.__dbConnector.getImgDefFilePath(1)
        n2 = "./VMName1/"
        self.assertEquals(n1, n2, "getImgDefFilePath() error")

    def test_setDataImagePath(self):
        # Instanciamos la clase
        self.__dbConnector.setDataImagePath(1, "./VMName1Test/")
        n1 = self.__dbConnector.getImagePath(1)
        n2 = "./VMName1Test/"
        self.assertEquals(n1, n2, "setDataImagePath() error")  
        
    def test_createImage(self):
        # Instanciamos la clase
        imageID = 123
        self.__dbConnector.createImage(123, "VMNameTest", "./VMNameTest/", "./OSImagePath1", "./VMNameTest/", 0)
        self.assertTrue(self.__dbConnector.doesImageExist(imageID), "createImage() error")  
        self.__dbConnector.deleteImage(imageID)    
    
    def test_getRunningPorts(self):
        # Instanciamos la clase
        l1 = self.__dbConnector.getActivePorts()
        l2 = [1, 2, 3, 4]
        self.assertEquals(l1, l2, "getActivePorts() error") 
        
    def test_getUsers(self):
        # Instanciamos la clase
        l1 = self.__dbConnector.getVMOwnerIDs()
        l2 = [1, 2, 3]
        self.assertEquals(l1, l2, "getVMOwnerIDs() error")

    def test_getAssignedVM(self):
        # Instanciamos la clase
        n1 = self.__dbConnector.getImgIDFromVNCPort(1)
        n2 = 1
        self.assertEquals(n1, n2, "getImgIDFromVNCPort() error") 
        
    def test_getImageNameFromDomainName(self):
        # Instanciamos la clase
        n1 = self.__dbConnector.getImageNameFromDomainName(2)
        n2 = "VMName1"
        self.assertEquals(n1, n2, "getImageNameFromDomainName() error")   
        
    def test_getDomainDataImagePath(self):
        # Instanciamos la clase
        n1 = self.__dbConnector.getDomainDataImagePath(2)
        n2 = "./VMNameCopy1"
        self.assertEquals(n1, n2, "getDomainDataImagePath() error")
 
    def test_getMACAddressFromDomainName(self):
        # Instanciamos la clase
        n1 = self.__dbConnector.getMACAddressFromVNCPort(3)
        n2 = "2C:00:00:00:00:02"
        self.assertEquals(n1, n2, "getMACAddressFromVNCPort() error") 
        
    def test_getPasswordInDomain(self):
        # Instanciamos la clase
        n1 = self.__dbConnector.getVNCPassword(3)
        n2 = "1234567890Test"
        self.assertEquals(n1, n2, "getVNCPassword() error")
        
    def test_registerVMResources(self):
        # Instanciamos la clase
        portId = self.__dbConnector.registerVMResources("VMName123", 2,
            23, "testPass", 3, 100, "./VMNameCopyTest", "./OSImagePath1", "testMac", "testUUID")
        self.assertTrue(self.__dbConnector.doesVMExist(portId), "Not VM register") 
        self.__dbConnector.unregisterVMResources("VMName123")
        self.assertFalse(self.__dbConnector.doesVMExist(23), "registerVMResources() error")
        
    def test_extractFreeMACandUUID(self):
        # Instanciamos la clase
        (_uuid1, mac1) = self.__dbConnector.extractFreeMACAndUUID()
        (_uuid2, mac2) = ("9a47c734-5e5f-11e2-981b-001f16b99e1d", "2C:00:00:00:00:00")
        self.assertEquals(mac1, mac2, "extractFreeMACAndUUID() error")
    
    def test_extractFreeVNCPort(self):
        # Instanciamos la clase
        vncPort1 = self.__dbConnector.extractFreeVNCPort()
        vncPort2 = (15000)
        self.assertEquals(vncPort1, vncPort2, "extractFreeVNCPort() error")
             
    def test_getDomainsConnectionData(self):
        result = self.__dbConnector.getDomainsConnectionData()
        expectedResult = [
                          {"DomainID": "Command1", "UserID": 1, "ImageID": 1, "VMName" :"VMName11", "VNCPort" : 1, "VNCPass" : "12134567890"},
                          {"DomainID": "Command2", "UserID": 1, "ImageID": 1, "VMName" :"VMName22", "VNCPort" : 2, "VNCPass" : "1234567890"},
                          {"DomainID": "Command3", "UserID": 2, "ImageID": 1, "VMName" :"VMName33", "VNCPort" : 3, "VNCPass" : "1234567890Test"},
                          {"DomainID": "Command4", "UserID": 3, "ImageID": 1, "VMName" :"VMName44", "VNCPort" : 4, "VNCPass" : "1234567890"}
                          ]
        self.assertEquals(result, expectedResult, "getDomainsConnectionData() error")
        
    def test_getVMBootCommand(self):
        result = self.__dbConnector.getVMBootCommand("VMName44")
        expectedResult = "Command4"
        self.assertEquals(result, expectedResult, "getVMBootCommand() error")
        result = self.__dbConnector.getVMBootCommand("VMName33")
        self.assertEquals(result, "Command3", "getVMBootCommand() error")
        
    def test_getDomainNameFromVMBootCommand(self):
        result = self.__dbConnector.getDomainNameFromVMBootCommand("Command4")
        expectedResult = "VMName44"
        self.assertEquals(result, expectedResult, "getDomainNameFromVMBootCommand() error")
        
    def test_addVMBootCommand(self):
        self.__dbConnector.registerVMResources("VMName55", 1, 1, "123", 1, 1, "data", "os", "mac", "uuid")
        self.__dbConnector.addVMBootCommand("VMName55", "1234")
        result = self.__dbConnector.getVMBootCommand("VMName55")
        self.assertEquals(result, "1234", "addVMBootCommand() error")
        
    def test_getDataImagePath(self):
        result = self.__dbConnector.getDataImagePath("VMName33")
        expectedResult = "./VMNameCopy2"
        self.assertEquals(result, expectedResult, "getDataImagePath() error")
        
    def test_getOSImagePath(self):
        result = self.__dbConnector.getOSImagePath(1)
        expectedResult = "./VMName1/"
        self.assertEquals(result, expectedResult, "getOSImagePath() error")  
        
    def test_getRegisteredDomainNames(self):
        result = self.__dbConnector.getRegisteredDomainNames()
        expectedResult = ["VMName11", "VMName22", "VMName33", "VMName44"]
        self.assertEquals(result, expectedResult, "getRegisteredDomainNames() error")      
        
    def test_getActiveDomainUIDs(self):
        result = self.__dbConnector.getActiveDomainUIDs()
        expectedResult =  ["Command1", "Command2", "Command3", "Command4"]
        self.assertEquals(result, expectedResult, "getActiveDomainUIDs() error")        
        
    def test_getBootableFlag(self):
        result = self.__dbConnector.getBootableFlag(2)
        expectedResult = True
        self.assertEquals(result, expectedResult, "getBootableFlag() does not work")
        
if __name__ == "__main__":
    unittest.main()
