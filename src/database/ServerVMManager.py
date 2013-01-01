# -*- coding: UTF8 -*-
import MySQLdb


class ServerVMManager(object):
    '''
        Clase encargada de dar de alta y de baja en la base de datos 
        nuevos servidores, indicando los detalles sobre la IP, el puerto y 
        el número máximo de máquinas virtuales que dicho servidor puede ejecutar al mismo tiempo.
    '''


    def __init__(self,sqlUser,sqlPass):
        '''
        Constructor de la clase. Recibe el nombre y lla contrasennia del usuario sql encargado
         de gestionar la base de datos
        '''
        self.sqlUser = sqlUser
        self.sqlPass = sqlPass
        #Seleccionamos la base de datos que vamos a manejar
        # Nos conectamos a MySql 
        self.db = self.connect()
        self.cursor = self.db.cursor()
        
    def connect(self):
        #Seleccionamos la base de datos que vamos a manejar
        # Nos conectamos a MySql 
        db=MySQLdb.connect(host='localhost',user= self.sqlUser,passwd= self.sqlPass)
        cursor=db.cursor()
        #Creamos la consulta encargada de extraer los datos
        sql = "USE DBMainServer"     
        #Ejecutamos el comando
        cursor.execute(sql)
        #devolvemos el cursor
        return db
    
    def disconnect(self):
        #cerramos las conexiones
        self.cursor.close()
        self.db.close()
        
    def showServers(self):
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT * FROM VMServer"     
        #Ejecutamos el comando
        self.cursor.execute(sql)
        #Recogemos los resultado
        results=self.cursor.fetchall()
        #Guardamos en una lista los ids resultantes
        for r in results:
            print(r)
        
    def getMaxVMNumber(self,serverId):
        '''
         Función que devuelve eldevuelve el número máximo de máquinas virtuales 
          que el servidor puede soportar
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT maxVM FROM VMServer WHERE serverId = " + serverId    
        #Ejecutamos el comando
        self.cursor.execute(sql)
        #Recogemos los resultado
        results=self.cursor.fetchone()
        #Devolvemos el resultado 
        return results[0] 
    
    def getFreeVMNumber(self,serverId):
        '''
            devuelve el número de máquinas virtuales libres que el servidor 
            pasado como argumento puede soportar todavía.
        '''
        #Obtenemos el numero de mv activas para este servidor
        sql = "SELECT count(*) FROM ServerImages WHERE serverId =" + serverId
                #Ejecutamos el comando
        self.cursor.execute(sql)
        #Recogemos los resultado
        running=self.cursor.fetchone()
        #Obtenemos el máximo núnmero mv para este servidor
        max = self.getMaxVMNumber(serverId)
        #Devolvemos la diferencia
        return (max - running[0]) 
    
    def getServers(self):
        '''
            permite obtener una lista con los identificadores de todos los servidores de 
             máquinas virtuales que actualmente se encuentran dados de alta en la base de datos.
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT serverId FROM VMServer "  
        #Ejecutamos el comando
        self.cursor.execute(sql)
        #Recogemos los resultado
        results=self.cursor.fetchall()
        #Guardamos en una lista los ids resultantes
        serverIds = []
        for r in results:
            serverIds.append(r[0])
        #Devolvemos la lista resultado
        return serverIds
    
    def setMaxVM(self,serverId,maxVM): 
        '''
            permite configurar el número de máquinas virtuales que admite como máximo el
             servidor de máquinas virtuales
        '''
         #Creamos la consulta encargada de extraer los datos
        sql = "UPDATE VMServer SET maxVM = "  + maxVM + " WHERE serverId = " + serverId
        #Ejecutamos el comando
        self.cursor.execute(sql) 
        
        #Actualizamos la base de datos
        self.db.commit()      
        
    def subscribeServer(self,port,IP,maxVM):
        '''
            permite registrar un Nuevo servidor de máquinas virtuales con el puerto, la IP y el número
             máximo de máquinas virtuales que se le pasan como argumento
        '''
         #Creamos la consulta encargada de extraer los datos
        sql = "INSERT INTO VMServer(ip,portAdress,maxVM) VALUES('" + IP + "','" + port +"'," + maxVM +") "  
        #Ejecutamos el comando
        self.cursor.execute(sql)               
        #Extraemos el id del servidor recien creado
        sql = "SELECT serverId FROM VMServer WHERE ip ='" + IP + "' AND portAdress ='" + port + "'" 
        sql += " AND  maxVM =" + maxVM   
        #Ejecutamos el comando
        self.cursor.execute(sql) 
        #Cogemos el utlimo
        serverId = self.cursor.lastrowid
        #Actualizamos la base de datos
        self.db.commit() 
        #Lo devolvemos
        return serverId
    
    def unsubscribeServer(self,serverId):
        '''
            Permite eliminar un determinado servidor de máquinas virtuales de la base de datos cuyo
             identificador se le pasa como argumento.
        '''
        #Borramos la máquina virtual
        sql = "DELETE FROM VMServer WHERE serverId = " + serverId
        #Ejecutamos el comando
        self.cursor.execute(sql)
        #Gracias al ON DELETE CASCADE se borrarán las imagenes registradas para este servidor
        #Actualizamos la base de datos
        self.db.commit() 
        
    def getImageServers(self,imageId):
        '''
            Devuelve una lista con todos los identificadores de servidores que pueden dar acceso a la
             imagen cuyo identificador se pasa como argumento.
        '''
        # Creamos la consulta
        sql = "SELECT serverId FROM ServerImages WHERE imageId =" + imageId
        #Ejecutamos el comando
        self.cursor.execute(sql)
        #Recogemos los resultado
        results=self.cursor.fetchall()
        #Guardamos en una lista los ids resultantes
        serverIds = []
        for r in results:
            serverIds.append(r[0])
        #Devolvemos la lista resultado
        return serverIds
    
