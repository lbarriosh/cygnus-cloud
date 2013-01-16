# -*- coding: UTF8 -*-
import MySQLdb

class UserAccess(object):
    '''
        Clase encargada de gestionar el logueo de un determinado usuario
    '''
    def __init__(self,sqlUser,sqlPassword,databaseName):
        self.__sqlUser = sqlUser
        self.__sqlPass = sqlPassword
        self.__databaseName = databaseName
        #Seleccionamos la base de datos que vamos a manejar
        # Nos conectamos a MySql 
        self.__db = self.connect()
        self.__cursor = self.__db.cursor()
        
    def connect(self):
        #Seleccionamos la base de datos que vamos a manejar
        # Nos conectamos a MySql 
        db=MySQLdb.connect(host='localhost',user= self.__sqlUser,passwd= self.__sqlPass)
        cursor=db.cursor()
        #Creamos la consulta encargada de extraer los datos
        sql = "USE " + self.__databaseName     
        #Ejecutamos el comando
        cursor.execute(sql)
        #devolvemos el cursor
        return db
    
    def disconnect(self):
        #cerramos las conexiones
        self.__cursor.close()
        self.__db.close()
                
    def login(self,name,password):
        '''
            Comprueba si el usuario se encuentra registrado en la base
                de datos con la contraseña definida
        '''
        
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT * FROM Users WHERE name ='" + name + "'" 
        
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        
        #Recogemos los resultado
        result=self.__cursor.fetchone()
        
        #Comprobamos si ha encontrado el usuario
        if(self.__cursor.rowcount == 1):
            #Extraemos la contraseña y comparamos
            p = result[2]
            if(p == password):
                #Si la contraseña coincide devolvemos el id
                return result[0]
            else:
                 #Si no coincide lanzamos una excepción
                 raise Exception("Incorrect password")
        else:
                #Si no se encuentra el usuario lanzamos una excepción
                raise Exception("User Not Found")
 
#Metodo de prueba           
def main():
    print("Gestor de Logueo de CygnusCloud:")
    #Preguntamos por el usuario
    print('Inserte el nombre de usuario:')
    user = raw_input()
    print('Inserte la contrasennia :')
    password = raw_input() 
    #Instanciamos la clase
    userAccess = UserAccess("CygnusCloud","cygnuscloud2012","DBWebServer")
    # llamamos al metodo de logueado
    id = userAccess.login(user, password)
    #Mostramos el identificador
    print("Usuario logueado con id: ")
    print(id)
    #Nos desconectamos
    userAccess.disconnect()
    

## Comandos a ejecutar de inicio
#TODO : Quitar despues de hacer pruebas
if __name__ == "__main__":
    main()              
            
