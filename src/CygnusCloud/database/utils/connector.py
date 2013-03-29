# -*- coding: UTF8 -*-

'''
Conector básico con una base de datos
@author: Luis Barrios Hernández
@author: Adrián Fernández Hernández
@version: 3.0
'''
import MySQLdb
from threading import BoundedSemaphore

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
        self.__semaphore = BoundedSemaphore(1)
        # Nota: no nos conectamos a MySQL aquí: el código cliente llama a connect.    
        
    def connect(self):
        '''
            Realiza la conexión con la base de datos
            Argumentos:
                Ninguno
            Devuelve:
                Nada
        '''
        with self.__semaphore :
            self.__dbConnection = MySQLdb.connect(host='localhost', user=self.__sqlUser, passwd=self.__sqlPassword)
            cursor = self.__dbConnection.cursor()
            sql = "USE " + self.__databaseName   
            cursor.execute(sql) 
            cursor.close()               
    
    def disconnect(self):
        '''
            Realiza la desconexión de una base de datos
            Argumentos:
                Ninguno
            Devuelve:
                Nada
        '''       
        with self.__semaphore :
            self.__dbConnection.commit()
            self.__dbConnection.close()
        
    def _executeUpdate(self, command):
        '''
        Ejecuta una actualización sobre la base de datos
        Argumentos:
            command: string con los comandos SQL a ejecutar
        Devuelve:
            Nada
        '''       
        with self.__semaphore :
            cursor = self.__dbConnection.cursor()
            cursor.execute(command)       
            cursor.close()
            self.__dbConnection.commit()
         
#    def _writeChangesToDatabase(self):
#        '''
#        Fuerza la escritura de los cambios realizados a la base de datos
#        '''
#        self.__dbConnection.commit() 
        
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
        with self.__semaphore :
            cursor = self.__dbConnection.cursor()
            cursor.execute(command)        
            if (pickOneResult) :
                result =  cursor.fetchone()
            else :
                result = cursor.fetchall()
            cursor.close()
            return result
        
    def getLastRowId(self, command):
        '''
        Ejecuta una consulta en la base de datos, devolviendo el ID de la ultima fila
        Argumentos:
            command: string con la consulta SQL
        Devuelve:
            ID de la última fila devuelta por la consulta
        '''
        with self.__semaphore :
            cursor = self.__dbConnection.cursor()
            cursor.execute(command)
            result = cursor.lastrowid         
            cursor.close()
            return result