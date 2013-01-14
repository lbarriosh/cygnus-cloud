
# -*- coding: UTF8 -*-
import MySQLdb
import os
import unittest

from VMServerDB.ImageManager import ImageManager
from VMServerDB.RuntimeData import RuntimeData
from DBUtils.DBUtils import DBUtils

class DBWebServerTests(unittest.TestCase):
    '''
        Clase encargada de realizar los test unitarios asociados 
    '''
    def test_getImages(self):
        #Instanciamos la clase
        imageM = ImageManager("CygnusCloud","cygnuscloud2012","DBVMServerTest")
        l1 = imageM.getImages()
        l2 = [1,2,3,4]
        self.assertEquals(l1, l2, "Not same images")
        
    def test_getName(self):
        #Instanciamos la clase
        imageM = ImageManager("CygnusCloud","cygnuscloud2012","DBVMServerTest")
        n1 = imageM.getName(1)
        n2 = "VMName1"
        self.assertEquals(n1, n2, "Not same image name")
        
    def test_getImagePath(self):
        #Instanciamos la clase
        imageM = ImageManager("CygnusCloud","cygnuscloud2012","DBVMServerTest")
        n1 = imageM.getImagePath(1)
        n2 = "./VMName1/"
        self.assertEquals(n1, n2, "Not same image path")   
        
    def test_getFileConfigPath(self):
        #Instanciamos la clase
        imageM = ImageManager("CygnusCloud","cygnuscloud2012","DBVMServerTest")
        n1 = imageM.getFileConfigPath(1)
        n2 = "./VMName1/"
        self.assertEquals(n1, n2, "Not same image path")

    def test_setImagePath(self):
        #Instanciamos la clase
        imageM = ImageManager("CygnusCloud","cygnuscloud2012","DBVMServerTest")
        imageM.setImagePath(1,"./VMName1Test/")
        n1 = imageM.getImagePath(1)
        n2 = "./VMName1Test/"
        self.assertEquals(n1, n2, "Not change image path")  
        
    def test_createImage(self):
        #Instanciamos la clase
        imageM = ImageManager("CygnusCloud","cygnuscloud2012","DBVMServerTest")
        imageId = imageM.createImage(123,"VMNameTest","./VMNameTest/","./VMNameTest/")
        self.assertTrue(imageM.isImageExists(imageId), "Not image regist")  
        imageM.deleteImage(imageId)    
    
    def test_getRunningPorts(self):
        #Instanciamos la clase
        runtimeD = RuntimeData("CygnusCloud","cygnuscloud2012","DBVMServerTest")
        l1 = runtimeD.getRunningPorts()
        l2 = [0,1,2,3,4]
        self.assertEquals(l1, l2, "Not same ports") 
        
    def test_getUsers(self):
        #Instanciamos la clase
        runtimeD = RuntimeData("CygnusCloud","cygnuscloud2012","DBVMServerTest")
        l1 = runtimeD.getUsers()
        l2 = [1,2,3,4,5]
        self.assertEquals(l1, l2, "Not same users")

    def test_getAssignedVM(self):
        #Instanciamos la clase
        runtimeD = RuntimeData("CygnusCloud","cygnuscloud2012","DBVMServerTest")
        n1 = runtimeD.getAssignedVM(1)
        n2 = 1
        self.assertEquals(n1, n2, "Not same VM") 
        
    def test_getAssignedVMName(self):
        #Instanciamos la clase
        runtimeD = RuntimeData("CygnusCloud","cygnuscloud2012","DBVMServerTest")
        n1 = runtimeD.getAssignedVMName(2)
        n2 = "VMName2"
        self.assertEquals(n1, n2, "Not same VM Name")   
        
    def test_getMachineDataPath(self):
        #Instanciamos la clase
        runtimeD = RuntimeData("CygnusCloud","cygnuscloud2012","DBVMServerTest")
        n1 = runtimeD.getMachineDataPath(2)
        n2 = "./VMNameCopy2"
        self.assertEquals(n1, n2, "Not same VM path")
 
    def test_getMacAdress(self):
        #Instanciamos la clase
        runtimeD = RuntimeData("CygnusCloud","cygnuscloud2012","DBVMServerTest")
        n1 = runtimeD.getMacAdress(3)
        n2 = "2C:00:00:00:00:03"
        self.assertEquals(n1, n2, "Not same VM MAC") 
        
    def test_getPassword(self):
        #Instanciamos la clase
        runtimeD = RuntimeData("CygnusCloud","cygnuscloud2012","DBVMServerTest")
        n1 = runtimeD.getPassword(3)
        n2 = "1234567890Test"
        self.assertEquals(n1, n2, "Not same VM Pass")
        
    def test_RegisterVM(self):
        #Instanciamos la clase
        runtimeD = RuntimeData("CygnusCloud","cygnuscloud2012","DBVMServerTest")
        portId = runtimeD.registerVNCPort(23,23,4,"./VMNameCopyTest","testMac","testUUID","testPass")
        self.assertTrue(runtimeD.isVMExists(portId), "Not VM register") 
        runtimeD.unregisterVNCPort(23)
        self.assertFalse(runtimeD.isVMExists(23), "Not VM unregisted")
    def test_NextMac(self):
        #Instanciamos la clase
        runtimeD = RuntimeData("CygnusCloud","cygnuscloud2012","DBVMServerTest")
        (uuid1,mac1)= runtimeD.extractfreeMac()
        (uuid2,mac2) = ("9a47c734-5e5f-11e2-981b-001f16b99e1d","2C:00:00:00:00:00")
        self.assertEquals(mac1, mac2, "Not same MAC")
             

        
if __name__ == "__main__":
    #Cargamos el script de prueba
    dbUtils = DBUtils(os.getcwd() + "/DBVMServerTest.sql")
    dbUtils.initMySqlUser("CygnusCloud","cygnuscloud2012")
    dbUtils.loadScript("CygnusCloud","cygnuscloud2012")     
    unittest.main()