# -*- coding: UTF8 -*-
'''
Pruebas unitarias de la base de datos de estado
@author: Luis Barrios Hernández
@version: 2.0
'''
import unittest

from ccutils.databases.configuration import DBConfigurator
from clusterEndpoint.databases.clusterEndpointDB import ClusterEndpointDBConnector

class Test(unittest.TestCase):      

    def setUp(self):
        dbConfigurator = DBConfigurator("")
        dbConfigurator.runSQLScript("ClusterEndpointDBTest", "./ClusterEndpointDBTest.sql")
        dbConfigurator.addUser("cygnuscloud", "cygnuscloud", "ClusterEndpointDBTest", True)
        self.__connector = ClusterEndpointDBConnector("cygnuscloud", "cygnuscloud", "ClusterEndpointDBTest")

    def tearDown(self):       
        #dbConfigurator = DBConfigurator("")
        #dbConfigurator.dropDatabase("ClusterEndpointDBTest")
        pass
        
    def testProcessVMServerSegment(self):
        segmentData = [('Server1', 'Ready', 'IP1', 1, 0)]
        self.__connector.processVMServerSegment(1, 1, segmentData)
        result = self.__connector.getVMServersData()
        expectedResult =  [{"VMServerName":"Server1", "VMServerStatus":"Ready", "VMServerIP":"IP1", "VMServerListenningPort":1,
                            "IsVanillaServer" : False}]
        self.assertEquals(result, expectedResult, "VM server segments - single segment error")
            
        segmentData = [('Server1', 'Shut down', 'IP1', 1, 0), ('Server2', 'Booting', 'IP2', 1, 1)]
        self.__connector.processVMServerSegment(1, 1, segmentData)
        result = self.__connector.getVMServersData()
        expectedResult =  [{"VMServerName":"Server1", "VMServerStatus":"Shut down", "VMServerIP":"IP1", "VMServerListenningPort":1, "IsVanillaServer" : False},
                           {"VMServerName":"Server2", "VMServerStatus":"Booting", "VMServerIP":"IP2", "VMServerListenningPort":1, "IsVanillaServer" : True}]
        self.assertEquals(result, expectedResult, "VM server segments - single segment error")
           
    def testProcessMultipleVMServerSegments(self):
        segmentData = [('Server1', 'Ready', 'IP1', 1, 0)]
        self.__connector.processVMServerSegment(1, 2, segmentData)
        result = self.__connector.getVMServersData()
        expectedResult = []
        self.assertEquals(result, expectedResult, "VM server segments - multiple segments error")
        segmentData = [('Server2', 'Ready', 'IP2', 1, 1)]
        self.__connector.processVMServerSegment(2, 2, segmentData)
        result = self.__connector.getVMServersData()
        expectedResult =  [{"VMServerName":"Server1", "VMServerStatus":"Ready", "VMServerIP":"IP1", "VMServerListenningPort":1, "IsVanillaServer" : False},
                           {"VMServerName":"Server2", "VMServerStatus":"Ready", "VMServerIP":"IP2", "VMServerListenningPort":1, "IsVanillaServer" : True},]
        self.assertEquals(result, expectedResult, "VM server segments - multiple segments error")
             
    def testProcessEmptyVMServerSegments(self):
        segmentData = [('Server1', 'Ready', 'IP1', 1, 0)]
        self.__connector.processVMServerSegment(1, 1, segmentData)
        result = self.__connector.getVMServersData()
        expectedResult =  [{"VMServerName":"Server1", "VMServerStatus":"Ready", "VMServerIP":"IP1", "VMServerListenningPort":1, "IsVanillaServer" : False}]
        self.assertEquals(result, expectedResult, "VM server segments - empty segments error")
             
        segmentData = []
        self.__connector.processVMServerSegment(0, 0, segmentData)
        result = self.__connector.getVMServersData()
        expectedResult =  []
        self.assertEquals(result, expectedResult, "VM server segments - empty segments error")
            
    def testProcessVMDistributionSegment(self):
        segmentData = [('Server1', 1), ('Server1', 2), ('Server1', 3)]
        self.__connector.processVMDistributionSegment(1, 1, segmentData)
        result = self.__connector.getVMDistributionData()
        expectedResult = [{"VMServerName":"Server1", "VMID":1}, {"VMServerName":"Server1", "VMID":2}, {"VMServerName":"Server1", "VMID":3}]
        self.assertEquals(result, expectedResult, "VM distribution segments - one segment error")
            
    def testProcessMultipleVMDistributionSegments(self):
        segmentData = [('Server1', 1), ('Server1', 2), ('Server1', 3)]
        self.__connector.processVMDistributionSegment(1, 2, segmentData)
        result = self.__connector.getVMDistributionData()
        expectedResult = []
        self.assertEquals(result, expectedResult, "VM distribution segments - multiple segments error")
         
        segmentData = [('Server2', 3), ('Server2', 4)]
        self.__connector.processVMDistributionSegment(2, 2, segmentData)
        result = self.__connector.getVMDistributionData()
        expectedResult = [{"VMServerName":"Server1", "VMID":1}, {"VMServerName":"Server1", "VMID":2}, {"VMServerName":"Server1", "VMID":3},
                          {"VMServerName":"Server2", "VMID":3}, {"VMServerName":"Server2", "VMID":4}]
        self.assertEquals(result, expectedResult, "VM distribution segments - multiple segments error")
             
    def testProcessEmptyVMDistributionSegment(self):
        segmentData = [('Server1', 1), ('Server1', 2), ('Server1', 3)]
        self.__connector.processVMDistributionSegment(1, 1, segmentData)
        result = self.__connector.getVMDistributionData()
        expectedResult = [{"VMServerName":"Server1", "VMID":1}, {"VMServerName":"Server1", "VMID":2}, {"VMServerName":"Server1", "VMID":3}]
        self.assertEquals(result, expectedResult, "VM distribution segments - one segment error")
             
        segmentData = []
        self.__connector.processVMDistributionSegment(0, 0, segmentData)
        result = self.__connector.getVMDistributionData()
        expectedResult = []
        self.assertEquals(result, expectedResult, "VM distribution segments - empty segment error")
           
    def testProcessActiveVMSegment(self):
            
        # Hay que crear un servidor de máquinas virtuales
        segmentData = [('Server1', 'Ready', 'IP1', 1, 0)]
        self.__connector.processVMServerSegment(1, 1, segmentData)          
            
        segmentData = [('machine1', 1, 1, 'Debian1', 15800, 'Password')]
        self.__connector.processActiveVMSegment(1, 1, 'IP1', segmentData)
        result = self.__connector.getActiveVMsData(None)
        expectedResult = [{"VMServerName" : "Server1", "DomainUID" : "machine1", "UserID" : 1, "VMID" : 1, "VMName" : "Debian1", "VNCPort" : 15800, 
                           "VNCPassword" : "Password" }]
        self.assertEquals(result, expectedResult, "Active VM segment - single segment error")
           
    def testGetActiveVMsData(self):
            
        # Hay que crear un servidor de máquinas virtuales
        segmentData = [('Server1', 'Ready', 'IP1', 1, 0)]
        self.__connector.processVMServerSegment(1, 1, segmentData)
            
            
        segmentData = [('machine1', 1, 1, 'Debian1', 15800, 'Password'), ('machine2', 2, 1, 'Debian2', 15802, 'Password')]
        self.__connector.processActiveVMSegment(1, 1, 'IP1', segmentData)
        result = self.__connector.getActiveVMsData(1)
        expectedResult = [{"VMServerName" : "Server1", "DomainUID" : "machine1", "UserID" : 1, "VMID" : 1, "VMName" : "Debian1", "VNCPort" : 15800, 
                           "VNCPassword" : "Password" }]
        self.assertEquals(result, expectedResult, "Get active VM data error")
            
        result = self.__connector.getActiveVMsData(2)
        expectedResult = [{"VMServerName" : "Server1", "DomainUID" : "machine2", "UserID" : 2, "VMID" : 1, "VMName" : "Debian2", "VNCPort" : 15802, 
                           "VNCPassword" : "Password" }]
        self.assertEquals(result, expectedResult, "Get active VM data error")
            
        result = self.__connector.getActiveVMsData(100)
        expectedResult = []        
        self.assertEquals(result, expectedResult, "Get active VM data error")
            
        result = self.__connector.getActiveVMsData(None)
        expectedResult = [{"VMServerName" : "Server1", "DomainUID" : "machine2", "UserID" : 2, "VMID" : 1, "VMName" : "Debian2", "VNCPort" : 15802, 
                           "VNCPassword" : "Password" },
                          {"VMServerName" : "Server1", "DomainUID" : "machine1", "UserID" : 1, "VMID" : 1, "VMName" : "Debian1", "VNCPort" : 15800, 
                           "VNCPassword" : "Password" }]        
        self.assertEquals(result, expectedResult, "Get active VM data error")
           
    def testProcessMultipleActiveVMSegments(self):
        # Hay que crear un servidor de máquinas virtuales
        segmentData = [('Server1', 'Ready', 'IP1', 1, 0)]
        self.__connector.processVMServerSegment(1, 1, segmentData)
            
            
        segmentData = [('machine1', 1, 1, 'Debian1', 15800, 'Password')]
        self.__connector.processActiveVMSegment(1, 2, 'IP1', segmentData)
        result = self.__connector.getActiveVMsData(None)
        expectedResult = []
        self.assertEquals(result, expectedResult, "Active VMs - multiple segment error")
            
        segmentData = [('machine2', 2, 1, 'Debian2', 15802, 'Password')]
        self.__connector.processActiveVMSegment(2, 2, 'IP1', segmentData)
        result = self.__connector.getActiveVMsData(None)
        expectedResult = [{"VMServerName" : "Server1", "DomainUID" : "machine2", "UserID" : 2, "VMID" : 1, "VMName" : "Debian2", "VNCPort" : 15802, 
                           "VNCPassword" : "Password" },
                          {"VMServerName" : "Server1", "DomainUID" : "machine1", "UserID" : 1, "VMID" : 1, "VMName" : "Debian1", "VNCPort" : 15800, 
                           "VNCPassword" : "Password" }]        
        self.assertEquals(result, expectedResult, "Active VMs - multiple segment error")
           
    def processEmptyActiveVMSegment(self):
             
        # Hay que crear un servidor de máquinas virtuales
        segmentData = [('Server1', 'Ready', 'IP1', 1, 0)]
        self.__connector.processVMServerSegment(1, 1, segmentData)        
             
        segmentData = [('machine1', 1, 1, 'Debian1', 15800, 'Password')]
        self.__connector.processActiveVMSegment(1, 1, 'IP1', segmentData)
        result = self.__connector.getActiveVMsData(None)
        expectedResult = [{"VMServerName" : "Server1", "DomainUID" : "machine1", "UserID" : 1, "VMID" : 1, "VMName" : "Debian1", "VNCPort" : 15800, 
                           "VNCPassword" : "Password" }]
        self.assertEquals(result, expectedResult, "Active VM segment - empty segment error")
             
        segmentData = []
        self.__connector.processActiveVMSegment(0, 0, 'IP1', segmentData)
        result = self.__connector.getActiveVMsData(None)
        expectedResult = []
        self.assertEquals(result, expectedResult, "Active VM segment - empty segment error")
         
    def test_getImageBasicData(self):
        result = self.__connector.getImageData(1)
        expectedResult = {'OSVariant': 1, 'OSFamily': 1, 'VanillaImageFamilyID': 1, 'ImageDescription': 'Imagen vanilla', 'IsBootable': 
            False, 'ImageName': 'Debian-Squeeze', 'IsEdited': False, 'AssignedToSubject': True, 'OwnerID': 0, 
                'IsBaseImage': True}
        self.assertEquals(result, expectedResult, "getImageData() error")
        result = self.__connector.getImageData("Command1")
        expectedResult = {'OSVariant': 1, 'OSFamily': 1, 'VanillaImageFamilyID': 1, 'ImageDescription': 'Imagen LSO', 'IsBootable': 
                          False, 'ImageName': 'Debian-LSO', 'IsEdited': True, 'AssignedToSubject': False, 'OwnerID': 1, 'IsBaseImage': 
                          False}
        self.assertEquals(result, expectedResult, "getImageData() error")
         
    def test_getBootableImagesData(self):
        result = self.__connector.getBootableImagesData([1])
        expectedResult = []
        self.assertEquals(result, expectedResult, "getBootableImagesData() error")
        result = self.__connector.getBootableImagesData([3])
        expectedResult = [{'OSVariant': 1, 'OSFamily': 1, 'VanillaImageFamilyID': 1, 'ImageDescription': 'Imagen de AISO', 
                          'ImageID': 3, 'ImageName': 'Debian-AISO'}]
        self.assertEquals(result, expectedResult, "getBootableImagesData() error")
        result = self.__connector.getBootableImagesData([3, 4])
        expectedResult = [{'OSVariant': 1, 'OSFamily': 1, 'VanillaImageFamilyID': 1, 'ImageDescription': 'Imagen de AISO', 
                           'ImageID': 3, 'ImageName': 'Debian-AISO'}, {'OSVariant': 1, 'OSFamily': 2, 'VanillaImageFamilyID': 4, 
                                'ImageDescription':'Imagen de LEC', 'ImageID': 4, 'ImageName': 'Windows-LEC'}]
        self.assertEquals(result, expectedResult, "getBootableImagesData() error")
          
    def test_getBaseImagesData(self):
        result = self.__connector.getBaseImagesData()
        expectedResult =  [{'OSVariant': 1, 'OSFamily': 1, 'VanillaImageFamilyID': 1, 'ImageDescription': 'Imagen vanilla', 'ImageID': 1, 
                            'ImageName': 'Debian-Squeeze'}, {'OSVariant': 1, 'OSFamily': 1, 'VanillaImageFamilyID': 4, 'ImageDescription': 
                                                             'Imagen vanilla', 'ImageID': 2, 'ImageName': 'Windows 7'}]
        self.assertEquals(result, expectedResult, "getBaseImagesData() error")
     
    def test_getEditedImages(self):
        result = self.__connector.getEditedImageIDs(100)
        expectedResult = []
        self.assertEquals(result, expectedResult, "getEditedImageIDs() error")
           
        result = self.__connector.getEditedImageIDs(2)
        expectedResult = [5]
        self.assertEquals(result, expectedResult, "getEditedImageIDs() error")
  
    def test_getVanillaImageFamilyID(self):
        result = self.__connector.getVanillaImageFamilyID(1)
        expectedResult = 1
        self.assertEquals(result, expectedResult, "getVanillaImageFamilyID error()")
        result = self.__connector.getVanillaImageFamilyID("Command2")
        expectedResult = 4
        self.assertEquals(result, expectedResult, "getVanillaImageFamilyID error()")
        result = self.__connector.getVanillaImageFamilyID(1000)
        expectedResult = None
        self.assertEquals(result, expectedResult, "getVanillaImageFamilyID error()")
      
    def test_getNewImageIDs(self):
        result = self.__connector.getNewImageIDs(0)
        expectedResult = []
        self.assertEquals(result, expectedResult, "getNewImageIDs() error")
        result = self.__connector.getNewImageIDs(1)
        expectedResult = ["Command1", "Command2"]
        self.assertEquals(result, expectedResult, "getNewImageIDs() error")
    def test_getVanillaImageFamiliyData(self):
        result = self.__connector.getVanillaImageFamiliyData(1)
        expectedResult = {"Name" : "Linux-Small", "RAMSize" : 1048576, "VCPUs": 1, "OSDiskSize" : 5242880, "DataDiskSize" : 3145728}
        self.assertEquals(result, expectedResult, "getVanillaImageFamilyData error()")
        result = self.__connector.getVanillaImageFamiliyData(1000)
        expectedResult = None
        self.assertEquals(result, expectedResult, "getVanillaImageFamilyData error()")
        
    def test_getMaxVanillaImageFamilyData(self):
        result = self.__connector.getMaxVanillaImageFamilyData()
        expectedResult = {'OSDiskSize': 41943040, 'DataDiskSize': 16777216, 'VCPUs': 4, 'RAMSize': 3145728}
        self.assertEquals(result, expectedResult, "getMaxVanillaImageFamilyData() error")
if __name__ == "__main__":
    unittest.main()