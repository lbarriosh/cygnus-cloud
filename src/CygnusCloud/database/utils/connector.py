# -*- coding: UTF8 -*-

'''
Conector básico con una base de datos
@author: Luis Barrios Hernández
@author: Adrián Fernández Hernández
@version: 3.0
'''
import mysql.connector
from threading import Lock

class BasicDatabaseConnector(object):
    '''
    Conector básico con una base de datos
    '''
    def __init__(self, sqlUser, sqlPassword, databaseName):
        '''
            Constructor de la clase. Recibe el nombre y lla contrasennia del usuario sql encargado
            de gestionar la base de datos
            Argumentos:
                sqlUser: usuario para conectarnos a MySQL
                sqlPassword: contraseña para conectarnos a MySQL
                databaseName: nombre de la base de datos a la que nos vamos a conectar
            Devuelve:
                Nada
        '''
        self.__sqlUser = sqlUser
        self.__sqlPassword = sqlPassword
        self.__databaseName = databaseName
        self.__lock = Lock()
        # Nota: no nos conectamos a MySQL aquí: el código cliente llama a connect.    
        
    def connect(self):
        '''
            Realiza la conexión con la base de datos
            Argumentos:
                Ninguno
            Devuelve:
                Nada
        '''
        with self.__lock:
            self.__dbConnection = mysql.connector.connect(user=self.__sqlUser, password=self.__sqlPassword,
                              host='127.0.0.1', database=self.__databaseName)
            
    
    def disconnect(self):
        '''
            Realiza la desconexión de una base de datos
            Argumentos:
                Ninguno
            Devuelve:
                Nada
        '''       
        with self.__lock :
            self.__dbConnection.close()
        
    def _executeUpdate(self, command):
        '''
        Ejecuta una actualización sobre la base de datos
        Argumentos:
            command: string con los comandos SQL a ejecutar
        Devuelve:
            Nada
        '''       
        with self.__lock :
            cursor = self.__dbConnection.cursor()
            cursor.execute(command, ())    
            self.__dbConnection.commit()
            cursor.close()
        
    def _executeQuery(self, command, pickOneResult=False):
        '''
        Ejecuta una consulta en la base de datos.
        Argumentos:
            command: string con la consulta SQL
            pickOneResult: si es True, se devolverá un resultado. Si es False,
            se devolverán todos.
        Devuelve:
            resultado o resultados obtenidos a partir de la consulta
        '''
        with self.__lock :
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