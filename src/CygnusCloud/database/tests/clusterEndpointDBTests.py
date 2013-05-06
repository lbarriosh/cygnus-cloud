# -*- coding: UTF8 -*-
'''
Pruebas unitarias de la base de datos de estado
@author: Luis Barrios Hernández
@version: 2.0
'''
import unittest

from database.utils.configuration import DBConfigurator
from database.clusterEndpoint.clusterEndpointDB import ClusterEndpointDBConnector

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
#           
#     def testProcessVMDistributionSegment(self):
#         segmentData = [('Server1', 1), ('Server1', 2), ('Server1', 3)]
#         self.__connector.processVMDistributionSegment(1, 1, segmentData)
#         result = self.__connector.getVMDistributionData()
#         expectedResult = [{"VMServerName":"Server1", "VMID":1}, {"VMServerName":"Server1", "VMID":2}, {"VMServerName":"Server1", "VMID":3}]
#         self.assertEquals(result, expectedResult, "VM distribution segments - one segment error")
#           
#     def testProcessMultipleVMDistributionSegments(self):
#         segmentData = [('Server1', 1), ('Server1', 2), ('Server1', 3)]
#         self.__connector.processVMDistributionSegment(1, 2, segmentData)
#         result = self.__connector.getVMDistributionData()
#         expectedResult = []
#         self.assertEquals(result, expectedResult, "VM distribution segments - multiple segments error")
#       
#         segmentData = [('Server2', 3), ('Server2', 4)]
#         self.__connector.processVMDistributionSegment(2, 2, segmentData)
#         result = self.__connector.getVMDistributionData()
#         expectedResult = [{"VMServerName":"Server1", "VMID":1}, {"VMServerName":"Server1", "VMID":2}, {"VMServerName":"Server1", "VMID":3},
#                           {"VMServerName":"Server2", "VMID":3}, {"VMServerName":"Server2", "VMID":4}]
#         self.assertEquals(result, expectedResult, "VM distribution segments - multiple segments error")
#           
#     def testProcessEmptyVMDistributionSegment(self):
#         segmentData = [('Server1', 1), ('Server1', 2), ('Server1', 3)]
#         self.__connector.processVMDistributionSegment(1, 1, segmentData)
#         result = self.__connector.getVMDistributionData()
#         expectedResult = [{"VMServerName":"Server1", "VMID":1}, {"VMServerName":"Server1", "VMID":2}, {"VMServerName":"Server1", "VMID":3}]
#         self.assertEquals(result, expectedResult, "VM distribution segments - one segment error")
#           
#         segmentData = []
#         self.__connector.processVMDistributionSegment(0, 0, segmentData)
#         result = self.__connector.getVMDistributionData()
#         expectedResult = []
#         self.assertEquals(result, expectedResult, "VM distribution segments - empty segment error")
#         
#     def testProcessActiveVMSegment(self):
#          
#         # Hay que crear un servidor de máquinas virtuales
#         segmentData = [('Server1', 'Ready', 'IP1', 1, 0)]
#         self.__connector.processVMServerSegment(1, 1, segmentData)
#          
#          
#         segmentData = [('machine1', 1, 1, 'Debian1', 15800, 'Password')]
#         self.__connector.processActiveVMSegment(1, 1, 'IP1', segmentData)
#         result = self.__connector.getActiveVMsData(None)
#         expectedResult = [{"VMServerName" : "Server1", "DomainUID" : "machine1", "UserID" : 1, "VMID" : 1, "VMName" : "Debian1", "VNCPort" : 15800, 
#                            "VNCPassword" : "Password" }]
#         self.assertEquals(result, expectedResult, "Active VM segment - single segment error")
#          
#     def testGetActiveVMsData(self):
#          
#         # Hay que crear un servidor de máquinas virtuales
#         segmentData = [('Server1', 'Ready', 'IP1', 1, 0)]
#         self.__connector.processVMServerSegment(1, 1, segmentData)
#          
#          
#         segmentData = [('machine1', 1, 1, 'Debian1', 15800, 'Password'), ('machine2', 2, 1, 'Debian2', 15802, 'Password')]
#         self.__connector.processActiveVMSegment(1, 1, 'IP1', segmentData)
#         result = self.__connector.getActiveVMsData(1)
#         expectedResult = [{"VMServerName" : "Server1", "DomainUID" : "machine1", "UserID" : 1, "VMID" : 1, "VMName" : "Debian1", "VNCPort" : 15800, 
#                            "VNCPassword" : "Password" }]
#         self.assertEquals(result, expectedResult, "Get active VM data error")
#          
#         result = self.__connector.getActiveVMsData(2)
#         expectedResult = [{"VMServerName" : "Server1", "DomainUID" : "machine2", "UserID" : 2, "VMID" : 1, "VMName" : "Debian2", "VNCPort" : 15802, 
#                            "VNCPassword" : "Password" }]
#         self.assertEquals(result, expectedResult, "Get active VM data error")
#          
#         result = self.__connector.getActiveVMsData(100)
#         expectedResult = []        
#         self.assertEquals(result, expectedResult, "Get active VM data error")
#          
#         result = self.__connector.getActiveVMsData(None)
#         expectedResult = [{"VMServerName" : "Server1", "DomainUID" : "machine2", "UserID" : 2, "VMID" : 1, "VMName" : "Debian2", "VNCPort" : 15802, 
#                            "VNCPassword" : "Password" },
#                           {"VMServerName" : "Server1", "DomainUID" : "machine1", "UserID" : 1, "VMID" : 1, "VMName" : "Debian1", "VNCPort" : 15800, 
#                            "VNCPassword" : "Password" }]        
#         self.assertEquals(result, expectedResult, "Get active VM data error")
#          
#     def testProcessMultipleActiveVMSegments(self):
#         # Hay que crear un servidor de máquinas virtuales
#         segmentData = [('Server1', 'Ready', 'IP1', 1, 0)]
#         self.__connector.processVMServerSegment(1, 1, segmentData)
#          
#          
#         segmentData = [('machine1', 1, 1, 'Debian1', 15800, 'Password')]
#         self.__connector.processActiveVMSegment(1, 2, 'IP1', segmentData)
#         result = self.__connector.getActiveVMsData(None)
#         expectedResult = []
#         self.assertEquals(result, expectedResult, "Active VMs - multiple segment error")
#          
#         segmentData = [('machine2', 2, 1, 'Debian2', 15802, 'Password')]
#         self.__connector.processActiveVMSegment(2, 2, 'IP1', segmentData)
#         result = self.__connector.getActiveVMsData(None)
#         expectedResult = [{"VMServerName" : "Server1", "DomainUID" : "machine2", "UserID" : 2, "VMID" : 1, "VMName" : "Debian2", "VNCPort" : 15802, 
#                            "VNCPassword" : "Password" },
#                           {"VMServerName" : "Server1", "DomainUID" : "machine1", "UserID" : 1, "VMID" : 1, "VMName" : "Debian1", "VNCPort" : 15800, 
#                            "VNCPassword" : "Password" }]        
#         self.assertEquals(result, expectedResult, "Active VMs - multiple segment error")
#          
#     def processEmptyActiveVMSegment(self):
#          
#         # Hay que crear un servidor de máquinas virtuales
#         segmentData = [('Server1', 'Ready', 'IP1', 1, 0)]
#         self.__connector.processVMServerSegment(1, 1, segmentData)        
#          
#         segmentData = [('machine1', 1, 1, 'Debian1', 15800, 'Password')]
#         self.__connector.processActiveVMSegment(1, 1, 'IP1', segmentData)
#         result = self.__connector.getActiveVMsData(None)
#         expectedResult = [{"VMServerName" : "Server1", "DomainUID" : "machine1", "UserID" : 1, "VMID" : 1, "VMName" : "Debian1", "VNCPort" : 15800, 
#                            "VNCPassword" : "Password" }]
#         self.assertEquals(result, expectedResult, "Active VM segment - empty segment error")
#          
#         segmentData = []
#         self.__connector.processActiveVMSegment(0, 0, 'IP1', segmentData)
#         result = self.__connector.getActiveVMsData(None)
#         expectedResult = []
#         self.assertEquals(result, expectedResult, "Active VM segment - empty segment error")
        
if __name__ == "__main__":
    unittest.main()