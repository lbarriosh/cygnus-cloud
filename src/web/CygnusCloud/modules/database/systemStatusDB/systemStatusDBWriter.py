# -*- coding: UTF8 -*-
'''
Web status database writer

@author: Luis Barrios Hernández
@version: 3.2
'''

from database.utils.connector import BasicDatabaseConnector

class SystemStatusDatabaseWriter(BasicDatabaseConnector):
    """
    This objects update the system status database with the data sent from a cluster server.
    """
    def __init__(self, sqlUser, sqlPassword, databaseName):
        """
        Initializes the writer's state
        Args:
        sqlUser: the SQL user to use
        sqlPassword: the SQL user's password
        databaseName: the database's name
        """
        BasicDatabaseConnector.__init__(self, sqlUser, sqlPassword, databaseName)
        self.__vmServerSegmentsData = []
        self.__vmServerSegments = 0
        self.__imageDistributionSegmentsData = []
        self.__imageDistributionSegments = 0
        self.__activeVMSegmentsData = dict()
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
        if (data != []) :
            self.__vmServerSegmentsData += data
            self.__vmServerSegments += 1
        if (self.__vmServerSegments == segmentCount) :
            receivedData = SystemStatusDatabaseWriter.__getVMServersDictionary(self.__vmServerSegmentsData)
            registeredIDs = self.__getKnownVMServerIDs()
            # Step 1: remove the nonexistent rows
            if (registeredIDs != None) :
                for ID in registeredIDs :
                    if not (receivedData.has_key(ID)) :
                        self.__deleteVMServer(ID)
            # Step 2: classify the segment's data
            inserts = []
            for ID in receivedData.keys() :
                if (registeredIDs != None and ID in registeredIDs) :
                    self.__updateVMServerData(receivedData[ID])
                else :
                    inserts.append(receivedData[ID])
            # Step 3: write changes to the database
            if (inserts != []) :
                self.__insertVMServers(inserts)
            self.__vmServerSegmentsData = [] 
            self.__vmServerSegments = 0
            
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
        if (data != []) :
            self.__imageDistributionSegmentsData.append(data)
            self.__imageDistributionSegments += 1
        if (self.__imageDistributionSegments == segmentCount) :
            # Write changes to the database
            command = "DELETE FROM VirtualMachineDistribution;"
            self._executeUpdate(command)
            if (self.__imageDistributionSegmentsData != []) :
                command = "INSERT INTO VirtualMachineDistribution VALUES " + SystemStatusDatabaseWriter.__convertSegmentsToSQLTuples(self.__imageDistributionSegmentsData)
                self.__imageDistributionSegmentsData = []   
                self.__imageDistributionSegments = 0         
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
        if (not self.__activeVMSegmentsData.has_key(vmServerIP)) :
            self.__activeVMSegmentsData[vmServerIP] = []
            self.__activeVMSegments[vmServerIP] = 0
        if (data != []) :
            self.__activeVMSegmentsData[vmServerIP] += data
            self.__activeVMSegments[vmServerIP] += 1
        if (self.__activeVMSegments[vmServerIP] == segmentCount) :
            receivedData = SystemStatusDatabaseWriter.__getActiveVMsDictionary(self.__activeVMSegmentsData[vmServerIP])
            registeredIDs = self.__getActiveVMIDs()
            # Step 1: remove the nonexistent rows
            if (registeredIDs != None) :
                for ID in registeredIDs :
                    if not (receivedData.has_key(ID)) :
                        self.__deleteActiveVM(ID)
            # Step 2: classify the segment's data
            inserts = []
            for ID in receivedData.keys() :
                if (registeredIDs != None and not (ID in registeredIDs)) :
                    inserts.append(receivedData[ID])
            # Step 3: write changes to the database
            if (inserts != []) :
                self.__insertActiveVMData(self.__getVMServerName(vmServerIP), inserts)
            self.__activeVMSegmentsData[vmServerIP] = []
            self.__activeVMSegments[vmServerIP] = 0
        
    @staticmethod    
    def __getVMServersDictionary(segmentList):
        """
        Turns a list of virtual machine server tuples into a dictionary. Its keys
        are the virtual machine servers' IDs, and its values are the matching tuples.
        Args:
            segmentList: a list of tuples with the virtual machine server's data.
        Returns:
            A dictionary <virtual machine server ID, tuple)
        """
        result = {}
        for segment in segmentList :
            result[segment[0]] = segment
        return result
    
    @staticmethod
    def __getActiveVMsDictionary(segmentList):
        """
        Turns a list of active VMs into a dictionary. Its keys are the
        VM's IDs, and its values are the matching tuples.
        Args:
            segmentList: a list of tuples with the virtual machine's data.
        Returns:
            A dictionary <VM ID, tuple)
        """
        result = {}
        for segment in segmentList :
            result[(segment[0], segment[1], segment[2])] = segment
        return result
                
    def __getKnownVMServerIDs(self):
        """
        Return the known (or registered) virtual machine server IDs.
        Args:
            None
        Returns:
            A list with the known VM server IDs.
        """
        query = "SELECT serverName FROM VirtualMachineServer;";
        result = set()
        output = self._executeQuery(query, False)
        for t in output :
            result.add(t[0])
        return result
            
    def __insertVMServers(self, tupleList):
        """
        Inserts virtual machine servers' data into the status database
        Args:
            tupleList: a list of tuples with the VM server's data
        Returns:
            Nothing
        """
        update = "INSERT INTO VirtualMachineServer VALUES {0};"\
            .format(SystemStatusDatabaseWriter.__convertTuplesToSQLStr(tupleList))
        self._executeUpdate(update)
        
    def __updateVMServerData(self, data):
        """
        Updates a virtual machine server's data.
        Args: 
            data: a tuple containing the new VM server's data
        Returns:
            Nothing            
        """
        update = "UPDATE VirtualMachineServer SET serverStatus='{1}', serverIP='{2}', serverPort={3}\
            WHERE serverName='{0}'".format(data[0], data[1], data[2], data[3])
        self._executeUpdate(update)
        
    def __deleteVMServer(self, serverID):
        """
        Deletes a virtual machine server from the status database
        Args:
            serverID: the VM server's ID
        Returns:
            Nothing
        """
        # Workaround: ON DELETE CASCADE only works with MySQL's InnoDB engine.
        update = "DELETE FROM ActiveVirtualMachines WHERE serverName = '{0}';".format(serverID)
        self._executeUpdate(update)
        update = "DELETE FROM VirtualMachineServer WHERE serverName = '{0}'".format(serverID)
        self._executeUpdate(update)        
            
    def __getActiveVMIDs(self):
        """
        Return the known active VM ID's
        Args:
            None
        Returns:
            A list with the known active VM ID's.
        """
        query = "SELECT serverName, userID, virtualMachineID FROM ActiveVirtualMachines;"
        results = self._executeQuery(query)
        output = set()
        for row in results :
            output.add((row[0], row[1], row[2]))
        return output
    
    def __insertActiveVMData(self, vmServerIP, data):
        """
        Inserts some active VM's data into the status database.
        Args:
            vmServerIP: the host VM server's IP
            data: a list with the new active VM's data
        Returns:
            Nothing
        """
        update = "INSERT INTO ActiveVirtualMachines VALUES {0};"\
            .format(SystemStatusDatabaseWriter.__convertTuplesToSQLStr(data, [vmServerIP]))
        self._executeUpdate(update)
        
    def __deleteActiveVM(self, machineID):
        """
        Deletes an active VM.
        Args:
            machineID: the active VM's ID.
        Returns:
            Nothing
        """
        update = "DELETE FROM ActiveVirtualMachines WHERE serverName='{0}' AND userID={1} AND virtualMachineID={2};"\
            .format(machineID[0], machineID[1], machineID[2])
        self._executeUpdate(update)
            
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
    def __convertTuplesToSQLStr(tupleList, dataToAdd = []):
        """
        Converts a list of tuples into a SQL data string.
        Args:
            tupleList: a list of tuples.
            dataToAdd: a list of data to add to EVERY segment
        Returns:
            A SQL string with the supplied data.
        """
        isFirstSegment = True
        command = ""
        for segmentTuple in tupleList :
            if (isFirstSegment) :
                isFirstSegment = False
            else :
                command += ", "
            segmentTuple_list = dataToAdd + list(segmentTuple)
            command += str(tuple(segmentTuple_list))
        return command    
    
    @staticmethod
    def __convertSegmentsToSQLTuples(segmentList):
        """
        Converts a list of segments into a SQL data string.
        Args:
            segmentList: a list of segments.
            dataToAdd: a list of data to add to EVERY segment
        Returns:
            A SQL string with the supplied data.
        """
        isFirstSegment = True
        command = ""
        for segment in segmentList :
            for segmentTuple in segment :
                if (isFirstSegment) :
                    isFirstSegment = False
                else :
                    command += ", "
                command += str(segmentTuple)
        command += ";"
        return command    