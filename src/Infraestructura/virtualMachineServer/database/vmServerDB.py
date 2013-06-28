# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: vmServerDB.py    
    Version: 5.0
    Description: Virtual machine server database connector
    
    Copyright 2012-13 Luis Barrios Hernández, Adrián Fernández Hernández,
        Samuel Guayerbas Martín

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
'''
from ccutils.databases.connector import BasicDBConnector

from virtualMachineServer.database.transfer_t import TRANSFER_T

class VMServerDBConnector(BasicDBConnector):
    '''
    Virtual machine server database connector
    '''

    def __init__(self, sqlUser, sqlPass, databaseName):
        '''
        Initializes the connector state
        Args:
            sqlUser: a MySQL user
            sqlPass: a password
            databaseName: a database name
        '''
        BasicDBConnector.__init__(self, sqlUser, sqlPass, databaseName)
        self.generateMACsAndUUIDs()
        self.generateVNCPorts()
        
    def getImageIDs(self):
        '''
        Returns the registered images' IDs
        Args:
            None
        Returns:
            A list with the registered images' IDs
        '''      
        sql = "SELECT ImageID FROM Image" 
        results = self._executeQuery(sql, False)
        imageIds = []
        for r in results:
            imageIds.append(r)
        return imageIds
    
    def getDataImagePath(self, imageID):
        '''
        Returns an images' data disk image.
        Args:
            imageID: an imageID
        Returns:
            The data disk image path. If the image does not exist,
            None will be returned.
        '''
        sql = "SELECT dataImagePath FROM Image WHERE ImageID = {0};".format(imageID)   
        result = self._executeQuery(sql, True)
        if (result == None) : 
            return None
        return result
    
    def updateBootableFlag(self, imageID, value):
        update = "UPDATE Image SET bootable = {1} WHERE imageID={0};".format(imageID, value)
        self._executeUpdate(update)
    
    def getOSImagePath(self, imageID):
        '''
        Returns an images' OS disk image.
        Args:
            imageID: an imageID
        Returns:
            The OS disk image path. If the image does not exist,
            None will be returned.
        '''
        sql = "SELECT osImagePath FROM Image WHERE ImageID = {0};".format(imageID)
        result = self._executeQuery(sql, True)
        if (result == None) : 
            return None
        return result
    
    def getDefinitionFilePath(self, imageID):
        '''
        Returns an images' definition file
        Args:
            imageID: an imageID
        Returns:
            The definition file path. If the image does not exist,
            None will be returned.
        '''
        sql = "SELECT definitionFilePath FROM Image WHERE ImageID = {0};".format(imageID)   
        result = self._executeQuery(sql)
        if (result == None) : 
            return None
        return result[0]
        
    def createImage(self, imageID, osImagePath, dataImagePath, definitionFilePath, bootable):
        """
        Registers a new image
        Args:
            imageID: the new image ID
            osImagePath: the OS disk image path
            dataImagePath: the data disk image path
            definitionFilePath: the definition file path
            bootable: indicates wether the image can be booted in copy-on-write mode or not.
        Returns:
            Nothing
        """
        if (bootable) : bootableFlag = 1
        else : bootableFlag = 0
        
        update = "INSERT INTO Image VALUES ({0}, '{1}', '{2}', '{3}', {4})"\
            .format(imageID, osImagePath, dataImagePath, definitionFilePath, bootableFlag)          
        self._executeUpdate(update)  
        
    def getBootableFlag(self, imageID):
        """
        Returns the bootable flag value associated with an image.
        Args:
            imageID: an image ID
        Returns: the bootable flag value.
        """
        query = "SELECT bootable FROM Image WHERE ImageID = {0};".format(imageID)
        flag = self._executeQuery(query, True)
        return bool(flag)
    
    def deleteImage(self, imageID):
        sql = "DELETE FROM Image WHERE ImageID = {0};".format(imageID)
        self._executeUpdate(sql) 
    
    def generateMACsAndUUIDs(self): 
        '''
        Builds and fills the FreeMACsAndUUIDsTable
        Args:
            None
        Returns:
            Nothing
        '''
        sql = "DROP TABLE IF EXISTS FreeMACsAndUUIDs"         
        self._executeUpdate(sql)  
        sql = "CREATE TABLE IF NOT EXISTS FreeMACsAndUUIDs(UUID VARCHAR(40) ,MAC VARCHAR(20),PRIMARY KEY(UUID,MAC)) ENGINE=MEMORY;"
        self._executeUpdate(sql)
        v = 0
        while v < 256 :
            x = str(hex(v))[2:].upper()
            if v < 16:
                x = '0' + x
            sql = "INSERT INTO FreeMACsAndUUIDs VALUES (UUID(),'" + '2C:00:00:00:00:' + x + "');"
            self._executeUpdate(sql)
            v = v + 1            
        
    def generateVNCPorts(self): 
        '''
        Builds an fill the FreeVNCPorts table
        Args:
            None
        Returns:
            Nothing
        '''
        sql = "DROP TABLE IF EXISTS FreeVNCPorts;" 
        self._executeUpdate(sql)  
        sql = "CREATE TABLE IF NOT EXISTS FreeVNCPorts(VNCPort INTEGER PRIMARY KEY) ENGINE=MEMORY;"
        self._executeUpdate(sql)
        p = 15000
        v = 0
        while v < 256 :
            sql = "INSERT INTO FreeVNCPorts VALUES ('" + str(p) + "');"
            self._executeUpdate(sql)
            p = p + 2
            v = v + 1
        
    def extractFreeMACAndUUID(self):
        '''
        Extracts a (freeMAC, freeUUID) pair from the FreeMACsAndUUIDs table.
        Args:
            None
        Returns.
            a (freeMAC, freeUUID) pair
        '''
        sql = "SELECT * FROM FreeMACsAndUUIDs"
        result = self._executeQuery(sql, True)
        if (result == None) : 
            return None        
        sql = "DELETE FROM FreeMACsAndUUIDs WHERE UUID = '" + result[0] + "' AND MAC ='" + result[1] + "'"
        self._executeUpdate(sql)
        return (result[0], result[1])
    
    def freeMACAndUUID(self, UUID, MAC):
        '''
        Frees a MAC address and a domain UUID.
        Args:
            UUID: the UUID to be freed
            MAC: the MAC address to be freed
        Returns:
            Nothing
        '''
        sql = "INSERT INTO FreeMACsAndUUIDs VALUES ('" + UUID + "','" + MAC + "')"
        self._executeUpdate(sql)
        
    def extractFreeVNCPort(self):
        '''
        Extracts a free VNC port from the FreeVNCPorts table
        Args:
            None
        Returns:
            the extracted free VNC port
        '''
        sql = "SELECT * FROM FreeVNCPorts"
        result = self._executeQuery(sql, True)
        if (result == None) : 
            return None
        sql = "DELETE FROM FreeVNCPorts WHERE VNCPort = '" + str(result) + "'"
        self._executeUpdate(sql)
        return result
    
    def freeVNCPort(self, VNCPort):
        """
        Frees a VNC port
        Args:
            VNCPort: the VNC port to be freed
        Returns:
            Nothing
        """
        sql = "INSERT INTO FreeVNCPorts VALUES ('" + str(VNCPort) + "')"
        self._executeUpdate(sql)      
    
    def getDomainDataImagePath(self, domainName):
        """
        Returns a domain data disk image path
        Args:
            domainName: the domain name
        Returns:
            the domain data disk image path
        """
        sql = "SELECT dataImagePath FROM ActiveVM  WHERE domainName = '{0}';".format(domainName)        
        result = self._executeQuery(sql, True)
        if (result == None) : 
            return None
        return result
    
    def getDomainOSImagePath(self, domainName): 
        """
        Returns a domain OS disk image path
        Args:
            domainName: the domain name
        Returns:
            the domain OS disk image path
        """      
        sql = "SELECT osImagePath FROM ActiveVM WHERE domainName = '" + str(domainName) + "'" 
        result = self._executeQuery(sql, True)
        if (result == None) : 
            return None
        return result
    
    def getDomainMACAddress(self, domainName):
        """
        Returns a domain MAC address
        Args:
            domainName: the domain name
        Returns:
            the domain MAC address
        """
        sql = "SELECT macAddress FROM ActiveVM WHERE domainName = '" + str(domainName) + "'" 
        result = self._executeQuery(sql, True)
        if (result == None) : 
            return None
        return result
    
    def getDomainUUID(self, domainName):
        """
        Returns a domain UUID
        Args:
            domainName: the domain name
        Returns:
            the domain UUID
        """
        sql = "SELECT uuid FROM ActiveVM WHERE domainName = '" + str(domainName) + "'" 
        result = self._executeQuery(sql, True)
        if (result == None) : 
            return None
        return result
    
    def getDomainVNCPassword(self, domainName): 
        """
        Returns a domain VNC port
        Args:
            domainName: the domain name
        Returns:
            the domain VNC port
        """       
        sql = "SELECT VNCPass FROM ActiveVM WHERE domainName = '" + str(domainName) + "'" 
        result = self._executeQuery(sql, True)
        if (result == None) : 
            return None
        return result
    
    def getDomainImageID(self, domainName):
        """
        Returns a domain image ID
        Args:
            domainName: the domain name
        Returns:
            the domain image ID
        """   
        sql = "SELECT ImageID FROM ActiveVM WHERE domainName = '" + str(domainName) + "'" 
        result = self._executeQuery(sql, True)
        if (result == None) : 
            return None
        return result         
    
    def getDomainNameFromVNCPort(self, vncPort): 
        """
        Returns a domain name from its VNC server port
        Args:
            vncPort: a domain VNC server port
        Returns:
            the domain name
        """      
        sql = "SELECT domainName FROM ActiveVM WHERE VNCPort = '" + str(vncPort) + "'" 
        result = self._executeQuery(sql, True)
        if (result == None) : 
            return None
        return result
    
    def getWebsockifyDaemonPID(self, domainName):
        """
        Returns a domain websockify daemon's PID
        Args:
            domainName: a domain name
        Returns:
            the domain websockify daemon PID
        """     
        sql = "SELECT websockifyPID FROM ActiveVM WHERE domainName = '" + str(domainName) + "'" 
        result = self._executeQuery(sql, True)
        if (result == None) : 
            return None
        return result      
    
    def getDomainOwnerID(self, domainName):
        """
        Returns a domain owner's ID
        Args:
            domainName: a domain name
        Returns:
            the domain owner's PID
        """     
        sql = "SELECT userId FROM ActiveVM WHERE domainName = '" + str(domainName) + "'" 
        result = self._executeQuery(sql, True)
        if (result == None) : 
            return None
        return int(result)
    
    def registerVMResources(self, domainName, imageID, vncPort, vncPassword, userId, websockifyPID, osImagePath, dataImagePath, MAC, UUID):
        """
        Registers the resources assigned to a domain.
        Args:
            domainName: the domain name
            imageID: the domain image ID
            vncPort: the domain VNC server port
            vncPassword: the domain VNC server password
            userID: the domain owner ID
            websockifyPID: the domain websockify daemon PID
            osImagePath: the domain OS disk image
            dataImagePath: the domain data disk image
            MAC: the domain MAC address
            UUID: the domain UUID
        Returns:
            Nothing
        """
        sql = "INSERT INTO ActiveVM VALUES('{0}', {1}, {2}, '{3}', {4}, {5}, '{6}', '{7}', '{8}', '{9}')" \
            .format(domainName, imageID, vncPort, vncPassword[:-1], userId, websockifyPID,
                    osImagePath, dataImagePath, MAC, UUID);
        self._executeUpdate(sql)        
        return vncPort 
    
    def unregisterDomainResources(self, domainName):
        """
        Unregisters the resources assigned to a domain
        Args:
            domainName: a domain name
        Returns:
            Nothing
        """
        update = "DELETE FROM ActiveVM WHERE domainName = '" + str(domainName) + "'"
        self._executeUpdate(update)        
        
    def getDomainsConnectionData(self):
        '''
        Returns the active virtual machines' connection data
        Args:
            None
        Returns:
            A list of dictionaries containing the active virtual machines' connection data
        '''
        query = "SELECT ActiveDomainUIDs.commandID, ActiveVM.userId, ActiveVM.ImageID, ActiveVM.domainName, ActiveVM.VNCPort, ActiveVM.VNCPass\
            FROM ActiveVM, ActiveDomainUIDs WHERE ActiveVM.domainName = ActiveDomainUIDs.domainName;"
        results = self._executeQuery(query, False)
        if (results == None) :
            return []
        else :
            ac = []
            for row in results:
                ac.append({"DomainID" : row[0], "UserID" : int(row[1]), "ImageID" : int(row[2]), "VMName": row[3], "VNCPort" : int(row[4]), "VNCPass" : row[5]})
            return ac
        
    def addVMBootCommand(self, domainName, commandID):
        """
        Registers a virtual machine boot command's ID
        Args:
            domainName: a domain name
            commandID: the boot command's unique ID
        Returns:
            Nothing
        """
        update = "INSERT INTO ActiveDomainUIDs VALUES ('{0}', '{1}');".format(domainName, commandID)
        self._executeUpdate(update)
        
    def getVMBootCommand(self, domainName):
        """
        Reads a domain boot command's ID
        Args:
            domainName: a domain name
        Returns:
            the domain boot command's ID
        """
        query = "SELECT commandID FROM ActiveDomainUIDs WHERE domainName = '" + domainName + "';"
        result = self._executeQuery(query, True)
        if (result == None) :
            return None
        else :
            return result
        
    def getDomainNameFromVMBootCommand(self, commandID):
        """
        Finds a domain name using a domain boot command ID
        Args:
            commandID: the domain boot command's ID
        Returns:
            the domain name associated with the domain boot command
        """
        query = "SELECT domainName FROM ActiveDomainUIDs WHERE commandID = '{0}';".format(commandID)
        result = self._executeQuery(query, True)
        if (result == None) :
            return None
        else :
            return result
    
    def __getAssignedMACsAndVNCPorts(self):
        """
        Returns the MAC addresses and VNC ports assigned to the active virtual machines.
        Args:
            None
        Returns:
            a pair (assignedMACs, assignedVNCPorts), where assignedMACs and assignedPorts are
            the lists of assigned MAC addresses and assigned VNCPorts.
        """
        query = "SELECT macAddress, VNCPort FROM ActiveVM;"
        result = self._executeQuery(query, False)
        assignedMACs, assignedVNCPorts = ([], [])
        if (result != None) :
            for row in result :
                assignedMACs.append(row[0])
                assignedVNCPorts.append(int(row[1]))
                assignedVNCPorts.append(int(row[1]) + 1)
        return (assignedMACs, assignedVNCPorts)      
    
    def __allocateMACAddressAndUUID(self, macAddr):
        """
        Allocates a MAC address and a UUID
        Args:
            macAddr: the MAC addr to allocate
        Returns:
            Nothing
        """
        command = "DELETE FROM FreeMACsAndUUIDs WHERE MAC ='{0}';".format(macAddr)    
        self._executeUpdate(command)      
        
    def __allocateVNCPort(self, port):
        """
        Allocates a VNC server port
        Args:
            port: the VNC port to allocate
        Returns:
            Nothing
        """
        command = "DELETE FROM FreeVNCPorts WHERE VNCPort = {0};".format(port)
        self._executeUpdate(command)
            
    def getActiveDomainUIDs(self):
        """
        Returns the active virtual machines' IDs
        Args:
            None
        Returns:
            a list containing the active virtual machines' IDs
        """
        query = "SELECT CommandID FROM ActiveDomainUIDs;"
        rows = self._executeQuery(query, False)
        if (rows == None) :
            return []
        result = []
        for row in rows :
            result.append(row)
        return result
    
    def getRegisteredDomainNames(self):
        """
        Returns the active virtual machines' names
        Args:
            None
        Returns:
            a list containing the active virtual machines' names
        """
        query = "SELECT domainName FROM ActiveVM;"
        results = self._executeQuery(query, False)
        if (results == None) :
            return []
        else :
            ac = []
            for row in results:
                ac.append(row)
            return ac
        
    def allocateAssignedMACsUUIDsAndVNCPorts(self):
        """
        Allocates the MAC addresses, UUIDs and VNC server ports used by the active virtual machines.
        Args:
            None
        Returns:
            Nothing
        """
        assignedMACs, assignedVNCPorts = self.__getAssignedMACsAndVNCPorts()
        for macAddress in assignedMACs :
            self.__allocateMACAddressAndUUID(macAddress)
        for port in assignedVNCPorts :
            self.__allocateVNCPort(port)
        
    def addToTransferQueue(self, data):
        """
        Queues a transfer
        Args:
            data: a dictionary containing the transfer's data
        Returns:
            Nothing
        """
        serialized_data = ""
        serialized_data += str(data["Transfer_Type"]) + "$"
        serialized_data += data["RepositoryIP"] + "$"
        serialized_data += str(data["RepositoryPort"]) + "$"
        serialized_data += data["CommandID"] + "$"
        if (data["Transfer_Type"] == TRANSFER_T.STORE_IMAGE) :
            serialized_data += str(data["TargetImageID"]) + "$"
            serialized_data += data["SourceFilePath"]
        elif (data["Transfer_Type"] != TRANSFER_T.CANCEL_EDITION) :        
            serialized_data += str(data["SourceImageID"]) + "$"
            if (data["Transfer_Type"] == TRANSFER_T.CREATE_IMAGE or data["Transfer_Type"] == TRANSFER_T.EDIT_IMAGE) :    
                serialized_data += str(data["UserID"])
        else :
            serialized_data += str(data["ImageID"])
        
        
        insert = "INSERT INTO TransferQueue(data) VALUES ('{0}');".format(serialized_data)
        self._executeUpdate(insert)  

    def peekFromTransferQueue(self):
        """
        Reads the transfer queue's head
        Args:
            None
        Returns:
            A dictionary with the transfer queue head's data. If the transfer queue is empty, None
            will be returned. 
        """
        query = "SELECT MIN(position) FROM TransferQueue;"
        first_element_ID = self._executeQuery(query, True)
        if (first_element_ID == None) :
            return None
        query = "SELECT data FROM TransferQueue WHERE position = {0};".format(first_element_ID)
        serialized_data = self._executeQuery(query, True)
        tokens = serialized_data.split("$")
        result = dict()
        result["Transfer_Type"] = int(tokens[0]) 
        result["RepositoryIP"] = tokens[1]
        result["RepositoryPort"] = int(tokens[2])
        result["CommandID"] = tokens[3]
        if (result["Transfer_Type"] == TRANSFER_T.STORE_IMAGE) :
            result["TargetImageID"] = int(tokens[4])
            result["SourceFilePath"] = tokens[5]           
        elif (result["Transfer_Type"] != TRANSFER_T.CANCEL_EDITION) :   
            result["SourceImageID"] = int(tokens[4])
            if (result["Transfer_Type"] == TRANSFER_T.CREATE_IMAGE or result["Transfer_Type"] == TRANSFER_T.EDIT_IMAGE) :             
                result["UserID"] = int(tokens[5])
        else :
            result["ImageID"] = int(tokens[4])
        return result
        
    def removeFirstElementFromTransferQueue(self):
        """
        Removes the transfer queue's head
        Args:
            None
        Returns:
            Nothing
        """
        query = "SELECT MIN(position) FROM TransferQueue;"
        first_element_ID = self._executeQuery(query, True)
        if (first_element_ID == None) :
            return
        else :
            first_element_ID = first_element_ID
        update = "DELETE FROM TransferQueue WHERE position = {0};".format(first_element_ID)
        self._executeUpdate(update)
    
    def addToCompressionQueue(self, data):
        """
        Queues a compression/extraction operation
        Args:
            data: a dictionary containing the operation's data
        Returns:
            Nothing
        """
        serialized_data = ""
        serialized_data += str(data["Transfer_Type"]) + "$"
        serialized_data += data["CommandID"] + "$"
        serialized_data += str(data["TargetImageID"]) + "$"
        serialized_data += data["RepositoryIP"] + "$"
        serialized_data += str(data["RepositoryPort"]) + "$"
        if (data["Transfer_Type"] == TRANSFER_T.STORE_IMAGE) :
            serialized_data += data["OSImagePath"] + "$"
            serialized_data += data["DataImagePath"] + "$"
            serialized_data += data["DefinitionFilePath"] + "$"            
        else :
            serialized_data += str(data["SourceImageID"]) 
            if (data["Transfer_Type"] != TRANSFER_T.DEPLOY_IMAGE) :            
                serialized_data += "$" + str(data["UserID"])
            
        insert = "INSERT INTO CompressionQueue(data) VALUES ('{0}');".format(serialized_data)
        self._executeUpdate(insert)  
            
    def peekFromCompressionQueue(self):
        """
        Reads the compression queue's head
        Args:
            None
        Returns:
            A dictionary with the compression queue head's data. If the compression queue is empty, None
            will be returned. 
        """
        query = "SELECT MIN(position) FROM CompressionQueue;"
        first_element_ID = self._executeQuery(query, True)
        if (first_element_ID == None) :
            return None
        query = "SELECT data FROM CompressionQueue WHERE position = {0};".format(first_element_ID)
        serialized_data = self._executeQuery(query, True)
        tokens = serialized_data.split("$")
        result = dict()
        result["Transfer_Type"] = int(tokens[0])
        result["CommandID"] = tokens[1]
        result["TargetImageID"] = int(tokens[2])
        result["RepositoryIP"] = tokens[3]
        result["RepositoryPort"] = int(tokens[4])
        if (result["Transfer_Type"] == TRANSFER_T.STORE_IMAGE) :
            result["OSImagePath"] = tokens[5]
            result["DataImagePath"] = tokens[6]
            result["DefinitionFilePath"] = tokens[7]            
        else:
            result["SourceImageID"] = int(tokens[5])
            if (result["Transfer_Type"] != TRANSFER_T.DEPLOY_IMAGE) :
                result["UserID"] = int(tokens[6])
            
        return result
            
    def removeFirstElementFromCompressionQueue(self):
        """
        Removes the compression queue's head
        Args:
            None
        Returns:
            Nothing
        """
        query = "SELECT MIN(position) FROM CompressionQueue;"
        first_element_ID = self._executeQuery(query, True)
        if (first_element_ID == None) :
            return
        update = "DELETE FROM CompressionQueue WHERE position = {0};".format(first_element_ID)
        self._executeUpdate(update)
    
    def addValueToConnectionDataDictionary(self, commandID, value):
        """
        Stores the image repository connection data into the connection data dictionary
        Args:
            commandID: an image edition command's ID
            value: a dictionary containing the image repository connection data associated with the image edition command
        Returns:
            Nothing
        """
        serialized_data = value["RepositoryIP"] + "$" + str(value["RepositoryPort"])
        update = "INSERT INTO ConnectionDataDictionary VALUES('{0}', '{1}');".format(commandID, serialized_data)
        self._executeUpdate(update)
        
    def getImageRepositoryConnectionData(self, commandID):
        """
        Reads the image repository connection data from the connection data dictionary
        Args:
            commandID: an image edition command's ID
        Returns:
            a dictionary containing the image repository connection data associated with the image edition command
        """
        query = "SELECT value FROM ConnectionDataDictionary WHERE dict_key = '{0}';".format(commandID)
        result = self._executeQuery(query)
        if (result == None) :
            return None
        else:
            result = result[0]
        value = dict()
        tokens = result.split("$")
        value["RepositoryIP"] = tokens[0]
        value["RepositoryPort"] = int(tokens[1])
        return value
    
    def removeImageRepositoryConnectionData(self, commandID):
        """
        Removes the image repository connection data from the connection data dictionary
        Args:
            commandID: an image edition command's ID
        Returns:
            Nothing
        """
        update = "DELETE FROM ConnectionDataDictionary WHERE dict_key = '{0}';".format(commandID)
        self._executeUpdate(update)        