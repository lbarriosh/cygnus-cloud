# -*- coding: UTF8 -*-

from ccutils.enums import enum
from database.utils.connector import BasicDatabaseConnector

SERVER_STATE_T = enum("BOOTING", "READY", "SHUT_DOWN")

class ClusterServerDatabaseConnector(BasicDatabaseConnector):
    """
    Nota: esta clase es ServerVMManager, con los métodos específicos
    de ImagesInServerManager.
    """
    '''
        These objects register and delete virtual machine servers to the database.   
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
        BasicDatabaseConnector.__init__(self, sqlUser, sqlPassword, databaseName)
        
    #===========================================================================
    # No aparecen aquí:
    # - showServers. No hace falta imprimir los datos de los servidores.
    # - el método main() con pruebas. Para eso están las unitarias.
    # - el método getMaxVMNumber. Las estadísticas del servidor se guardan en otra
    #   tabla, y lo que me parece más razonable es que sea el servidor el que nos informe
    #   (al arrancar) de cuántas máquinas virtuales puede alojar.
    #   De todas formas, el servidor de máquinas virtuales actual no hace eso,
    #   por lo que esos datos no están en el esquema
    # - el método getFreeVMNumber no aparece porque el servidor de máquinas virtuales
    #   no nos dice nada de esto.
    #===========================================================================
        
    def deleteVMServerStatics(self, serverId):
        '''
        Borra las estadísticas de un servidor de máquinas virtuales
            Argumentos:
                serverId: el identificador único del servidor
            Devuelve:
                Nada
        '''
        command = "DELETE FROM VMServerStatus WHERE serverId = " + str(serverId)
        self._executeUpdate(command)
        
        
    def getVMServerBasicData(self, serverId):
        '''
            Devuelve la información asociada a un servidor de máquinas virtuales
            Argumentos:
                serverId: el identificador único del servidor
            Devuelve:
                Diccionario con los datos del servidor
                Nota: ¿por qué no una tupla o una lista? Porque el orden en que se devuelven
                las cosas importaría, lo cual es un fastidio para añadir y quitar cosas
                (lo sé por la red). Al devolver un diccionario, es mucho más fácil añadir
                y quitar cosas a devolver.
        '''
        #Creamos la consulta encargada de extraer los datos
        query = "SELECT serverName, serverStatus, serverIP, serverPort FROM VMServer"\
            + " WHERE serverId = " + str(serverId) + ";"
        # Recogemos los resultados
        results=self._executeQuery(query)
        if (results == ()) : 
            return None
        d = dict()
        (name, status, ip, port) = results[0]
        # Devolvemos el resultado 
        d["ServerName"] = name
        d["ServerStatus"] = status
        d["ServerIP"] = ip
        d["ServerPort"] = port
        return d        
        
    def getVMServerStatistics(self, serverId):
        '''
            Devuelve las estadísticas de un servidor de máquinas virtuales
            Argumentos:
                serverId: el identificador único del servidor
            Returns:
                Diccionario con las estadísticas del servidor.
        '''
        #Creamos la consulta encargada de extraer los datos
        query = "SELECT hosts FROM VMServerStatus WHERE serverId = " + str(serverId) + ";"
        results=self._executeQuery(query)
        if (results == ()) : 
            return None
        d = dict()        
        activeHosts = results[0][0]
        d["ActiveHosts"] = activeHosts
        # Devolvemos los resultados
        return d
    
    def getVMServerIDs(self):
        '''
            Permite obtener una lista con los identificadores de todos los servidores de 
            máquinas virtuales que actualmente se encuentran dados de alta en la base de datos.
        
            Nota: este es el antiguo método getServers
            Argumentos: 
                Ninguno
            Devuelve:
                Lista con los identificadores de todos los servidores de máquinas virtuales
        '''
        #Creamos la consulta encargada de extraer los datos
        query = "SELECT serverId FROM VMServer;"  
        #Recogemos los resultado
        results=self._executeQuery(query)
        serverIds = []
        for r in results:
            serverIds.append(r[0])
        #Devolvemos la lista resultado
        return serverIds
    
    def getActiveVMServersConnectionData(self):
        """
        Returns a list containing the active servers' IP addresses.
        Args:
            None
        Returns: 
            Nothing
        """
        query = "SELECT serverIP, serverPort FROM VMServer WHERE serverStatus = " + str(SERVER_STATE_T.READY) + ";"
        results = self._executeQuery(query)
        serverIPs = []
        for r in results :
            serverIPs.append({"ServerIP" : r[0], "ServerPort" : r[1]})
        return serverIPs
        
        
    def subscribeVMServer(self, name, IPAddress, port):
        '''
            Permite registrar un Nuevo servidor de máquinas virtuales con el puerto, la IP y el número
             máximo de máquinas virtuales que se le pasan como argumento
            Argumentos:
                name: nombre del nuevo servidor
                IPAddress: la IP del nuevo servidor
                port: el puerto del nuevo servidor
            Returns:
                El identificador del nuevo servidor.
            Nota: creo que es mejor el nombre registerVMServer. subscribe significa suscribir,
            ratificar algo.
        '''
        #Creamos la consulta encargada de insertar los valores en la base de datos
        query = "INSERT INTO VMServer(serverStatus, serverName, serverIP, serverPort) VALUES (" + \
            str(SERVER_STATE_T.BOOTING) + ", '" + name + "', '" + IPAddress + "'," + str(port) +");"
        #Ejecutamos el comando
        self._executeUpdate(query)      
        #Extraemos el id del servidor recien creado
        query = "SELECT serverId FROM VMServer WHERE serverIP ='" + IPAddress + "';"
        # Nota: con coger una columna que identifique de forma única al servidor, basta.
        # Cuantas menos condiciones se evalúen, menos costoso es esto.
        # Revisé esto porque me cargué una columna, el máximo número de máquinas virtuales.
        #Cogemos el utlimo
        serverId = self.getLastRowId(query)
        #Lo devolvemos
        return serverId
    
    def unsubscribeVMServer(self, serverNameOrIPAddress):
        '''
            Permite eliminar un determinado servidor de máquinas virtuales de la base de datos cuyo
             identificador se le pasa como argumento.
            Argumentos:
                serverNameOrIPAddress: el nombre o la IP del servidor
            Devuelve:
                Nada
            Nota: tuve que dejar de usar el id porque la web no sabe que ids tiene asignado
            cada servidor. Estos son únicos dentro del servidor principal.
        '''
        serverId = self.getVMServerID(serverNameOrIPAddress)
        # Borramos la fila
        query = "DELETE FROM VMServer WHERE serverId = " + str(serverId) + ";"
        #Ejecutamos el comando
        self._executeUpdate(query)
        # Apaño. ON DELETE CASCADE no funciona cuando las tablas usan un motor de almacenamiento
        # distinto. Una usa INNODB (VMServer) y otra usa MEMORY (VMServerStatus, que es nueva)
        query = "DELETE From VMServerStatus WHERE serverId = " + str(serverId) + ";"
        self._executeUpdate(query)
        
    def getImageIDs(self):
        query = "SELECT DISTINCT imageId FROM ImageOnServer;"
        results = self._executeQuery(query)
        imageIDs = []
        for r in results:
            imageIDs.append(r[0])
        return imageIDs
        
    def getImageServers(self, imageId):
        '''
            Devuelve una lista con todos los identificadores de servidores que pueden dar acceso a la
             imagen cuyo identificador se pasa como argumento.
            Argumentos:
                imageId: el identificador único de la imagen
            Devuelve:
                lista con los identificadores de los servidores que tienen la imagen
            Nota: tuve que añadir el estado de los servidores de máquinas virtuales, que no
            estaba contemplado en el diseño inicial. Y tengo que cruzar dos tablas: una imagen
            no está disponible si un servidor que no está preparado, que está apagado o que
            se ha desconectado la tiene. Sólo está disponible si el servidor está listo.
        '''
        # Creamos la consulta
        query = "SELECT ImageOnServer.serverId FROM ImageOnServer " +\
            "INNER JOIN VMServer ON ImageOnServer.serverId = VMServer.serverID " \
                + "WHERE VMServer.serverStatus = " + str(SERVER_STATE_T.READY) \
                + " AND " + "imageId =" + str(imageId) + ";"
        #Recogemos los resultado
        results=self._executeQuery(query)
        #Guardamos en una lista los ids resultantes
        serverIds = []
        for r in results:
            serverIds.append(r[0])
        #Devolvemos la lista resultado
        return serverIds
    
    def getHostedImages(self, serverID):
        '''
            Devuelve la lista de máquinas virtuales que puede albergar el servidor de máquinas virtuales
            cuyo identificador nos proporcionan como argumento.
            Argumentos:
                imageId: el identificador único de la imagen
            Devuelve:
                lista con los identificadores de los servidores que tienen la imagen
        '''
        # Creamos la consulta
        query = "SELECT serverName, imageId FROM VMServer, ImageOnServer " +\
                 "WHERE VMServer.serverId = ImageOnServer.serverId;"
        #Recogemos los resultado
        results=self._executeQuery(query)
        #Guardamos en una lista los ids resultantes
        retrievedData = []
        for r in results:
            retrievedData.append({"ServerName" : r[0], "VMID" : int(r[1])})
        #Devolvemos la lista resultado
        return retrievedData
    
    def getVMServerID(self, nameOrIPAddress):
        '''
        Devuelve el ID de un servidor de máquinas virtuales a partir de su nombre o
        su IP.
        Argumentos:    
            nameOrIPAddress: el nombre o la IP del servidor de máquinas virtuales
        Devuelve:
            El ID del servidor.
        '''
        query = "SELECT serverId FROM VMServer WHERE serverIP = '" + nameOrIPAddress +\
             "' OR serverName = '" + nameOrIPAddress + "';"
        # Execute it
        results=self._executeQuery(query)
        if (results == ()) : 
            return None
        return results[0][0]
    
    def updateVMServerStatus(self, serverId, newStatus):
        '''
            Actualiza el estado de un servidor de máquinas virtuales (listo, arrancando,
            desconectado,...)
            Argumentos:
                serverId: el identificador úncio del servidor
                newStatus: el nuevo estado del servidor
            Devuelve:
                Nada
        '''
        query = "UPDATE VMServer SET serverStatus=" + str(newStatus) + \
            " WHERE serverId = " + str(serverId) + ";"
        # Execute it
        self._executeUpdate(query)
        
    def getServerImages(self, serverId):
        '''
            Devuelve una lista con los identificadores de las imágenes asociadas a un servidor 
              de máquinas virtuales.
            Argumentos:
                serverId: el identificador del servidor de máquinas virtuales
            Returns:
                Lista con los identificadores de las imágenes
            Nota: este método está modificado para que un solo objeto me sirva para 
            leer la base de datos. Tal y como estaba, tenía que tener un objeto ImageServerManager
            para cada servidor de máquinas virtuales, y eso son muchas conexiones.
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT imageId FROM ImageOnServer WHERE serverId = " + str(serverId)    
        #Recogemos los resultado
        results=self._executeQuery(sql)
        #Guardamos en una lista los ids resultantes
        serverIds = []
        for r in results:
            serverIds.append(r[0])
        #Devolvemos la lista resultado
        return serverIds
         
    def assignImageToServer(self, serverID, imageID):
        '''
        Asigna una imagen a un servidor de máquinas virtuales
        Argumentos:
            serverID: identificador único del servidor de máquinas virtuales
            imageID: identificador único de la imagen
        Devuelve:
            Nada.
        '''
        # Insert the row in the table
        query = "INSERT INTO ImageOnServer VALUES(" + str(serverID)+ "," + str(imageID)  +") "  
        self._executeUpdate(query)
        
    def setVMServerStatistics(self, serverID, runningHosts):
        '''
        Actualiza las estadísticas de un servidor de máquinas virtuales.
        '''
        query = "INSERT INTO VMServerStatus VALUES(" + str(serverID) + ", " + str(runningHosts) + ");"
        try :
            self._executeUpdate(query)
        except Exception :
            query = "UPDATE VMServerStatus SET hosts = " + str(runningHosts) + " WHERE serverId = "\
                + str(serverID) + ";"
            self._executeUpdate(query)
        
    def setServerBasicData(self, serverId, name, status, IPAddress, port):
        '''
            Modifica los datos básicos de un servidor de máquinas virtuales
            Argumentos:
                name: nuevo nombre del servidor
                status: nuevo estado del servidor
                IPAddress: nueva IP del servidor
                port: nuevo puerto del servidor
            Devuelve:
                Nada
        '''
        # Create the query
        query = "UPDATE VMServer SET serverName = '" + name + "', serverIP = '" + IPAddress + "', "+\
            "serverPort = " + str(port) + ", serverStatus = " + str(status) +\
            " WHERE  serverId = " + str(serverId) + ";"
        # Execute it
        self._executeUpdate(query)