# -*- coding: UTF8 -*-

'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: connector.py    
    Version: 2.5
    Description: Basic database connector definitions
    
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
import mysql.connector
from threading import Lock

class BasicDBConnector(object):
    '''
    This is the base class for all the database connectors.
    '''
    def __init__(self, sqlUser, sqlPassword, databaseName):
        '''
            Initializes the connector's state
            Args:
                sqlUser: the MySQL user to use
                sqlPassword: the MySQL password to use
                databaseName: a MySQL database name.
            Returns:
                Nothing
        '''
        self.__sqlUser = sqlUser
        self.__sqlPassword = sqlPassword
        self.__databaseName = databaseName
        self.__lock = Lock()
        # Nota: no nos conectamos a MySQL aquí: el código cliente llama a connect.
        
    def _executeUpdate(self, command):
        '''
        Performs an update over the MySQL database.
        Args:
            command: the command to run
        Returns:
            Nothing
        '''       
        with self.__lock :
            self.__dbConnection = mysql.connector.connect(user=self.__sqlUser, password=self.__sqlPassword,
                              host='127.0.0.1', database=self.__databaseName)
            cursor = self.__dbConnection.cursor()
            cursor.execute(command, ())    
            self.__dbConnection.commit()
            cursor.close()
            self.__dbConnection.close()
        
    def _executeQuery(self, command, pickOneResult=False):
        '''
        Runs a MySQL query
        Args:
            command:  the query to run
            pickOneResult: if True, only one result will be returned. If False,
            a list of results will be returned.
        Returns:
            the result(s) associated with the query.
        '''
        with self.__lock :
            self.__dbConnection = mysql.connector.connect(user=self.__sqlUser, password=self.__sqlPassword,
                              host='127.0.0.1', database=self.__databaseName)
            cursor = self.__dbConnection.cursor()
            cursor.execute(command, ())
            result = []
            for row in cursor :
                if (len(row) == 1) :
                    result.append(row[0])     
                else :
                    result.append(row)               
            cursor.close()
            if (result == []) :
                return None
            if (pickOneResult):
                return result[0]
            else:
                return result
            self.__dbConnection.close()