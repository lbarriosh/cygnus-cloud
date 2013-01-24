# -*- coding: UTF8 -*-
import MySQLdb

from utils.enums import enum

SERVER_STATE_T = enum("BOOTING", "READY")

class VMServerManager(object):
    '''
        This objects register and delete virtual machine servers to the database.    '''


    def __init__(self, sqlUser, sqlPassword, databaseName):
        '''
            Initializes the manager's state
            Args:
                sqlUser: the user to use to connect to a MySQL database
                sqlPassword: the password to use to connecto to the MySQL database
                databaseName: the name of the database which we'll connect to
            Returns:
                Nothing
        '''
        # Store the connection data
        self.__sqlUser = sqlUser
        self.__sqlPassword = sqlPassword
        self.__databaseName = databaseName
        # Connect to the database
        self.__db = self.connect()
        self.__cursor = self.__db.cursor()
        
    def connect(self):
        '''
            Connects to a MySQL database
            Args:
                None
            Returns:
                The database cursor used to send queries to the database.
        '''
        # Connect to MySQL
        db=MySQLdb.connect(host='localhost',user= self.__sqlUser,passwd= self.__sqlPassword)
        cursor=db.cursor()
        # Select the database to use
        sql = "USE "  + self.__databaseName   
        cursor.execute(sql)
        # Return the cursor
        return db
    
    def disconnect(self):
        '''
            Disconnects from a MySQL database
            Args:
                None
            Returns:
                Nothing
        '''
        # Close the connection
        self.__cursor.close()
        self.__db.close()
        
        
    def getVMServerStatus(self, serverId):
        '''
            Returns a virtual machine server's status
            Args:
                serverId: the virtual machine server's unique identifier
            Returns:
                A dictionary containing the server's status (at this moment, the
                number of active hosts)
        '''
        # Create the query
        query = "SELECT hosts FROM VMServerStatus WHERE serverId = " + str(serverId) + ";"
        # Execute it
        self.__cursor.execute(query)
        # Retrieve the results
        results=self.__cursor.fetchall()
        d = dict()
        d["ActiveHosts"] = int(results[0])
        return d
    
    def getVMServerIDs(self):
        '''
            Returns the virtual machine servers' IDs
            Args: 
                None
            Returns:
                A list containing all the virtual machine servers' IDs.
        '''
        # Create the query
        query = "SELECT serverId FROM VMServer;"  
        # Execute it
        self.__cursor.execute(query)
        # Retrieve the results
        results=self.__cursor.fetchall()
        serverIds = []
        for r in results:
            serverIds.append(r[0])
        # Return them
        return serverIds
        
    def registerVMServer(self, IPAddress, port):
        '''
            Registers a new virtual machine server in the database
            Args:
                None
            Returns:
                The new server's ID
        '''
        # Create the query
        query = "INSERT INTO VMServer(ip,portAdress,maxVM) VALUES(" + \
            SERVER_STATE_T.BOOTING + ", '" + IPAddress + "'," + port +");"  
        # Execute it
        self.__cursor.execute(query)               
        # Obtain the new server's ID
        query = "SELECT serverId FROM VMServer WHERE ip ='" + IPAddress + "');"  
        self.__cursor.execute(query) 
        serverId = self.__cursor.lastrowid
        # Update the database NOW
        self.__db.commit() 
        # Return the new server's ID
        return serverId
    
    def unregisterVMServer(self, serverId):
        '''
            Unregisters a virtual machine server.
            Args:
                serverId: the virtual machine server's unique ID
            Returns:
                Nothing
        '''
        # Delete the row
        query = "DELETE FROM VMServer WHERE serverId = " + str(serverId)
        self.__cursor.execute(query)
        # Write the changes to the database
        self.__db.commit() 
        # Note that the server registered images have already been erased (thanks
        # to the ON DELETE CASCADE SQL sentence)
        
    def getAvailableVMServers(self, imageId):
        '''
            Returns a list with the unique identifiers of all the virtual machine servers that can
            host an specific image.
            Args:
                imageId: the image's unique identifier
            Returns:
                A list containing the image's ID
        '''
        # Create the query 
        query = "SELECT serverId FROM ServerImages " +\
            "INNER JOIN VMServer ON ServerImages.serverId = VMServer.serverID" \
                + "WHERE VMServer.serverStatus = " + str(SERVER_STATE_T.READY) \
                + " AND " + "imageId =" + str(imageId) + ";"
        # Run it
        self.__cursor.execute(query)
        # Retrieve the results
        results=self.__cursor.fetchall()
        serverIds = []
        for r in results:
            serverIds.append(r[0])
        return serverIds
    
    def updateVMServerStatus(self, serverId, newStatus):
        '''
            Updates a virtual machine server's status
            Args:
                serverId: the virtual machine server's unique identifier
                newStatus: the new virtual machine server's status
            Returns:
                Nothing
        '''
        query = "UPDATE VMServer SET serverStatus=" + str(newStatus) + \
            " WHERE serverId = " + str(serverId) + ";"
        # Execute it
        self.__cursor.execute(query)
        # Write the changes to the database
        self.__db.commit()   