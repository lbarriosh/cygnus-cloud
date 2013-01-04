# -*- coding: UTF8 -*-
import MySQLdb

class UserAccess(object):
    '''
    Clase encargada de gestionar el logueo de un determinado usuario
    '''
    def __init__(self,sqlUser,sqlPassword):
        self.sqlUser = sqlUser
        self.sqlPass = sqlPassword
        
    def login(self,name,password):
        '''
            Esta función comprueba si el usuario se encuentra registrado en la base
                de datos con la contraseña definida
        '''
        # Nos conectamos a MySql 
        db=MySQLdb.connect(host='localhost',user= self.sqlUser,passwd= self.sqlPass)
        cursor=db.cursor()
        #Creamos la consulta encargada de extraer los datos
        sql = "USE DBWebServer " 
        
        #Ejecutamos el comando
        cursor.execute(sql)
        
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT * FROM Users WHERE name ='" + name + "'" 
        
        #Ejecutamos el comando
        cursor.execute(sql)
        
        #Recogemos los resultado
        resultado=cursor.fetchone()
        
        #Comprobamos si ha encontrado el usuario
        if(cursor.rowcount == 1):
            #Extraemos la contraseña y comparamos
            p = resultado[2]
            if(p == password):
                #Si la contraseña coincide devolvemos el id
                return resultado[0]
            else:
                 raise Exception("Incorrect password")
        else:
                raise Exception("User Not Found")
        
        cursor.close()
        db.close()
 
#Metodo de prueba           
def main():
    print("Gestor de Logueo de CygnusCloud:")
    #Preguntamos por el usuario
    print('Inserte el nombre de usuario:')
    user = raw_input()
    print('Inserte la contrasennia :')
    password = raw_input() 
    #Instanciamos la clase
    userAccess = UserAccess("CygnusCloud","cygnuscloud2012")
    # llamamos al metodo de logueado
    id = userAccess.login(user, password)
    #Mostramos el identificador
    print("Usuario logueado con id: ")
    print(id)
    

## Comandos a ejecutar de inicio
#TODO : Quitar despues de hacer pruebas
if __name__ == "__main__":
    main()              
            
