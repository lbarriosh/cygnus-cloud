# -*- coding: UTF8 -*-
import MySQLdb


class RuntimeData(object):
    '''
        Esta clase se encargará de gestionar las características de las diferentes 
         máquinas virtuales que se encuentran en ejecución en un momento determinado.
         Además también se encargará de registrar en la base de datos las nuevas máquinas 
         virtuales en ejecución y de dar de baja aquellas máquinas que se apaguen.
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
        
    def showVMs(self):
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT * FROM ActualVM" 
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Recogemos los resultado
        results=self.__cursor.fetchall()
        #Mostramos los resultados
        for r in results:
            print(r)        
        

    def getRunningPorts(self):
        '''
            Devuelve una lista con los puertos VNC correspondientes a las máquinas 
             virtuales que se encuentran actualmente en ejecución.
        ''' 
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT VNCPortAdress FROM ActualVM" 
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Recogemos los resultado
        results=self.__cursor.fetchall()
        #Guardamos en una lista los ids resultantes
        ports = []
        for r in results:
            ports.append(r[0])
        #Devolvemos la lista resultado
        return ports
    
    def getUsers(self):
        '''
             Devuelve una lista con los identificadores de todos los usuarios que actualmente
               se encuentran ejecutando una determinada máquina virtual en este servidor de 
               máquinas virtuales.
        ''' 
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT userId FROM ActualVM" 
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Recogemos los resultado
        results=self.__cursor.fetchall()
        #Guardamos en una lista los ids resultantes
        users = []
        for r in results:
            users.append(r[0])
        #Devolvemos la lista resultado
        return users
    
    def getAssignedVM(self,vncPort):
        '''
            Devuelve el identificador de la máquina virtual que se encuentra en ejecución en el 
             puerto VNC pasado como argumento.
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT VMId FROM ActualVM WHERE VNCPortAdress = '" + vncPort + "'" 
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Recogemos el resultado
        result=self.__cursor.fetchone()
        #Devolvemos el resultado
        return result[0] 
    
    def getAssignedVMName(self,vncPort):
        '''
            Devuelve el nombre de la máquina virtual que se encuentra en ejecución
             en  el puerto VNC pasado como argumento.
        '''
         #Creamos la consulta encargada de extraer los datos
        sql = "SELECT vm.name FROM ActualVM av,VirtualMachine vm WHERE av.VNCPortAdress = '" + vncPort + "' AND "
        sql += "vm.VMId = av.VMId " 
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Recogemos el resultado
        result=self.__cursor.fetchone()
        #Devolvemos el resultado
        return result[0] 
    
    def getMachineDataPath(self,vncPort):
        '''
            Devuelve la ruta asociada a la copia de la imagen de la máquina virtual que se encuentra 
             en ejecución en el puertoVNC pasado como argumento.
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT imageCopyPath FROM ActualVM  WHERE VNCPortAdress = '" + vncPort + "'"
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Recogemos el resultado
        result=self.__cursor.fetchone()
        #Devolvemos el resultado
        return result[0] 
    
    def getMacAdress(self,vncPort):
        '''
            Devuelve la dirección MAC del cliente VNC cuyo puerto se pasa como argumento.
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT macAdress FROM ActualVM WHERE VNCPortAdress = '" + vncPort + "'" 
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Recogemos el resultado
        result=self.__cursor.fetchone()
        #Devolvemos el resultado
        return result[0] 
    
    def getPassword(self,vncPort): 
        '''
            Devuelve la contraseña que se ha dado al puerto VNC que se le pasa como argumento.
        ''' 
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT VNCPass FROM ActualVM WHERE VNCPortAdress = '" + vncPort + "'" 
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Recogemos el resultado
        result=self.__cursor.fetchone()
        #Devolvemos el resultado
        return result[0]
    
    def registerVM(self,vncPort,userId, VMId, imageCopyPath, fileConfigCopyPath, mac, password):
        '''
            Permite dar de alta una nueva máquina virtual en ejecución cuyas características se pasan
             como argumentos.
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "INSERT INTO ActualVM VALUES('"  
        sql+=    vncPort + "'," + userId  +"," + VMId +",'" 
        sql +=  imageCopyPath + "','" + fileConfigCopyPath + "','" + mac + "','"
        sql +=  password + "')"  
        #Ejecutamos el comando
        self.__cursor.execute(sql)  
        #Actualizamos la base de datos
        self.__db.commit()              
        #devolvemos el puerto en el que ha sido creado
        return vncPort 
    
    def unregisterVNCPort(self,vncPort):
        '''
            Da de baja en la base de datos el puerto VNC que se le pasa como argumento 
             y con él, todas las características asociadas al mismo.
        ''' 
                #Borramos la máquina virtual
        sql = "DELETE FROM ActualVM WHERE VNCPortAdress = " + vncPort
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Gracias al ON DELETE CASCADE se borrarán las imagenes registradas para este servidor
        #Actualizamos la base de datos
        self.__db.commit() 
        
def main():    
    #Instanciamos la clase
    runtimeData = RuntimeData("CygnusCloud","cygnuscloud2012")
    #Comenzamos con las pruebas
    other = 's'
    while(other == 's'):
        print("Escoja un numero de prueba (1-9)")
        prueba = raw_input()
        
        if(prueba == '1'):
            #Puertos VNC actualmente en uso
            print("Prueba 1")
            print("Los puertos VNC actualmente en uso son:")
            ports = runtimeData.getRunningPorts()
            for p in ports:
                print(p)
        elif(prueba == '2'):
            #usuarios actuales
            print("Prueba 2")
            print("Los usuarios con máquinas virtuales actualmente activas son:")
            users = runtimeData.getUsers()
            for u in users:
                print(u)
        elif(prueba == '3'):
            #MV asociado a un puerto
            print("Prueba 3")
            print("Indique el identificador del puerto")
            port = raw_input()
            VMId = runtimeData.getAssignedVM(port)
            print("La máquina virtual asociada a este puerto es:")
            print(VMId)
        elif(prueba == '4'):
            #nombre de la MV asociado a un puerto
            print("Prueba 4")
            print("Indique el identificador del puerto")
            port = raw_input()
            VMName = runtimeData.getAssignedVMName(port)
            print("La máquina virtual asociada a este puerto es:")
            print(VMName)
        elif(prueba == '5'):
            #ruta de la MV asociado a un puerto
            print("Prueba 5")
            print("Indique el identificador del puerto")
            port = raw_input()
            path = runtimeData.getMachineDataPath(port)
            print("La ruta de la máquina virtual asociada a este puerto es:")
            print(path)
        elif(prueba == '6'):
            #direccion MAC asociado a un puerto
            print("Prueba 6")
            print("Indique el identificador del puerto")
            port = raw_input()
            mac = runtimeData.getMacAdress(port)
            print("La dirección MAC asociada a este puerto es:")
            print(mac)
        elif(prueba == '7'):
            #contraseña asociado a un puerto
            print("Prueba 7")
            print("Indique el identificador del puerto")
            port = raw_input()
            password = runtimeData.getPassword(port)
            print("La contraseña asociada a este puerto es:")
            print(password)
        elif(prueba == '8'):
            #creacion de una nueva MV
            print("Prueba 8")
            print("Indique el identificador del puerto")
            port = raw_input()
            print("Indique el identificador del usuario")
            userId = raw_input()
            print("Indique el identificador de la MV")
            vmId = raw_input()
            print("Indique la ruta")
            path = raw_input()
            print("Indique la ruta del fichero de configuracion:")
            configPath = raw_input()
            print("Indique la direccion MAC")
            mac = raw_input()
            print("Indique la contraseña")
            portPass = raw_input()
            
            portId = runtimeData.registerVM(port,userId,vmId,path, configPath, mac, portPass)
            print("MV registrada:")
            runtimeData.showVMs()
        elif(prueba == '9'):
            #contraseña asociado a un puerto
            print("Prueba 9")
            print("Indique el identificador del puerto a dar de baja")
            port = raw_input()
            runtimeData.unregisterVNCPort(port)
            print("La máquina virtual ha sido dada de baja:")
            runtimeData.showVMs()
        else:
            print("Prueba no disponible.")
               
        #Comprobamos si se quiere hacer otra prueba
        print("Desea hacer otra prueba?(s/n)")
        other = raw_input() 
         
    #Nos desconectamos
    runtimeData.disconnect()

## Comandos a ejecutar de inicio (solo en caso de pruebas)
if __name__ == "__main__":
    main()                        