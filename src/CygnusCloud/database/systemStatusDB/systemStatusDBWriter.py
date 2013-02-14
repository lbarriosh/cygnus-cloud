# -*- coding: UTF8 -*-
'''
Web status database writer

@author: Luis Barrios Hernández
@version: 2.0
'''

from database.utils.connector import BasicDatabaseConnector

class SystemStatusDatabaseWriter(BasicDatabaseConnector):
    def __init__(self, sqlUser, sqlPassword, databaseName):
        BasicDatabaseConnector.__init__(self, sqlUser, sqlPassword, databaseName)
        self.__vmServerSegments = []
        self.__imageDistributionSegments = []
        self.__activeVMSegments = dict()
        
    def processVMServerSegment(self, segmentNumber, segmentCount, data):
        self.__vmServerSegments.append(data)
        if (len(self.__vmServerSegments) == segmentCount) :
            # Write changes to the database
            command = "DELETE FROM VirtualMachineServer;"
            self._executeUpdate(command)
            command = "INSERT INTO VirtualMachineServer VALUES " + SystemStatusDatabaseWriter.__segmentsToStr(self.__vmServerSegments)
            self.__vmServerSegments = []            
            self._executeUpdate(command)
            
    def processVMDistributionSegment(self, segmentNumber, segmentCount, data):
        self.__imageDistributionSegments.append(data)
        if (len(self.__imageDistributionSegments) == segmentCount) :
            # Write changes to the database
            command = "DELETE FROM VirtualMachineDistribution;"
            self._executeUpdate(command)
            command = "INSERT INTO VirtualMachineDistribution VALUES " + SystemStatusDatabaseWriter.__segmentsToStr(self.__imageDistributionSegments)
            self.__imageDistributionSegments = []            
            self._executeUpdate(command)
            
    def processActiveVMSegment(self, segmentNumber, segmentCount, vmServerIP, data):
        if (not self.__activeVMSegments.has_key(vmServerIP)) :
            self.__activeVMSegments[vmServerIP] = []
        self.__activeVMSegments[vmServerIP].append(data)
        if (len(self.__activeVMSegments[vmServerIP]) == segmentCount) :
            # Fetch the virtual machine server's name
            serverName = self.__getVMServerName(vmServerIP)
            # Write changes to the database
            command = "DELETE FROM ActiveVirtualMachines WHERE serverName = '" + serverName + "';"
            self._executeUpdate(command)
            command = "INSERT INTO ActiveVirtualMachines VALUES " + SystemStatusDatabaseWriter.__segmentsToStr(self.__activeVMSegments[vmServerIP], [serverName])
            self.__activeVMSegments[vmServerIP] = []         
            self._executeUpdate(command)
            
    def __getVMServerName(self, serverIP):
        query = "SELECT serverName FROM VirtualMachineServer WHERE serverIP = '" + serverIP + "';"
        result = self._executeQuery(query, True)
        return result[0]
                        
    @staticmethod
    def __segmentsToStr(segmentList, dataToAdd = []):
        isFirstSegment = True
        command = ""
        for segment in segmentList :
            for segmentTuple in segment :
                if (isFirstSegment) :
                    isFirstSegment = False
                else :
                    command += ", "
                segmentTuple_list = dataToAdd + list(segmentTuple)
                command += str(tuple(segmentTuple_list))
        command += ";"
        return command    