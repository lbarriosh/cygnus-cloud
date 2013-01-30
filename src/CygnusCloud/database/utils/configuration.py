# -*- coding: UTF8 -*-
'''
    In this module, we define the database configurator class. Its instances
    can configure a MySQL database.
    @author: Adrián Fernández Hernández
    @author: Luis Barrios Hernández
    @version: 2.0
'''
import MySQLdb

from os import path

class DBConfigurator(object):

    def __init__(self, rootPassword):
        '''
            Initializes the configurator's state
            Args: 
                rootPassword: root's password
        '''
        self.__rootPassword = rootPassword
        
    def addUser(self, user, password, databaseName, allPrivileges=True):
        '''
            Adds a new MySQL user
            Args:
                user: the new user's name
                password: the new user's password
                databaseName: the database's name
                allPrivileges: if True, the new user will be able to do everything
                with the database. If False, the new user will only be able to execute queries
                in the database.
            Returns:
                Nothing
        '''
        conn = MySQLdb.Connection(host="localhost", user="root", passwd=self.__rootPassword)
        cursor = conn.cursor()
        if (allPrivileges):
            privileges = "ALL"
        else :
            privileges = "SELECT"            
        cursor.execute("GRANT " + privileges + " ON " + databaseName + ".* TO '" +  user + "'@'" + "localhost" + "' IDENTIFIED BY '" + password + "';")
        cursor.close()
        conn.close()  
        
    def createDatabase(self, databaseName):
        '''
        Creates a MySQL database
        '''   
        db = MySQLdb.connect(host='localhost',user="root",passwd=self.__rootPassword)
        command = "CREATE DATABASE " + databaseName + ";"
        cursor = db.cursor()
        cursor.execute(command)
        cursor.close()
        db.close()
        
    def dropDatabase(self, databaseName):
        db = MySQLdb.connect(host='localhost',user="root",passwd=self.__rootPassword)
        command = "DROP DATABASE " + databaseName + ";"
        cursor = db.cursor()
        cursor.execute(command)
        cursor.close()
        db.close()
        
    def runSQLScript(self, database, sqlFilePath, username="root", password=None):
        '''
            Runs a SQL script
            Args:
                databaseName: the MySQL database to use
                sqlFilePath: the SQL script path
                username: a MySQL user name.
                password: the user's password
        '''
        if (username == "root") :
            db = MySQLdb.connect(host='localhost',user="root",passwd=self.__rootPassword)
        else: 
            db = MySQLdb.connect(host='localhost',user=username,passwd=password)    
        cursor=db.cursor()
        
        command = "CREATE DATABASE IF NOT EXISTS " + database + ";"
        cursor.execute(command)
        command = "USE " + database + ";"
        cursor.execute(command)
        command = ""
        
        fp = open(sqlFilePath)
        for line in fp:
                if line.endswith(';\n'):
                    command += line
                    cursor.execute(command)
                    command = ""
                else:
                    command += line          
        # Run the last command (if necessary)
        if (not DBConfigurator.__isEmpty__(command)) :
            cursor.execute(command)
        # Write the changes to the database
        db.commit() 
        # Close the database connection
        cursor.close()
        db.close()
        
    @staticmethod
    def __isEmpty__(str):
        for c in str :
            if (c != ' ' and c != '\n' and c != '\r' and c != 't') :
                return False
        return True