# -*- coding: UTF8 -*-
'''
    Clase encargada de cargar un determinado script de inicializacion de 
     base de datos creando un determinado usuario de mySQL
'''
import MySQLdb

class DBUtils:

    def __init__(self,filePath):
        '''
        Constructora de la clase. Recibe la ruta del script
        a cargar
        '''
        self.initFilePath = filePath;
        
    def initMySqlUser(self,user,password):
        '''
            Funcion encargada de crear un nuevo usuario en mySQl
        '''
        #Nos conectamos como root para crear el usuario
        conn = MySQLdb.Connection(host="localhost", user="root", passwd="170590ucm")
        cursor = conn.cursor()
        #cursor.execute("CREATE USER IF NOT EXISTS %s@%s IDENTIFIED BY %s", (user, "localhost", password))     
        cursor.execute("GRANT ALL ON *.* TO '" +  user + "'@'" + "localhost" + "' IDENTIFIED BY '" + password + "';")
        cursor.close()
        conn.close()
        
        
        
    def loadScript(self,user,password):
        '''
            Funcion encargada de lanzar el script
        '''
        # Nos conectamos a MySql 
        db=MySQLdb.connect(host='localhost',user= user,passwd= password)
        cursor=db.cursor()
        
        #Creamos la consulta encargada de cargar el script
        sql = "source " + self.initFilePath  
        
        #Ejecutamos el comando
        cursor.execute(sql)
        #Actualizamos la base de datos
        self.db.commit() 
        #Cerramos la conexión
        cursor.close()
        db.close()
        
       

def main():
    #Preguntamos por la ruta
    print('Inserte la ruta del script')
    path = raw_input()
    
    #Creamos la clase
    utils =  DBUtils(path)
    
    #Preguntamos por el usuario
    print('Inserte el nombre de usuario de MySql')
    user = raw_input()
    print('Inserte la contrasennia')
    password = raw_input()  

    #Creamos el usuario
   # utils.initMySqlUser(user, password)
    #Llamamos a la función encargada de cargar el script
    utils.loadScript(user, password)
    
    
## Comandos a ejecutar de inicio
if __name__ == "__main__":
    main()       