def main():
    #Instanciamos la clase
    serverVM = ServerVMManager("CygnusCloud","cygnuscloud2012")
    #Comenzamos con las pruebas
    other = 's'
    while(other == 's'):
        print("Escoja un numero de prueba (1-7)")
        prueba = raw_input()
        
        if(prueba == '1'):
            #máximo número de mv en el servidor de mv
            print("Prueba 1")
            print("Indique el identificador del servidor")
            serverId = raw_input()
            mn = serverVM.getMaxVMNumber(serverId)
            print("El máximo número de máquinas virtuales para este servidor son:")
            print(mn)
        elif(prueba == '2'):
            #máximo número de mv en el servidor de mv
            print("Prueba 2")
            print("Indique el identificador del servidor")
            serverId = raw_input()
            mn = serverVM.getFreeVMNumber(serverId)
            print("El número de máquinas virtuales libre para este servidor son:")
            print(mn)
        elif(prueba == '3'):
            #máximo número de mv en el servidor de mv
            print("Prueba 3")
            print("Servidores actualmente dados de alta")
            serverIds = serverVM.getServers()
            for s in serverIds:
                print(s)
        elif(prueba == '4'):
            #máximo número de mv en el servidor de mv
            print("Prueba 4")
            print("Indique el identificador del servidor")
            serverId = raw_input()
            print("Indique el nuevo máximo de máquinas virtuales")
            vmMax = raw_input()
            serverVM.setMaxVM(serverId,vmMax)
            print("El número máximo de máquinas virtuales ha sido cambiado por:")
            print(serverVM.getMaxVMNumber(serverId))
        elif(prueba == '5'):
            #registro de un nuevo servidor
            print("Prueba 5")
            print("Indique el puerto del servidor")
            port = raw_input()
            print("Indique la dirección IP:")
            ip = raw_input()
            print("Indique el número máximo de máquinas virtuales:")
            vmMax = raw_input()
            serverVM.subscribeServer(port,ip,vmMax)
            print("El nuevo servidor ha sido creado:")
            serverVM.showServers()
        elif(prueba == '6'):
            #dar de baja un servidor
            print("Prueba 6")
            print("Indique el identificador del servidor")
            serverId = raw_input()
            serverVM.unsubscribeServer(serverId)
            print("El servidor ha sido dado de baja:")
            serverVM.showServers()
        elif(prueba == '7'):
            #servidores con una determinada imagen
            print("Prueba 7")
            print("Indique el identificador de la imagen")
            imageId = raw_input()
            serverIds = serverVM.getImageServers(imageId)
            print("Servidores que contienen esta imagen:")
            for s in serverIds:
                print(s)
        else:
            print("Prueba no disponible.")
               
        #Comprobamos si se quiere hacer otra prueba
        print("Desea hacer otra prueba?(s/n)")
        other = raw_input()
    
    #Nos desconectamos
    serverVM.disconnect()

    
## Comandos a ejecutar de inicio (solo en caso de pruebas)
if __name__ == "__main__":
    main() 
            