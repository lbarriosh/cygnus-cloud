# -*- coding: UTF8 -*-
import MySQLdb


class ImageServerManager(object):
    '''
        Esta clase permite configurar que imágenes de máquinas virtuales pueden utilizarse en 
         cada uno de los servidores.
    '''


    def __init__(self,sqlUser,sqlPass,serverId,databaseName):
        '''
            Constructora de la clase
        '''
        self.__sqlUser = sqlUser
        self.__sqlPass = sqlPass
        self.__serverId = serverId
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
        
    def getServerImages(self):
        '''
             Devuelve una lista con los identificadores de las imágenes asociadas al servidor 
              de máquinas virtuales del atributo
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT imageId FROM ServerImages WHERE serverId = " + str(self.__serverId)    
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Recogemos los resultado
        results=self.__cursor.fetchall()
        #Guardamos en una lista los ids resultantes
        serverIds = []
        for r in results:
            serverIds.append(r[0])
        #Devolvemos la lista resultado
        return serverIds
    
    def getImageName(self,imageId):
        '''
            Devuelve el nombre asociado a una determinada imagen cuyo identificador
             se le pasa como argumento.
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT name FROM Image WHERE imageId = " + str(imageId)   
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Recogemos los resultado
        result=self.__cursor.fetchone()
        #Devolvemos el resultado
        return result[0]        
    
    def getImageDescription(self,imageId):
        '''
            Devuelve la descripción de una determinada imagen cuyo identificador se le 
            pasa como argumento.
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT description FROM Image WHERE imageId = " + str(imageId)   
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Recogemos los resultado
        result=self.__cursor.fetchone()
        #Devolvemos el resultado
        return result[0] 
    
    def createNewImage(self,name,description):
        '''
            Permite dar de alta en la base de datos una nueva imagen asociada 
             al servidor de máquinas virtuales definido como atributo.
        '''
         #Creamos la consulta encargada de extraer los datos
        sql = "INSERT INTO Image(name,description) VALUES('" + name + "','" + description  +"') "  
        #Ejecutamos el comando
        self.__cursor.execute(sql)               
        #Extraemos el id del servidor recien creado
        sql = "SELECT imageId FROM Image WHERE name ='" + name + "' AND description ='" + description +"'"  
        #Ejecutamos el comando
        self.__cursor.execute(sql) 
        #Cogemos el utlimo
        imageId = self.__cursor.lastrowid
        #Actualizamos la base de datos
        self.__db.commit() 
        #Lo devolvemos
        return imageId
    
    def isImageExists(self,imageId):   
        '''
            Comprueba si una imagen existe
        '''
        #Comprobamos que el usuario sea un administrador     
        sql = "SELECT COUNT(*) FROM Image WHERE imageId =" + str(imageId)
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Recogemos los resultado
        result=self.__cursor.fetchone()
        return (result[0] == 1)
    
    def setDescription(self,imageId,description):
        '''
            Permite editar la descripción asociada a una determinada imagen cuyo identificador 
             se le pasa como argumento.
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "UPDATE Image SET description = '"  + description + "' WHERE imageId = " + str(imageId)
        #Ejecutamos el comando
        self.__cursor.execute(sql) 
        
        #Actualizamos la base de datos
        self.__db.commit() 
        
def main():
    #Preguntamos por el id del servidor
    print("Indique el id del servidor:")
    serverId = raw_input()
    #Instanciamos la clase
    imageSM = ImageServerManager("CygnusCloud","cygnuscloud2012",serverId,"DBMainServer")
    #Comenzamos con las pruebas
    other = 's'
    while(other == 's'):
        print("Escoja un numero de prueba (1-5)")
        prueba = raw_input()
        
        if(prueba == '1'):
            print("Prueba 1")
            #Obtenemos las imagenes asociadas a este servidor
            imagesIds = imageSM.getServerImages()
            print("Las imagenes asociadas a este servidor son:")
            for i in imagesIds:
                print(i)
        elif(prueba == '2'):
            print("Prueba 2")
            print("Indique el id de la imagen:")
            imageId = raw_input()          
            #Obtenemos las imagenes asociadas a este servidor
            imageName = imageSM.getImageName(imageId)
            print("El nombre asociado a esta imagen es:")
            print(imageName)
        elif(prueba == '3'):
            print("Prueba 3")
            print("Indique el id de la imagen:")
            imageId = raw_input()          
            #Obtenemos las imagenes asociadas a este servidor
            imageDesc = imageSM.getImageDescription(imageId)
            print("la descripcion asociada a esta imagen es:")
            print(imageDesc)
        elif(prueba == '4'):
            print("Prueba 4")
            print("Indique el nombre de la nueva imagen:")
            imageName = raw_input()
            print("Indique la descripcion de la nueva imagen:")
            imageDesc = raw_input()          
            #Obtenemos las imagenes asociadas a este servidor
            imageId = imageSM.createNewImage(imageName,imageDesc)
            print("Imagen creada con identificador :")
            print(imageId)
        elif(prueba == '5'):
            print("Prueba 5")
            print("Indique el id de la  imagen:")
            imageId = raw_input()
            print("Indique la nueva descripcion:")
            imageDesc = raw_input()          
            #Obtenemos las imagenes asociadas a este servidor
            imageSM.setDescription(imageId,imageDesc)
            print("La descripcion ha sido modificada por:")
            print(imageSM.getImageDescription(imageId))
        else:
            print("Prueba no disponible.")
               
        #Comprobamos si se quiere hacer otra prueba
        print("Desea hacer otra prueba?(s/n)")
        other = raw_input() 
         
    #Nos desconectamos
    imageSM.disconnect()

## Comandos a ejecutar de inicio (solo en caso de pruebas)
if __name__ == "__main__":
    main() 