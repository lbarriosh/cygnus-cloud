# -*- coding: UTF8 -*-
import MySQLdb

class ImageManager(object):
    '''
        Esta clase permite gestionar las diferentes características de las imágenes 
         accesibles en el servidor de máquinas virtuales actual.
    '''

    def __init__(self,sqlUser,sqlPass):
        '''
            Constructora de la clase
        '''
        self.__sqlUser = sqlUser
        self.__sqlPass = sqlPass
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
        sql = "USE DBVMServer"     
        #Ejecutamos el comando
        cursor.execute(sql)
        #devolvemos el cursor
        return db
    
    def disconnect(self):
        #cerramos las conexiones
        self.__cursor.close()
        self.__db.close()

    def getImages(self):
        '''
             Devuelve una lista con todos los identificadores de imágenes que se 
              encuentran registradas en el servidor de máquinas virtuales.
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT VMId FROM VirtualMachine" 
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Recogemos los resultado
        results=self.__cursor.fetchall()
        #Guardamos en una lista los ids resultantes
        imageIds = []
        for r in results:
            imageIds.append(r[0])
        #Devolvemos la lista resultado
        return imageIds
    
    def getName(self,imageId):
        '''
            Devuelve el nombre de la imagen cuyo identificador se pasa como argumento. 
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT name FROM VirtualMachine WHERE VMId = " + imageId   
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Recogemos los resultado
        result=self.__cursor.fetchone()
        #Devolvemos el resultado
        return result[0]  
    
    def getImagePath(self,imageId):
        '''
            Devuelve la ruta donde se encuentra físicamente la imagen cuyo identificador 
             de imagen se pasa como argumento.
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT imagePath FROM VirtualMachine WHERE VMId = " + imageId   
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Recogemos los resultado
        result=self.__cursor.fetchone()
        #Devolvemos el resultado
        return result[0]
    
    def getFileConfigPath(self,imageId):
        '''
            Devuelve la ruta donde se encuentra el fichero de configuración asociado a 
             la imagen cuyo identificador se pasa como argumento
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT FileConfigPath FROM VirtualMachine WHERE VMId = " + imageId   
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Recogemos los resultado
        result=self.__cursor.fetchone()
        #Devolvemos el resultado
        return result[0]
    
    def setImagePath(self,imageId,path):
        '''
            Permite cambiar la ruta de la imagen cuyo identificador se pasa como argumento.
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "UPDATE VirtualMachine SET imagePath = '"  + path + "' WHERE VMId = " + imageId
        #Ejecutamos el comando
        self.__cursor.execute(sql) 
        
        #Actualizamos la base de datos
        self.__db.commit() 
        
    def createImage(self,name,imagePath,FileConfigPath):
        '''
            Permite registrar en la base de datos una nueva imagen de máquina virtual. 
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "INSERT INTO VirtualMachine(name,imagePath,FileConfigPath) VALUES('"  
        sql+=    name + "','" + imagePath  +"','" + FileConfigPath +"') "  
        #Ejecutamos el comando
        self.__cursor.execute(sql)               
        #Extraemos el id del servidor recien creado
        sql = "SELECT VMId FROM VirtualMachine WHERE name ='" + name + "' AND imagePath ='" + imagePath +"'" 
        sql += " AND FileConfigPath = '" + FileConfigPath + "'" 
        #Ejecutamos el comando
        self.__cursor.execute(sql) 
        #Cogemos el utlimo
        imageId = self.__cursor.lastrowid
        #Actualizamos la base de datos
        self.__db.commit() 
        #Lo devolvemos
        return imageId
    
    
def main():    
    #Instanciamos la clase
    imageM = ImageManager("CygnusCloud","cygnuscloud2012")
    #Comenzamos con las pruebas
    other = 's'
    while(other == 's'):
        print("Escoja un numero de prueba (1-6)")
        prueba = raw_input()
        
        if(prueba == '1'):
            print("Prueba 1")
            imagesIds = imageM.getImages()
            print("Imagenes registradas")
            for i in imagesIds:
                print(i)
        elif(prueba == '2'):
            print("Prueba 2")
            print("Indique el id de la imagen:")
            imageId = raw_input()
            #Obtenemos el nombre
            imageDName = imageM.getName(imageId)
            print("el nombre asociado a esta imagen es:")
            print(imageDName)
        elif(prueba == '3'):
            print("Prueba 3")
            print("Indique el id de la imagen:")
            imageId = raw_input()
            #Obtenemos el nombre
            imagePath = imageM.getImagePath(imageId)
            print("La ruta asociada a esta imagen es:")
            print(imagePath) 
        elif(prueba == '4'):
            print("Prueba 4")
            print("Indique el id de la imagen:")
            imageId = raw_input()
            #Obtenemos el nombre
            imageConfigPath = imageM.getFileConfigPath(imageId)
            print("El fichero de configuracion asociado a esta imagen es:")
            print(imageConfigPath)
        elif(prueba == '5'):
            print("Prueba 5")
            print("Indique el id de la imagen:")
            imageId = raw_input()
            print("Indique la nueva ruta de la imagen:")
            imagePath = raw_input()
            #Cambiamos la ruta
            imageM.setImagePath(imageId,imagePath)
            print("La nueva ruta será:")
            print(imageM.getImagePath(imageId))
        elif(prueba == '6'):
            print("Prueba 6")
            print("Indique el nombre de la nueva imagen:")
            imageName = raw_input()
            print("Indique la nueva ruta de la nueva imagen:")
            imagePath = raw_input()
            print("Indique la nueva ruta del fichero de configuracion de la nueva imagen:")
            imageConfigPath = raw_input()
            #Creamos la imagen
            imageId = imageM.createImage(imageName,imagePath,imageConfigPath)
            print("La imagen ha sido creada con el id:")
            print(imageId)
        else:
            print("Prueba no disponible.")
               
        #Comprobamos si se quiere hacer otra prueba
        print("Desea hacer otra prueba?(s/n)")
        other = raw_input() 
         
    #Nos desconectamos
    imageM.disconnect()

## Comandos a ejecutar de inicio (solo en caso de pruebas)
if __name__ == "__main__":
    main() 