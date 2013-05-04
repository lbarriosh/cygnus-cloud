
# -*- coding: UTF8 -*-
import unittest

from database.vmServer.vmServerDB import VMServerDBConnector
from database.utils.configuration import DBConfigurator
from virtualMachineServer.reactor.transfer_t import TRANSFER_T

class DBWebServerTests(unittest.TestCase):
    '''
        Clase con las pruebas unitarias de la base de datos del servidor de máquinas
        virtuales
    '''    
    def setUp(self):
        self.__dbConfigurator = DBConfigurator("")
        self.__dbConfigurator.runSQLScript("VMServerDBTest", "./VMServerDBTest.sql")
        self.__dbConfigurator.addUser("CygnusCloud", "cygnuscloud2012", "VMServerDBTest", True)
        self.__dbConnector = VMServerDBConnector("CygnusCloud", "cygnuscloud2012", "VMServerDBTest")
    
    def tearDown(self):
        self.__dbConnector.disconnect()
        self.__dbConfigurator.dropDatabase("VMServerDBTest")
    
#     def test_getImages(self):
#         result = self.__dbConnector.getImageIDs()
#         expectedResult = [1, 2, 3, 4]
#         self.assertEquals(result, expectedResult, "getImageIDs() error")
#        
#          
#     def test_getDataImagePath(self):
#         result = self.__dbConnector.getDataImagePath(1)
#         expectedResult = "./VMName1/Data.qcow2"
#         self.assertEquals(result, expectedResult, "getDataImagePath() error")   
#         
#     def test_getOSImagePath(self):
#         result = self.__dbConnector.getOSImagePath(1)
#         expectedResult = "./VMName1/OS.qcow2"
#         self.assertEquals(result, expectedResult, "getOSImagePath() error")   
#         
#     def test_getDefinitionFilePath(self):
#         result = self.__dbConnector.getDefinitionFilePath(1)
#         expectedResult = "./VMName1/Definition.xml"
#         self.assertEquals(result, expectedResult, "getDefinitionFilePath() error")   
#         
#     def test_createImage(self):
#         self.__dbConnector.createImage(123, "Image/OS.qcow2", "Image/Data.qcow2", "Image/Definition.xml", 0)
#         result = self.__dbConnector.getOSImagePath(123)
#         expectedResult = "Image/OS.qcow2"
#         self.assertEquals(result, expectedResult, "createImage() error")   
#         result = self.__dbConnector.getDataImagePath(123)
#         expectedResult = "Image/Data.qcow2"
#         self.assertEquals(result, expectedResult, "createImage() error")  
#         result = self.__dbConnector.getDefinitionFilePath(123)
#         expectedResult = "Image/Definition.xml"
#         self.assertEquals(result, expectedResult, "createImage() error")   
#         result = self.__dbConnector.getBootableFlag(123)
#         expectedResult = False
#         self.assertEquals(result, expectedResult, "createImage() error")   
#         
#     def test_deleteImage(self):
#         self.__dbConnector.deleteImage(1)
#         result = self.__dbConnector.getOSImagePath(1)
#         expectedResult = None
#         self.assertEquals(result, expectedResult, "deleteImage() error")  
#         
#     def test_getDomainImageID(self):
#         result = self.__dbConnector.getDomainImageID("1_1")
#         expectedResult = 1
#         self.assertEquals(result, expectedResult, "getDomainImageID() error") 
#         
#     def test_getDomainDataImagePath(self):
#         result = self.__dbConnector.getDomainDataImagePath("1_1")
#         expectedResult = "./DataImagePath1"
#         self.assertEquals(result, expectedResult, "getDomainDataImagePath() error") 
#     
#     def test_getDomainOSImagePath(self):
#         result = self.__dbConnector.getDomainOSImagePath("1_1")
#         expectedResult = "./OSImagePath1"
#         self.assertEquals(result, expectedResult, "getDomainOSImagePath() error") 
#         
#     def test_getDomainMACAddress(self):
#         result = self.__dbConnector.getDomainMACAddress("1_1")
#         expectedResult = "2C:00:00:00:00:00"
#         self.assertEquals(result, expectedResult, "getDomainMACAddress() error") 
#         
#     def test_getDomainUUID(self):
#         result = self.__dbConnector.getDomainUUID("1_1")
#         expectedResult = "fce02cff-5d6d-11e2-a3f0-001f16b99e1d"
#         self.assertEquals(result, expectedResult, "getDomainUUID() error") 
#         
#     def test_getDomainVNCPassword(self):
#         result = self.__dbConnector.getDomainVNCPassword("1_1")
#         expectedResult = "12134567890"
#         self.assertEquals(result, expectedResult, "getDomainVNCPassword() error") 
#         
#     def test_getWebsockifyDaemonPID(self):
#         result = self.__dbConnector.getWebsockifyDaemonPID("1_1")
#         expectedResult = 1
#         self.assertEquals(result, expectedResult, "getWebsockifyDaemonPID() error") 
#  
#     def test_getDomainNameFromVNCPort(self):
#         result = self.__dbConnector.getDomainNameFromVNCPort(1)
#         expectedResult = "1_1"
#         self.assertEquals(result, expectedResult, "getDomainNameFromVNCPort() error") 
#         
#     def test_registerVMResources(self):
#         self.__dbConnector.registerVMResources("1_20", 1, 2000, "aaa", 1, 2, "OS_20.qcow2", "Data_20.qcow2", "MAC_20", "UUID_20")
#         result = self.__dbConnector.getDomainNameFromVNCPort(2000)
#         expectedResult = "1_20"
#         self.assertEquals(result, expectedResult, "registerVMSResources() error")
#         result = self.__dbConnector.getDomainVNCPassword("1_20")
#         expectedResult = "aaa"
#         self.assertEquals(result, expectedResult, "registerVMSResources() error")
#         result = self.__dbConnector.getDomainOwnerID("1_20")
#         expectedResult = 1
#         self.assertEquals(result, expectedResult, "registerVMSResources() error")
#         result = self.__dbConnector.getWebsockifyDaemonPID("1_20")
#         expectedResult = 2
#         self.assertEquals(result, expectedResult, "registerVMSResources() error")
#         result = self.__dbConnector.getDomainOSImagePath("1_20")
#         expectedResult = "OS_20.qcow2"
#         self.assertEquals(result, expectedResult, "registerVMSResources() error")
#         result = self.__dbConnector.getDomainDataImagePath("1_20")
#         expectedResult = "Data_20.qcow2"
#         self.assertEquals(result, expectedResult, "registerVMSResources() error")
#         result = self.__dbConnector.getDomainMACAddress("1_20")
#         expectedResult = "MAC_20"
#         self.assertEquals(result, expectedResult, "registerVMSResources() error")
#         result = self.__dbConnector.getDomainUUID("1_20")
#         expectedResult = "UUID_20"
#         self.assertEquals(result, expectedResult, "registerVMSResources() error")
#         
#     def test_unregisterDomainResources(self):
#         self.__dbConnector.unregisterDomainResources("1_1")
#         result = self.__dbConnector.getDomainOSImagePath("1_1")
#         expectedResult = None
#         self.assertEquals(result, expectedResult, "unregisterDomainResources() error")
#         
#     def test_getOwnerID(self):
#         result = self.__dbConnector.getDomainOwnerID("1_1")
#         expectedResult = 1
#         self.assertEquals(result, expectedResult, "getOwnerID() error")
#        
#     def test_getVMBootCommand(self):
#         result = self.__dbConnector.getVMBootCommand("4_4")
#         expectedResult = "Command4"
#         self.assertEquals(result, expectedResult, "getVMBootCommand() error")
#         result = self.__dbConnector.getVMBootCommand("3_3")
#         self.assertEquals(result, "Command3", "getVMBootCommand() error")
# 
#        
#     def test_addVMBootCommand(self):
#         self.__dbConnector.registerVMResources("5_5", 1, 1, "123", 1, 1, "os", "data", "mac", "uuid")
#         self.__dbConnector.addVMBootCommand("5_5", "1234")
#         result = self.__dbConnector.getVMBootCommand("5_5")
#         self.assertEquals(result, "1234", "addVMBootCommand() error")
# 
#     def test_getBootableFlag(self):
#         result = self.__dbConnector.getBootableFlag(2)
#         expectedResult = True
#         self.assertEquals(result, expectedResult, "getBootableFlag() error")
#         
#     def test_getRegisteredDomainNames(self):
#         result = self.__dbConnector.getRegisteredDomainNames()
#         expectedResult = ["1_1", "2_2", "3_3", "4_4"]
#         self.assertEquals(result, expectedResult, "getRegisteredDomainNames() error")    
        
    def test_addToTransferQueue(self):
        expectedResult = dict()
        expectedResult["Transfer_Type"] = TRANSFER_T.STORE_IMAGE
        expectedResult["FTPTimeout"] = 100
        expectedResult["TargetImageID"] = 2
        expectedResult["RepositoryIP"] = "192.168.0.1"
        expectedResult["RepositoryPort"] = 3000
        expectedResult["CommandID"] = "1"
        expectedResult["SourceFilePath"] ="/tmp/foo.zip"
        self.__dbConnector.addToTransferQueue(expectedResult)
        result = self.__dbConnector.peekFromTransferQueue()
        self.assertEquals(result, expectedResult, "addToTransferQueue() error")
        self.__dbConnector.removeFirstElementFromTransferQueue()
        expectedResult = dict()
        expectedResult["Transfer_Type"] = TRANSFER_T.EDIT_IMAGE
        expectedResult["FTPTimeout"] = 100
        expectedResult["SourceImageID"] = 2
        expectedResult["TargetImageID"] = 2
        expectedResult["RepositoryIP"] = "192.168.0.1"
        expectedResult["RepositoryPort"] = 3000
        expectedResult["CommandID"] = "1"
        expectedResult["UserID"] = 1
        self.__dbConnector.addToTransferQueue(expectedResult)
        result = self.__dbConnector.peekFromTransferQueue()
        self.assertEquals(result, expectedResult, "addToTransferQueue() error")
        
    def test_addToCompressionQueue(self):
        expectedResult = dict()
        expectedResult["Transfer_Type"] = TRANSFER_T.STORE_IMAGE
        expectedResult["CommandID"] = "1"
        expectedResult["TargetImageID"] = 1
        expectedResult["OSImagePath"] = "os.qcow"
        expectedResult["DataImagePath"] = "data.qcow2"
        expectedResult["DefinitionFilePath"] = "definition.xml"
        expectedResult["RepositoryIP"] = "192.198.0.2"
        expectedResult["RepositoryPort"] = 3000
        self.__dbConnector.addToCompressionQueue(expectedResult)
        result = self.__dbConnector.peekFromCompressionQueue()
        self.assertEquals(result, expectedResult, "addToCompressionQueue() error")
        self.__dbConnector.removeFirstElementFromCompressionQueue()
        expectedResult = dict()
        expectedResult["Transfer_Type"] = TRANSFER_T.EDIT_IMAGE
        expectedResult["CommandID"] = "1"
        expectedResult["TargetImageID"] = 1
        expectedResult["SourceImageID"] = 2
        expectedResult["UserID"] = 3
        self.__dbConnector.addToCompressionQueue(expectedResult)
        result = self.__dbConnector.peekFromCompressionQueue()
        self.assertEquals(result, expectedResult, "addToCompressionQueue() error")
        
        
        
if __name__ == "__main__":
    unittest.main()
