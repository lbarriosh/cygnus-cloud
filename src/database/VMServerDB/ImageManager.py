# -*- coding: UTF8 -*-
import MySQLdb

class ImageManager(object):
    '''
        Esta clase permite gestionar las diferentes características de las imágenes 
         accesibles en el servidor de máquinas virtuales actual.
    '''

    def __init__(self,sqlUser,sqlPass,databaseName):
        '''
            Constructora de la clase
        '''
        # Guardamos los atributos necesarios para la conexión
        self.__sqlUser = sqlUser
        self.__sqlPass = sqlPass
        self.__databaseName = databaseName
        #Seleccionamos la base de datos que vamos a manejar
        # Nos conectamos a MySql 
        self.__db = self.connect()
        self.__cursor = self.__db.cursor()
        
    def connect(self):
        # Nos conectamos a MySql 
        db=MySQLdb.connect(host='localhost',user= self.__sqlUser,passwd= self.__sqlPass)
        cursor=db.cursor()
        #Cambiamos a la base de datos correspondiente
        sql = "USE " + self.__databaseName    
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
        sql = "SELECT name FROM VirtualMachine WHERE VMId = " + str(imageId)   
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
        sql = "SELECT imagePath FROM VirtualMachine WHERE VMId = " + str(imageId)   
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Recogemos los resultado
        result=self.__cursor.fetchone()
        #Devolvemos el resultado
        return result[0]
    
    def getOsImagePath(self,imageId):
        '''
            Devuelve la ruta donde se encuentra físicamente la imagen del SO cuyo identificador 
             de imagen se pasa como argumento.
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT osImagePath FROM VirtualMachine WHERE VMId = " + str(imageId)   
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
        sql = "SELECT FileConfigPath FROM VirtualMachine WHERE VMId = " + str(imageId)   
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
        #Creamos la consulta encargada de realizar la actualización
        sql = "UPDATE VirtualMachine SET imagePath = '"  + path + "' WHERE VMId = " + str(imageId)
        #Ejecutamos el comando
        self.__cursor.execute(sql)        
        #Actualizamos la base de datos
        self.__db.commit() 
        
    def createImage(self,imageId,name,imagePath,osImagePath,FileConfigPath):
        '''
            Permite registrar en la base de datos una nueva imagen de máquina virtual. 
        '''
        #Introducimos los datos en la base de datos
        sql = "INSERT INTO VirtualMachine(VMId,name,imagePath,osImagePath,FileConfigPath) VALUES("  
        sql+=    str(imageId) + ",'" + name + "','" + imagePath  +"','" + osImagePath + "','"+ FileConfigPath +"') "  
        #Ejecutamos el comando
        self.__cursor.execute(sql)  
        #Actualizamos la base de datos
        self.__db.commit()              
        #Devolvemos el id
        return imageId
    
    def deleteImage(self,imageId):
        #borramos el la MV
        sql = "DELETE FROM VirtualMachine WHERE VMId =" + str(imageId) 
        #Ejecutamos el comando
        self.__cursor.execute(sql) 
        # Gracias al ON DELETE CASCADE debería borrarse sus referencias en
        #  el resto de las tablas
        #Actualizamos la base de datos
        self.__db.commit()
 
    def isImageExists(self,VMId):   
        '''
            Comprueba si una imagen existe
        '''
        #Contamos el número de MV con el id dado    
        sql = "SELECT COUNT(*) FROM VirtualMachine WHERE VMId =" + str(VMId)
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Recogemos los resultado
        result=self.__cursor.fetchone()
        # Si el resultado es 1, la MV existe
        return (result[0] == 1)   
    
def main():    
    #Instanciamos la clase
    imageM = ImageManager("CygnusCloud","cygnuscloud2012","DBVMServer")
    #Comenzamos con las pruebas
    other = 's'
    while(other == 's'):
        print("Escoja un numero de prueba (1-6)")
        prueba = raw_input()
        
        if(prueba == '1'):
            # lista de imagenes registradas
            print("Prueba 1")
            imagesIds = imageM.getImages()
            print("Imagenes registradas")
            for i in imagesIds:
                print(i)
        elif(prueba == '2'):
            print("Prueba 2")
            # Nombre asociado a una imagen
            print("Indique el id de la imagen:")
            imageId = raw_input()
            #Obtenemos el nombre
            imageDName = imageM.getName(imageId)
            print("el nombre asociado a esta imagen es:")
            print(imageDName)
        elif(prueba == '3'):
            print("Prueba 3")
            #Descripcion asociada a una imagen
            print("Indique el id de la imagen:")
            imageId = raw_input()
            #Obtenemos el nombre
            imagePath = imageM.getImagePath(imageId)
            print("La ruta asociada a esta imagen es:")
            print(imagePath) 
        elif(prueba == '4'):
            print("Prueba 4")
            #Fichero de configuración asociado a una imagen
            print("Indique el id de la imagen:")
            imageId = raw_input()
            #Obtenemos el nombre
            imageConfigPath = imageM.getFileConfigPath(imageId)
            print("El fichero de configuracion asociado a esta imagen es:")
            print(imageConfigPath)
        elif(prueba == '5'):
            print("Prueba 5")
            #Actualización de la ruta de una imagen
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
            # Actualización de la ruta del fichero de configuración
            print("Indique el id de la imagen:")
            imageId = raw_input()
            print("Indique el nombre de la nueva imagen:")
            imageName = raw_input()
            print("Indique la nueva ruta de la nueva imagen:")
            imagePath = raw_input()
            print("Indique la nueva ruta del SO:")
            osImagePath = raw_input()
            print("Indique la nueva ruta del fichero de configuracion de la nueva imagen:")
            imageConfigPath = raw_input()
            #Creamos la imagen
            imageIds = imageM.createImage(imageId,imageName,imagePath,osImagePath,imageConfigPath)
            print("La imagen ha sido creada con el id:")
            print(imageIds)
        elif(prueba == '7'):
            print("Prueba 7")
            #Descripcion asociada a una imagen
            print("Indique el id de la imagen:")
            imageId = raw_input()
            #Obtenemos el nombre
            osImagePath = imageM.getOsImagePath(imageId)
            print("La ruta del SO asociada a esta imagen es:")
            print(osImagePath) 
            

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