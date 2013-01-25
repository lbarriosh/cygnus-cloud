# -*- coding: UTF8 -*-
import MySQLdb

from utils.enums import enum

SERVER_STATE_T = enum("BOOTING", "READY", "SHUT_DOWN")

class MainServerDatabaseConnector(object):
    '''
        These objects register and delete virtual machine servers to the database.   
    '''

    def __init__(self, sqlUser, sqlPassword, databaseName):
        '''
            Initializes the manager's state
            Args:
                sqlUser: the user to use to connect to a MySQL database
                sqlPassword: the password to use to connect to the MySQL database
                databaseName: the name of the database which we'll connect to
            Returns:
                Nothing
        '''
        # Store the connection data
        self.__sqlUser = sqlUser
        self.__sqlPassword = sqlPassword
        self.__databaseName = databaseName
        
    def connect(self):
        '''
            Connects to a MySQL database
            Args:
                None
            Returns:
                Nothing
        '''
        # Connect to MySQL
        db=MySQLdb.connect(host='localhost',user= self.__sqlUser,passwd= self.__sqlPassword)
        cursor=db.cursor()
        # Select the database to use
        sql = "USE "  + self.__databaseName   
        cursor.execute(sql)        
        # Connect to the database
        self.__db = db
        self.__cursor = db.cursor()
    
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
        
    def getVMServerBasicData(self, serverId):
        '''
            Returns the data associated to a virtual machine server
            Args:
                serverId: the virtual machine server's unique identifier
            Returns:
                A dictionary with the server's data.
        '''
        # Create the query
        query = "SELECT serverName, serverStatus, serverIP, serverPort FROM VMServer"\
            + " WHERE serverId = " + str(serverId) + ";"
        # Execute it
        self.__cursor.execute(query)
        # Retrieve the results
        results=self.__cursor.fetchall()
        d = dict()
        (name, status, ip, port) = results[0]
        d["ServerName"] = name
        d["ServerStatus"] = status
        d["ServerIP"] = ip
        d["ServerPort"] = port
        return d        
        
    def getVMServerStatistics(self, serverId):
        '''
            Returns a virtual machine server's statistics
            Args:
                serverId: the virtual machine server's unique identifier
            Returns:
                A dictionary containing the server's statistics (right now, just the
                number of active hosts)
        '''
        # Create the query
        query = "SELECT hosts FROM VMServerStatus WHERE serverId = " + str(serverId) + ";"
        # Execute it
        self.__cursor.execute(query)
        # Retrieve the results
        results=self.__cursor.fetchall()
        d = dict()
        if (results != tuple()) :
            activeHosts = results[0][0]
            d["ActiveHosts"] = activeHosts
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
        
    def registerVMServer(self, name, IPAddress, port):
        '''
            Registers a new virtual machine server in the database
            Args:
                name: the new server's name
                IPAddress: the new server's IP address
                port: the new server's port
            Returns:
                The new server's ID
        '''
        # Create the query
        query = "INSERT INTO VMServer(serverStatus, serverName, serverIP, serverPort) VALUES (" + \
            str(SERVER_STATE_T.BOOTING) + ", '" + name + "', '" + IPAddress + "'," + str(port) +");"
        # Execute it
        self.__cursor.execute(query)               
        # Obtain the new server's ID
        query = "SELECT serverId FROM VMServer WHERE serverIP ='" + IPAddress + "';"
        self.__cursor.execute(query) 
        serverId = self.__cursor.lastrowid
        # Update the database NOW
        self.__db.commit() 
        # Return the new server's ID
        return serverId
    
    def unregisterVMServer(self, serverNameOrIPAddress):
        '''
            Unregisters a virtual machine server.
            Args:
                serverId: the virtual machine server's unique ID
            Returns:
                Nothing
        '''
        serverId = self.getVMServerID(serverNameOrIPAddress)
        # Delete the row
        query = "DELETE FROM VMServer WHERE serverId = " + str(serverId) + ";"
        self.__cursor.execute(query)
        # Workaround. ON DELETE CASCADE does not work when different storage engines are used
        # with the tables.
        query = "DELETE From VMServerStatus WHERE serverId = " + str(serverId) + ";"
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
        query = "SELECT ImageOnServer.serverId FROM ImageOnServer " +\
            "INNER JOIN VMServer ON ImageOnServer.serverId = VMServer.serverID " \
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
    
    def getVMServerID(self, nameOrIPAddress):
        query = "SELECT serverId FROM VMServer WHERE serverIP = '" + nameOrIPAddress +\
             "' OR serverName = '" + nameOrIPAddress + "';"
        # Execute it
        self.__cursor.execute(query)
        results=self.__cursor.fetchall()
        return results[0][0]
    
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
        
    def getImages(self, serverId):
        '''
            Returns a list with the identifiers of the images that a virtual
            machine server contains.
            Args:
                serverId: the virtual machine server's unique ID
            Returns:
                A list containing all the image identifiers.
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT imageId FROM ImageOnServer WHERE serverId = " + str(serverId)    
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Recogemos los resultado
        results=self.__cursor.fetchall()
        #Guardamos en una lista los ids resultantes
        serverIds = []
        for r in results:
            serverIds.append(r[0])
        #Devolvemos la lista resultado
        return serverIds
    
    def getImageData(self, imageId):
        '''
        Returns all the data associated to an image.
        Args:
            imageId: the image's unique identifier
        Returns:
            A dictionary with the image name and description
        '''
        # Create the query
        query = "SELECT name, Description FROM Image WHERE imageId = " + str(imageId)   
        # Execute it
        self.__cursor.execute(query)
        # Fetch its output
        result=self.__cursor.fetchone()
        d = dict()
        d["ImageName"] = result[0]
        d["ImageDescription"] = result[1]
        return d
        
    def createNewImage(self, name, description):
        '''
            Creates a new image in the database
            Args:
                name: the new image's name
                description: the new image's description
            Returns:
                Nothing
        '''
        # Insert the row in the table
        query = "INSERT INTO Image(name,description) VALUES('" + name + "','" + description  +"') "  
        self.__cursor.execute(query)               
        # Obtain the new image's unique identifier
        query = "SELECT imageId FROM Image WHERE name ='" + name + "' AND description ='" + description +"'"  
        self.__cursor.execute(query) 
        imageId = self.__cursor.lastrowid
        # Write the changes to the database NOW
        self.__db.commit() 
        # Return the new image's id
        return imageId
    
    def assignImageToServer(self, serverID, imageID):
        '''
        Assigns an image to a virtual machine server. This means that the server can instantiate it.
        Args:
            serverID: the server's unique identifier
            imageID: the image's unique identifiers
        Returns: Nothing
        '''
        # Insert the row in the table
        query = "INSERT INTO ImageOnServer VALUES(" + str(serverID)+ "," + str(imageID)  +") "  
        self.__cursor.execute(query)               
        # Write the changes to the database NOW
        self.__db.commit() 
        
    def setImageData(self, imageId, imageName, imageDescription):
        '''
        Modifies an image's data
        Args:
            imageId: the image's unique identifier
            imageName: the image's new name
            imageDescription: the image's new description
        Returns:
            Nothing
        '''
        # Create the query
        query = "UPDATE Image SET name = '"  + imageName + "', description = '" + imageDescription +\
            "' WHERE imageId = " + str(imageId) + ";"
        # Execute it
        self.__cursor.execute(query)
        # Write the changes to the database NOW
        self.__db.commit() 
        
    def setVMServerStatistics(self, serverID, runningHosts):
        query = "INSERT INTO VMServerStatus VALUES(" + str(serverID) + ", " + str(runningHosts) + ");"
        try :
            self.__cursor.execute(query)
        except Exception :
            query = "UPDATE VMServerStatus SET hosts = " + str(runningHosts) + " WHERE serverId = "\
                + str(serverID) + ";"
            self.__cursor.execute(query)
        # Update the database NOW
        self.__db.commit() 
        
    def setServerBasicData(self, serverId, name, status, IPAddress, port):
        '''
            Modifies a virtual machine server's basic data
            Args:
                name: the new server's name
                status: the new server's status
                IPAddress: the new server's IP address
                port: the new server's port
            Returns:
                Nothing
        '''
        # Create the query
        query = "UPDATE VMServer SET serverName = '" + name + "', serverIP = '" + IPAddress + "', "+\
            "serverPort = " + str(port) + ", serverStatus = " + str(status) +\
            " WHERE  serverId = " + str(serverId) + ";"
        # Execute it
        self.__cursor.execute(query)               
        # Update the database NOW
        self.__db.commit() 