# -*- coding: UTF8 -*-
'''
Web status database writer

@author: Luis Barrios Hernández
@version: 2.1
'''

from database.utils.connector import BasicDatabaseConnector

class SystemStatusDatabaseWriter(BasicDatabaseConnector):
    """
    Initializes the writer's state
    Args:
        sqlUser: the SQL user to use
        sqlPassword: the SQL user's password
        databaseName: the database's name
    """
    def __init__(self, sqlUser, sqlPassword, databaseName):
        BasicDatabaseConnector.__init__(self, sqlUser, sqlPassword, databaseName)
        self.__vmServerSegments = []
        self.__imageDistributionSegments = []
        self.__activeVMSegments = dict()
        
    def processVMServerSegment(self, segmentNumber, segmentCount, data):
        """
        Processes a virtual machine server basic data segment.
        Args:
            segmentNumber: the segment's position in the sequence
            segmentCount: the total number of segments in the sequence
            data: the data to process
        Returns:
            Nothing
        """
        self.__vmServerSegments.append(data)
        if (len(self.__vmServerSegments) == segmentCount) :
            # Write changes to the database
            command = "DELETE FROM VirtualMachineServer;"
            self._executeUpdate(command)
            command = "INSERT INTO VirtualMachineServer VALUES " + SystemStatusDatabaseWriter.__segmentsToSQLTuples(self.__vmServerSegments)
            self.__vmServerSegments = []            
            self._executeUpdate(command)
            
    def processVMDistributionSegment(self, segmentNumber, segmentCount, data):
        """
        Processes a virtual machine distribution data segment.
        Args:
            segmentNumber: the segment's position in the sequence
            segmentCount: the total number of segments in the sequence
            data: the data to process
        Returns:
            Nothing
        """
        self.__imageDistributionSegments.append(data)
        if (len(self.__imageDistributionSegments) == segmentCount) :
            # Write changes to the database
            command = "DELETE FROM VirtualMachineDistribution;"
            self._executeUpdate(command)
            command = "INSERT INTO VirtualMachineDistribution VALUES " + SystemStatusDatabaseWriter.__segmentsToSQLTuples(self.__imageDistributionSegments)
            self.__imageDistributionSegments = []            
            self._executeUpdate(command)
            
    def processActiveVMSegment(self, segmentNumber, segmentCount, vmServerIP, data):
        """
        Processes an active virtual machine data segment.
        Args:
            segmentNumber: the segment's position in the sequence
            segmentCount: the total number of segments in the sequence
            vmServerIP: the host virtual machine server's IP
            data: the data to process
        Returns:
            Nothing
        """
        if (not self.__activeVMSegments.has_key(vmServerIP)) :
            self.__activeVMSegments[vmServerIP] = []
        self.__activeVMSegments[vmServerIP].append(data)
        if (len(self.__activeVMSegments[vmServerIP]) == segmentCount) :
            # Fetch the virtual machine server's name
            serverName = self.__getVMServerName(vmServerIP)
            # Write changes to the database
            command = "DELETE FROM ActiveVirtualMachines WHERE serverName = '" + serverName + "';"
            self._executeUpdate(command)
            command = "INSERT INTO ActiveVirtualMachines VALUES " + SystemStatusDatabaseWriter.__segmentsToSQLTuples(self.__activeVMSegments[vmServerIP], [serverName])
            self.__activeVMSegments[vmServerIP] = []         
            self._executeUpdate(command)
            
    def __getVMServerName(self, serverIP):
        """
        Returns the virtual machine server name that is linked to the given IP.
        Args:
            serverIP: a virtual machine server's IP
        Returns:
            the virtual machine server's name
        """
        query = "SELECT serverName FROM VirtualMachineServer WHERE serverIP = '" + serverIP + "';"
        result = self._executeQuery(query, True)
        return result[0]
                        
    @staticmethod
    def __segmentsToSQLTuples(segmentList, dataToAdd = []):
        """
        Converts a list of segments into a list of SQL tuples
        Args:
            segmentList: a list of segments.
            dataToAdd: a list of data to add to EVERY segment
        Returns:
            A SQL tuple string with the supplied data.
        """
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