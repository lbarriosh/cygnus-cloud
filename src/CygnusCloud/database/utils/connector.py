# -*- coding: UTF8 -*-

'''
Conector básico con una base de datos
@author: Luis Barrios Hernández
@author: Adrián Fernández Hernández
@version: 1.0
'''
import MySQLdb

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
        # Guardamos los datos de conexión necesarios
        self.__sqlUser = sqlUser
        self.__sqlPassword = sqlPassword
        self.__databaseName = databaseName
        # Nota: no nos conectamos a MySQL aquí: el código cliente llama a connect.
    
        
    def connect(self):
        '''
            Realiza la conexión con la base de datos
            Argumentos:
                Ninguno
            Devuelve:
                Nada
        '''
        self.__db = MySQLdb.connect(host='localhost', user=self.__sqlUser, passwd=self.__sqlPassword)
        self.__cursor = self.__db.cursor()
        # Cambiamos a la base de datos correspondeinte
        sql = "USE " + self.__databaseName   
        self.__cursor.execute(sql)        
        # No hace falta devolver el cursor: ya lo tenemos guardado y listo para usar
        
    
    def disconnect(self):
        '''
            Realiza la desconexión de una base de datos
            Argumentos:
                Ninguno
            Devuelve:
                Nada
        '''
        # cerramos las conexiones
        self.__db.commit()
        self.__cursor.close()
        self.__db.close()
        
    def executeUpdate(self, command):
        '''
        Ejecuta una actualización sobre la base de datos
        Argumentos:
            command: string con los comandos SQL a ejecutar
        Devuelve:
            Nada
        '''
        # Ejecutar la actualización
        self.__cursor.execute(command)
         
    def writeChangesToDatabase(self):
        '''
        Fuerza la escritura de los cambios realizados a la base de datos
        '''
        self.__db.commit() 
        
    def executeQuery(self, command, pickOneResult=False):
        '''
        Ejecuta una consulta en la base de datos.
        Argumentos:
            command: string con la consulta SQL
            pickOneResult: si es True, se devolverá un resultado. Si es False,
            se devolverán todos.
        Devuelve:
            resultado o resultados obtenidos a partir de la consulta
        '''
        self.__cursor.execute(command)
        # Recogemos los resultado
        if (pickOneResult) :
            return self.__cursor.fetchone()
        else :
            return self.__cursor.fetchall()
        
    def getLastRowId(self, command):
        '''
        Ejecuta una consulta en la base de datos, devolviendo el ID de la ultima fila
        Argumentos:
            command: string con la consulta SQL
        Devuelve:
            ID de la última fila devuelta por la consulta
        '''
        self.__cursor.execute(command)
        return self.__cursor.lastrowid
