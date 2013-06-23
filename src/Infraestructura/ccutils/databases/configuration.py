# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: configuration.py    
    Version: 3.0
    Description: Database configurator definitions
    
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
import MySQLdb
import os.path
from ccutils.processes.childProcessManager import ChildProcessManager

class DBConfigurator(object):
    """
    This class provides methods to configure databases.
    """

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
        Args:
            databaseName: the new database's name
        Returns:
            Nothing
        '''   
        db = MySQLdb.connect(host='localhost',user="root",passwd=self.__rootPassword)
        command = "CREATE DATABASE " + databaseName + ";"
        cursor = db.cursor()
        cursor.execute(command)
        cursor.close()
        db.close()
        
    def dropDatabase(self, databaseName):
        '''
        Deletes a MySQL database
        Args:
            databaseName: the database to delete's name
        Returns:
            Nothing
        '''
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
        passwordCommand = ""
        if (password != None and len(password) != 0) :
            passwordCommand = "-p" + str(password)
        filePath = os.path.abspath(sqlFilePath)
        command = "mysql -uroot {0} -e \"source {1}\"".format(passwordCommand, filePath)
        ChildProcessManager.runCommandInForeground(command, Exception)
        
    @staticmethod
    def __isEmpty__(string):
        for c in string :
            if (c != ' ' and c != '\n' and c != '\r' and c != 't') :
                return False
        return True