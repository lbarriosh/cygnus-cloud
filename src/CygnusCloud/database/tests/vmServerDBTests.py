
# -*- coding: UTF8 -*-
import unittest

from database.vmServer.imageManager import ImageManager
from database.vmServer.runtimeData import RuntimeData
from database.utils.configuration import DBConfigurator

class DBWebServerTests(unittest.TestCase):
    '''
        Clase encargada de realizar los test unitarios asociados 
    '''
    def test_getImages(self):
        #Instanciamos la clase
        imageM = ImageManager("CygnusCloud","cygnuscloud2012","VMServerDBTest")
        l1 = imageM.getImages()
        l2 = [1,2,3,4]
        self.assertEquals(l1, l2, "Not same images")
        
    def test_getName(self):
        #Instanciamos la clase
        imageM = ImageManager("CygnusCloud","cygnuscloud2012","VMServerDBTest")
        n1 = imageM.getName(1)
        n2 = "VMName1"
        self.assertEquals(n1, n2, "Not same image name")
        
    def test_getImagePath(self):
        #Instanciamos la clase
        imageM = ImageManager("CygnusCloud","cygnuscloud2012","VMServerDBTest")
        n1 = imageM.getImagePath(1)
        n2 = "./VMName1/"
        self.assertEquals(n1, n2, "Not same image path")   
        
    def test_getFileConfigPath(self):
        #Instanciamos la clase
        imageM = ImageManager("CygnusCloud","cygnuscloud2012","VMServerDBTest")
        n1 = imageM.getFileConfigPath(1)
        n2 = "./VMName1/"
        self.assertEquals(n1, n2, "Not same image path")

    def test_setImagePath(self):
        #Instanciamos la clase
        imageM = ImageManager("CygnusCloud","cygnuscloud2012","VMServerDBTest")
        imageM.setImagePath(1,"./VMName1Test/")
        n1 = imageM.getImagePath(1)
        n2 = "./VMName1Test/"
        self.assertEquals(n1, n2, "Not change image path")  
        
    def test_createImage(self):
        #Instanciamos la clase
        imageM = ImageManager("CygnusCloud","cygnuscloud2012","VMServerDBTest")
        imageId = imageM.createImage(123,"VMNameTest","./VMNameTest/","./OSImagePath1","./VMNameTest/")
        self.assertTrue(imageM.isImageExists(imageId), "Not image regist")  
        imageM.deleteImage(imageId)    
    
    def test_getRunningPorts(self):
        #Instanciamos la clase
        runtimeD = RuntimeData("CygnusCloud","cygnuscloud2012","VMServerDBTest")
        l1 = runtimeD.getRunningPorts()
        l2 = [1,2,3,4]
        self.assertEquals(l1, l2, "Not same ports") 
        
    def test_getUsers(self):
        #Instanciamos la clase
        runtimeD = RuntimeData("CygnusCloud","cygnuscloud2012","VMServerDBTest")
        l1 = runtimeD.getUsers()
        l2 = [1,1,2,3]
        self.assertEquals(l1, l2, "Not same users")

    def test_getAssignedVM(self):
        #Instanciamos la clase
        runtimeD = RuntimeData("CygnusCloud","cygnuscloud2012","VMServerDBTest")
        n1 = runtimeD.getAssignedVM(1)
        n2 = 1
        self.assertEquals(n1, n2, "Not same VM") 
        
    def test_getAssignedVMName(self):
        #Instanciamos la clase
        runtimeD = RuntimeData("CygnusCloud","cygnuscloud2012","VMServerDBTest")
        n1 = runtimeD.getAssignedVMName(2)
        n2 = "VMName2"
        self.assertEquals(n1, n2, "Not same VM Name")   
        
    def test_getMachineDataPath(self):
        #Instanciamos la clase
        runtimeD = RuntimeData("CygnusCloud","cygnuscloud2012","VMServerDBTest")
        n1 = runtimeD.getMachineDataPath(2)
        n2 = "./VMNameCopy1"
        self.assertEquals(n1, n2, "Not same VM path")
 
    def test_getMacAdress(self):
        #Instanciamos la clase
        runtimeD = RuntimeData("CygnusCloud","cygnuscloud2012","VMServerDBTest")
        n1 = runtimeD.getMacAdress(3)
        n2 = "2C:00:00:00:00:02"
        self.assertEquals(n1, n2, "Not same VM MAC") 
        
    def test_getPassword(self):
        #Instanciamos la clase
        runtimeD = RuntimeData("CygnusCloud","cygnuscloud2012","VMServerDBTest")
        n1 = runtimeD.getPassword(3)
        n2 = "1234567890Test"
        self.assertEquals(n1, n2, "Not same VM Pass")
        
    def test_RegisterVM(self):
        #Instanciamos la clase
        runtimeD = RuntimeData("CygnusCloud","cygnuscloud2012","VMServerDBTest")
        portId = runtimeD.registerVMResources("VMName123",23,23,1,23,"./VMNameCopyTest","./OSImagePath1","testMac","testUUID","testPass")
        self.assertTrue(runtimeD.isVMExists(portId), "Not VM register") 
        runtimeD.unRegisterVMResources("VMName123")
        self.assertFalse(runtimeD.isVMExists(23), "Not VM unregisted")
    def test_NextMac(self):
        #Instanciamos la clase
        runtimeD = RuntimeData("CygnusCloud","cygnuscloud2012","VMServerDBTest")
        (_uuid1,mac1)= runtimeD.extractfreeMacAndUuid()
        (_uuid2,mac2) = ("9a47c734-5e5f-11e2-981b-001f16b99e1d","2C:00:00:00:00:00")
        self.assertEquals(mac1, mac2, "Not same MAC")
    
    def test_VNCPort(self):
        #Instanciamos la clase
        runtimeD = RuntimeData("CygnusCloud","cygnuscloud2012","VMServerDBTest")
        vncPort1= runtimeD.extractfreeVNCPort()
        vncPort2 = (15000)
        self.assertEquals(vncPort1, vncPort2, "Not same VNCPort")
             
    def test_getVMsConnectionData(self):
        runtimeD = RuntimeData("CygnusCloud","cygnuscloud2012","VMServerDBTest")
        result = runtimeD.getVMsConnectionData()
        expectedResult = [
                          {"UserID": 1, "VMID": 1, "VMName" :"VMName11", "VNCPort" : 1, "VNCPass" : "1234567890"},
                          {"UserID": 1, "VMID": 1, "VMName" :"VMName22", "VNCPort" : 2, "VNCPass" : "1234567890"},
                          {"UserID": 2, "VMID": 1, "VMName" :"VMName33", "VNCPort" : 3, "VNCPass" : "1234567890Test"},
                          {"UserID": 3, "VMID": 1, "VMName" :"VMName44", "VNCPort" : 4, "VNCPass" : "1234567890"}
                          ]
        self.assertEquals(result, expectedResult, "getVMsConnectionData does not work")
        
if __name__ == "__main__":
    #Cargamos el script de prueba
    dbConfigurator = DBConfigurator("")
    dbConfigurator.runSQLScript("VMServerDBTest", "./VMServerDBTest.sql")
    dbConfigurator.addUser("CygnusCloud", "cygnuscloud2012", "VMServerDBTest", True)
    unittest.main()
    dbConfigurator.dropDatabase("VMServerDBTest")