
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
    
    def test_getAvailableImageIDs(self):
        # Instanciamos la clase
        l1 = self.__dbConnector.getAvailableImageIDs()
        l2 = [1, 2, 3, 4]
        self.assertEquals(l1, l2, "The image ID lists do not match")
        
    def test_getDomainNameFromImageID(self):
        # Instanciamos la clase
        n1 = self.__dbConnector.getDomainNameFromImageID(1)
        n2 = "VMName1"
        self.assertEquals(n1, n2, "Not same image name")
        
    def test_getDataImagePathFromImageID(self):
        # Instanciamos la clase
        n1 = self.__dbConnector.getDataImagePathFromImageID(1)
        n2 = "./VMName1/"
        self.assertEquals(n1, n2, "Not same image path")   
        
    def test_getDefinitionFilePathFromVNCPort(self):
        # Instanciamos la clase
        n1 = self.__dbConnector.getDefinitionFilePathFromVNCPort(1)
        n2 = "./VMName1/"
        self.assertEquals(n1, n2, "Not same image path")

    def test_setDataImagePath(self):
        # Instanciamos la clase
        self.__dbConnector.setDataImagePath(1, "./VMName1Test/")
        n1 = self.__dbConnector.getDataImagePathFromImageID(1)
        n2 = "./VMName1Test/"
        self.assertEquals(n1, n2, "Not change image path")  
        
    def test_createImage(self):
        # Instanciamos la clase
        imageId = self.__dbConnector.createImage(123, "VMNameTest", "./VMNameTest/", "./OSImagePath1", "./VMNameTest/")
        self.assertTrue(self.__dbConnector.doesImageExist(imageId), "Not image regist")  
        self.__dbConnector.deleteImage(imageId)    
    
    def test_getVNCPortsInUse(self):
        # Instanciamos la clase
        l1 = self.__dbConnector.getVNCPortsInUse()
        l2 = [1, 2, 3, 4]
        self.assertEquals(l1, l2, "Not same ports") 
        
    def test_getUserIDs(self):
        # Instanciamos la clase
        l1 = self.__dbConnector.getUserIDs()
        l2 = [1, 2, 3]
        self.assertEquals(l1, l2, "Not same users")

    def test_getAssignedVM(self):
        # Instanciamos la clase
        n1 = self.__dbConnector.getVMIDFromVNCPort(1)
        n2 = 1
        self.assertEquals(n1, n2, "Not same VM") 
        
    def test_getVMNameFromVNCPort(self):
        # Instanciamos la clase
        n1 = self.__dbConnector.getVMNameFromVNCPort(2)
        n2 = "VMName1"
        self.assertEquals(n1, n2, "Not same VM Name")   
        
    def test_getDataImagePathFromVNCPort(self):
        # Instanciamos la clase
        n1 = self.__dbConnector.getDataImagePathFromVNCPort(2)
        n2 = "./VMNameCopy1"
        self.assertEquals(n1, n2, "Not same VM path")
 
    def test_getMACAddressFromVNCPort(self):
        # Instanciamos la clase
        n1 = self.__dbConnector.getMACAddressFromVNCPort(3)
        n2 = "2C:00:00:00:00:02"
        self.assertEquals(n1, n2, "Not same VM MAC") 
        
    def test_getVNCPasswordFromVNCPort(self):
        # Instanciamos la clase
        n1 = self.__dbConnector.getVNCPasswordFromVNCPort(3)
        n2 = "1234567890Test"
        self.assertEquals(n1, n2, "Not same VM Pass")
        
    def test_registerVMResources(self):
        # Instanciamos la clase
        portId = self.__dbConnector.registerVMResources("VMName123", 2,
            23, "testPass", 3, 100, "./VMNameCopyTest", "./OSImagePath1", "testMac", "testUUID")
        self.assertTrue(self.__dbConnector.doesVMExist(portId), "Not VM register") 
        self.__dbConnector.unregisterVMResources("VMName123")
        self.assertFalse(self.__dbConnector.doesVMExist(23), "Not VM unregisted")
        
    def test_extractFreeMACandUUID(self):
        # Instanciamos la clase
        (_uuid1, mac1) = self.__dbConnector.extractFreeMACAndUUID()
        (_uuid2, mac2) = ("9a47c734-5e5f-11e2-981b-001f16b99e1d", "2C:00:00:00:00:00")
        self.assertEquals(mac1, mac2, "Not same MAC")
    
    def test_extractFreeVNCPort(self):
        # Instanciamos la clase
        vncPort1 = self.__dbConnector.extractFreeVNCPort()
        vncPort2 = (15000)
        self.assertEquals(vncPort1, vncPort2, "Not same VNCPort")
             
    def test_getVMsConnectionData(self):
        result = self.__dbConnector.getVMsConnectionData()
        expectedResult = [
                          {"UserID": 1, "VMID": 1, "VMName" :"VMName11", "VNCPort" : 1, "VNCPass" : "1234567890"},
                          {"UserID": 1, "VMID": 1, "VMName" :"VMName22", "VNCPort" : 2, "VNCPass" : "1234567890"},
                          {"UserID": 2, "VMID": 1, "VMName" :"VMName33", "VNCPort" : 3, "VNCPass" : "1234567890Test"},
                          {"UserID": 3, "VMID": 1, "VMName" :"VMName44", "VNCPort" : 4, "VNCPass" : "1234567890"}
                          ]
        self.assertEquals(result, expectedResult, "getVMsConnectionData does not work")
        
    def test_getVMBootCommand(self):
        result = self.__dbConnector.getVMBootCommand("VMName44")
        expectedResult = "123"
        self.assertEquals(result, expectedResult, "getVMBootCommand does not work")
        result = self.__dbConnector.getVMBootCommand("VMName33")
        self.assertEquals(result, None, "getVMBootCommand does not work")
        
    def test_addVMBootCommand(self):
        self.__dbConnector.addVMBootCommand("VMName33", "1234")
        result = self.__dbConnector.getVMBootCommand("VMName33")
        self.assertEquals(result, "1234", "addVMBootCommand does not work")
        
    def test_getDomainImageDataPath(self):
        result = self.__dbConnector.getDomainDataImagePathFromDomainName("VMName33")
        expectedResult = "./VMNameCopy2"
        self.assertEquals(result, expectedResult, "getDomainDataImagePathFromDomainName does not work")
        
    def test_getOSImagePathFromImageID(self):
        result = self.__dbConnector.getOsImagePathFromImageId(1)
        expectedResult = "./VMName1/"
        self.assertEquals(result, expectedResult, "getOSImageDataPath does not work")  
        
    def test_getRegisteredDomainNames(self):
        result = self.__dbConnector.getRegisteredDomainNames()
        expectedResult = ["VMName11", "VMName22", "VMName33", "VMName44"]
        self.assertEquals(result, expectedResult, "getActiveDomainNames() does not work")      
        
if __name__ == "__main__":
    unittest.main()
