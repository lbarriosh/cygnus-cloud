# -*- coding: UTF8 -*-
'''
Web status database unit tests
@author: Luis Barrios Hernández
@version: 1.0
'''
import unittest

from database.utils.configuration import DBConfigurator
from database.systemStatusDB.systemStatusDBReader import SystemStatusDatabaseReader
from database.systemStatusDB.systemStatusDBWriter import SystemStatusDatabaseWriter

class Test(unittest.TestCase):      

    def setUp(self):
        dbConfigurator = DBConfigurator("")
        dbConfigurator.runSQLScript("SystemStatusDBTest", "./SystemStatusDBTest.sql")
        dbConfigurator.addUser("website", "cygnuscloud", "SystemStatusDBTest", False)
        dbConfigurator.addUser("statusDBUpdater", "cygnuscloud", "SystemStatusDBTest", True)
        self.__reader = SystemStatusDatabaseReader("website", "cygnuscloud", "SystemStatusDBTest")
        self.__reader.connect()
        self.__writer = SystemStatusDatabaseWriter("statusDBUpdater", "cygnuscloud", "SystemStatusDBTest")
        self.__writer.connect()

    def tearDown(self):
        self.__reader.disconnect()
        self.__writer.disconnect()
        dbConfigurator = DBConfigurator("")
        dbConfigurator.dropDatabase("SystemStatusDBTest")

    def testUpdateVMServerData(self):
        segment1Data = [('Server1', 'Ready', 'IP1', 1)]
        segment2Data = [('Server2', 'Booting', 'IP2', 1)]
        self.__writer.processVMServerSegment(1, 2, segment1Data)
        serversData = self.__reader.getVMServersData()
        self.assertEquals(serversData, [], "processVMServerSegment does not work")
        self.__writer.processVMServerSegment(2, 2, segment2Data)
        serversData = self.__reader.getVMServersData()
        d1 = {"VMServerName":"Server1", "VMServerStatus":"Ready", "VMServerIP":"IP1", "VMServerListenningPort":1L}
        d2 = {"VMServerName":"Server2", "VMServerStatus":"Booting", "VMServerIP":"IP2", "VMServerListenningPort":1L}
        self.assertEquals(serversData, [d1,d2], "processVMServerSegment does not work")
        segment3Data = [("Server3", "Ready", "IP3", 1)]
        self.__writer.processVMServerSegment(1, 1, segment3Data)
        serversData = self.__reader.getVMServersData()
        d3 = {"VMServerName":"Server3", "VMServerStatus":"Ready", "VMServerIP":"IP3", "VMServerListenningPort":1}
        self.assertEquals(serversData, [d3], "processVMServerSegment does not work")
        
    def testUpdateVMDistributionData(self):
        segment1Data = [('Server1', 1), ('Server1', 2), ('Server1', 3)]
        segment2Data = [('Server2', 1), ('Server2', 4), ('Server2', 5)]
        self.__writer.processVMDistributionSegment(1, 2, segment1Data)
        serversData = self.__reader.getVMServersData()
        self.assertEquals(serversData, [], "processVMDistributionSegment does not work")
        self.__writer.processVMDistributionSegment(2, 2, segment2Data)
        serversData = self.__reader.getVMDistributionData()
        d1 = {"VMServerName":"Server1", "VMID":1}
        d2 = {"VMServerName":"Server1", "VMID":2}
        d3 = {"VMServerName":"Server1", "VMID":3}
        d4 = {"VMServerName":"Server2", "VMID":1}
        d5 = {"VMServerName":"Server2", "VMID":4}
        d6 = {"VMServerName":"Server2", "VMID":5}
        self.assertEquals(serversData, [d1,d2,d3,d4,d5,d6], "processVMDistributionSegment does not work")
        segment3Data = [('Server4', 10)]
        self.__writer.processVMDistributionSegment(1, 1, segment3Data)
        serversData = self.__reader.getVMDistributionData()
        d1 = {"VMServerName":"Server4", "VMID":10}
        self.assertEquals(serversData, [d1], "processVMDistributionSegment does not work")
        
if __name__ == "__main__":
    unittest.main()