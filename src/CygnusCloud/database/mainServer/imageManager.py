# -*- coding: UTF8 -*-
'''
This module contains the ImageManager, a class that registers images
in the main server's database and associates them to a virtual
machine server.
@author: Adrián Fernández Hernández
@author: Luis Barrios Hernández
@version: 2.0
'''
import MySQLdb


class ImageManager(object):
    '''
       These objects connect to a database and handle all the image-centered queries.
    '''

    def __init__(self, sqlUser, sqlPassword, databaseName):
        '''
            Initializes the ImageManager's state
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
        sql = "USE " + self.__databaseName  
        cursor.execute(sql)
        # Return the database cursor
        return db
    
    def disconnect(self):
        '''
            Disconnects from a MySQL database
            Args:
                None
            Returns:
                Nothing
        '''
        # Close the connections
        self.__cursor.close()
        self.__db.close()
        
    def getServerImages(self, serverId):
        '''
            Returns a list with the identifiers of the images that a virtual
            machine server contains.
            Args:
                serverId: the virtual machine server's unique ID
            Returns:
                A list containing all the image identifiers.
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT imageId FROM ServerImages WHERE serverId = " + str(serverId)    
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
            A tuple (name, description), where name is the image's name
            and description is its description
        '''
        # Create the query
        query = "SELECT name, Description FROM Image WHERE imageId = " + str(imageId)   
        # Execute it
        self.__cursor.execute(query)
        # Fetch its output
        result=self.__cursor.fetchone()
        return (result[0], result[1])
        
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
        query = "INSERT INTO ServerImages VALUES(" + str(serverID)+ "," + str(imageID)  +") "  
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
        query = "UPDATE Image SET description = '"  + imageDescription + "SET name = " + imageName + "' WHERE imageId = " + str(imageId)
        # Execute it
        self.__cursor.execute(query)
        # Write the changes to the database NOW
        self.__db.commit() 