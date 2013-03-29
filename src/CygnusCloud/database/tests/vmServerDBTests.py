
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
        self.__dbConnector = VMServerDBConnector("CygnusCloud","cygnuscloud2012","VMServerDBTest")
    
    def tearDown(self):
        self.__dbConnector.disconnect()
        self.__dbConfigurator.dropDatabase("VMServerDBTest")
    
    def test_getImages(self):
        #Instanciamos la clase
        l1 = self.__dbConnector.getImages()
        l2 = [1,2,3,4]
        self.assertEquals(l1, l2, "Not same images")
        
    def test_getName(self):
        #Instanciamos la clase
        n1 = self.__dbConnector.getName(1)
        n2 = "VMName1"
        self.assertEquals(n1, n2, "Not same image name")
        
    def test_getImagePath(self):
        #Instanciamos la clase
        n1 = self.__dbConnector.getImagePath(1)
        n2 = "./VMName1/"
        self.assertEquals(n1, n2, "Not same image path")   
        
    def test_getFileConfigPath(self):
        #Instanciamos la clase
        n1 = self.__dbConnector.getFileConfigPath(1)
        n2 = "./VMName1/"
        self.assertEquals(n1, n2, "Not same image path")

    def test_setImagePath(self):
        #Instanciamos la clase
        self.__dbConnector.setImagePath(1,"./VMName1Test/")
        n1 = self.__dbConnector.getImagePath(1)
        n2 = "./VMName1Test/"
        self.assertEquals(n1, n2, "Not change image path")  
        
    def test_createImage(self):
        #Instanciamos la clase
        imageId = self.__dbConnector.createImage(123,"VMNameTest","./VMNameTest/","./OSImagePath1","./VMNameTest/")
        self.assertTrue(self.__dbConnector.doesImageExist(imageId), "Not image regist")  
        self.__dbConnector.deleteImage(imageId)    
    
    def test_getRunningPorts(self):
        #Instanciamos la clase
        l1 = self.__dbConnector.getRunningPorts()
        l2 = [1,2,3,4]
        self.assertEquals(l1, l2, "Not same ports") 
        
    def test_getUsers(self):
        #Instanciamos la clase
        l1 = self.__dbConnector.getUsers()
        l2 = [1,2,3]
        self.assertEquals(l1, l2, "Not same users")

    def test_getAssignedVM(self):
        #Instanciamos la clase
        n1 = self.__dbConnector.getAssignedVM(1)
        n2 = 1
        self.assertEquals(n1, n2, "Not same VM") 
        
    def test_getAssignedVMName(self):
        #Instanciamos la clase
        n1 = self.__dbConnector.getAssignedVMName(2)
        n2 = "VMName1"
        self.assertEquals(n1, n2, "Not same VM Name")   
        
    def test_getMachineDataPath(self):
        #Instanciamos la clase
        n1 = self.__dbConnector.getMachineDataPath(2)
        n2 = "./VMNameCopy1"
        self.assertEquals(n1, n2, "Not same VM path")
 
    def test_getMacAdress(self):
        #Instanciamos la clase
        n1 = self.__dbConnector.getMacAdress(3)
        n2 = "2C:00:00:00:00:02"
        self.assertEquals(n1, n2, "Not same VM MAC") 
        
    def test_getPassword(self):
        #Instanciamos la clase
        n1 = self.__dbConnector.getPassword(3)
        n2 = "1234567890Test"
        self.assertEquals(n1, n2, "Not same VM Pass")
        
    def test_RegisterVM(self):
        #Instanciamos la clase
        portId = self.__dbConnector.registerVMResources("VMName123",23,23,1,23,"./VMNameCopyTest","./OSImagePath1","testMac","testUUID","testPass")
        self.assertTrue(self.__dbConnector.doesVMExist(portId), "Not VM register") 
        self.__dbConnector.unRegisterVMResources("VMName123")
        self.assertFalse(self.__dbConnector.doesVMExist(23), "Not VM unregisted")
        
    def test_NextMac(self):
        #Instanciamos la clase
        (_uuid1,mac1)= self.__dbConnector.extractfreeMacAndUuid()
        (_uuid2,mac2) = ("9a47c734-5e5f-11e2-981b-001f16b99e1d","2C:00:00:00:00:00")
        self.assertEquals(mac1, mac2, "Not same MAC")
    
    def test_VNCPort(self):
        #Instanciamos la clase
        vncPort1= self.__dbConnector.extractfreeVNCPort()
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
        self.assertEquals(result, "1234", "addVMBootCommando does not work")
        
        
if __name__ == "__main__":
    unittest.main()