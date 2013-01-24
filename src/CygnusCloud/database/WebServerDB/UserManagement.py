# -*- coding: UTF8 -*-
import MySQLdb

class UserManagement():
    '''
        Clase encargada de gestionar las acciones que un usuario logueado puede
        realizar sobre la base de datos de la web.
     
    '''

    def __init__(self,sqlUser,sqlPassword,databaseName,logUser):
        '''
            Constructor de la clase
        '''
        #Guardamos los atributos
        self.__sqlUser = sqlUser
        self.__sqlPassword = sqlPassword
        self.__user = logUser
        self.__databaseName = databaseName
        # Nos conectamos a MySql 
        self.__db = self.connect()
        self.__cursor = self.__db.cursor()
        # Extraemos la lista con los tipos asociados a
        #  el usuario
        self.typeIds = self.getTypeIds()
        
    def connect(self):
        '''
            Realiza la conexión con MySql
        '''
        #Seleccionamos la base de datos que vamos a manejar
        # Nos conectamos a MySql 
        db=MySQLdb.connect(host='localhost',user= self.__sqlUser,passwd= self.__sqlPassword)
        cursor=db.cursor()
        #Creamos la consulta encargada de extraer los datos
        sql = "USE " + self.__databaseName     
        #Ejecutamos el comando
        cursor.execute(sql)
        #devolvemos el cursor
        return db
    
    def disconnect(self):
        '''
            Realiza la desconexión con MySql
        '''
        #cerramos las conexiones
        self.__cursor.close()
        self.__db.close()
    
    def showUsers(self):
        '''
            Muestra la lista de usuarios registrados
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT * FROM Users"     
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Recogemos los resultado
        results=self.__cursor.fetchall()
        #Guardamos en una lista los ids resultantes
        for r in results:
            print(r)
            
    def showTypes(self):
        '''
            Muestra la lista de tipos registrados
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT * FROM UserType"     
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Recogemos los resultado
        results=self.__cursor.fetchall()
        #Guardamos en una lista los tipos resultantes
        for r in results:
            print(r)  
              
        
    def getTypeIds(self):
        '''
            Devuelve la lista de tipos asociados
            al usuario logueado
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT typeId FROM TypeOf WHERE userId = " + str(self.__user)     
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Recogemos los resultado
        resultados=self.__cursor.fetchall()
        #Guardamos en una lista los ids resultantes
        typeIds = []
        for r in resultados:
            typeIds.append(r[0])
        #Devolvemos la lista resultado
        return typeIds    
    
    def getUserGroupsIds(self):
        '''
            Esta función devuelve una lista con los identificadores de 
             grupos  asociados al usuario dado de alta en esta sesión
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT groupId FROM ClassGroup WHERE userId = " + str(self.__user)     
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Recogemos los resultado
        resultados=self.__cursor.fetchall()
        #Guardamos en una lista los ids resultantes
        groupIds = []
        for r in resultados:
            groupIds.append(r[0])
        #Devolvemos la lista resultado
        return groupIds  
    
    def getVMNames(self,idGroup):
        '''
             Devuelve una lista con los diferentes nombres 
             de las máquinas virtuales asociadas a un determinado grupo.
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT VMName FROM VMByGroup WHERE groupId = " + str(idGroup)     
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Recogemos los resultado
        results=self.__cursor.fetchall()
        #Guardamos en una lista los nombres resultantes
        vmNames = []
        for r in results:
            vmNames.append(r[0])
        #Devolvemos la lista resultado
        return vmNames
    
    def getSubjects(self,idGroup):
        '''
            Devuelve una tupla con el nombre de la asignatura asociada
             al grupo pasado como parámetro, el curso en la que se imparte dicha 
             asignatura, el año académico en el que se imparte y el grupo de clase 
             asociado
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT subject,curse,yearGroup,curseGroup FROM UserGroup WHERE groupId = " + str(idGroup)     
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Recogemos los resultado
        resultado=self.__cursor.fetchone()
        #Devolvemos la lista resultado
        return resultado 
    
    def getTeachers(self,idGroup):
        '''
            Devuelve el nombre de los profesores 
            que se encuentran asociados a dicho grupo.
        '''     
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT u.name FROM Users u,ClassGroup cg,UserType ut,TypeOf tof" 
        sql += " WHERE u.userId = cg.userId AND u.userId = tof.userId AND tof.typeId = ut.typeId " 
        sql += " AND ut.name = 'Teacher' AND cg.groupId = " + str(idGroup)     
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Recogemos los resultado
        resultados=self.__cursor.fetchall()
        #Guardamos en una lista los nombres resultantes
        teachersNames = []
        for r in resultados:
            teachersNames.append(r[0])
        #Devolvemos la lista resultado
        return teachersNames
    
    def isTypeOf(self,nameType,userId):
        '''
            Comprueba si un determinado usuario es
            del tipo que se indica como argumento
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT ut.name FROM UserType ut,TypeOf tof " 
        sql += "WHERE ut.typeId = tof.typeId AND tof.userId = " + str(userId)     
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Recogemos los resultado
        resultado=self.__cursor.fetchone()
        #Comprobamos si los nombres coinicden
        return (resultado[0] ==  nameType)      
         
    def deleteUser(self,userId):
        '''
            Esta función será una función exclusiva para los administradores y 
             con ella se dará de baja en la base de datos el usuario cuyo 
             identificador se pasa como argumento
        '''
        #Comprobamos que el usuario sea un administrador     
        if(self.isTypeOf("Administrator",self.__user)):
            #borramos el usuario
            sql = "DELETE FROM Users WHERE userId =" + str(userId) 
            #Ejecutamos el comando
            self.__cursor.execute(sql) 
            # Gracias al ON DELETE CASCADE debería borrarse sus referencias en
            #  el resto de las tablas
            #Actualizamos la base de datos
            self.__db.commit() 
        else:
            #El usuario no es administrador. Lanazamos una excepción
            raise Exception("Not Administrator User")
    
    def createUser(self,name,password,typeId):
        '''
            Esta función será una función exclusiva para los administradores 
             y con ella se dará de alta de forma interna a un nuevo usuario,
             cuyo nombre y contraseña se pasan como argumento.
        '''
        #Comprobamos que el usuario sea un administrador     
        if(self.isTypeOf("Administrator",self.__user)):
            #insertamos el usuario
            sql = "INSERT  INTO Users(name,pass) VALUES ('" + name + "','" + password + "')"
            #Ejecutamos el comando
            self.__cursor.execute(sql) 
            #Extraemos el id del usuario que acabamos de crear
            sql = "SELECT userId FROM Users WHERE name ='" + name + "' AND pass = '" + password +"'" 
            #Ejecutamos el comando
            self.__cursor.execute(sql)
            #Recogemos los resultado
            results=self.__cursor.fetchall()
            #Cogemos el utlimo
            userId = self.__cursor.lastrowid
            #Añadimos el tipo
            sql = "INSERT  INTO TypeOf(userId,typeId) VALUES (" + str(userId) + "," + str(typeId) + ")"
            #Ejecutamos el comando
            self.__cursor.execute(sql)
            #Actualizamos la base de datos
            self.__db.commit() 
            #Si todo ha salido bien devolvemos el id
            return userId 
            
        else:
            #El usuario no es administrador. Lanzamos una excepción
            raise Exception("Not Administrator User") 
 
    def isUserInGroup(self,groupId): 
        '''
            Esta función indica si el usuario pertence a un grupo
        '''
        # Extraemos los grupos del usuario
        groups = self.getUserGroupsIds()
        #Devolvemos true si existe al menos una vez el grupo en la lista
        return (groups.count(groupId) >= 1)
    
    def isUserExists(self,userId):
        '''
            Comprueba si un usuario existe
        '''
        #Comprobamos que el usuario sea un administrador     
        if(self.isTypeOf("Administrator",str(self.__user))):
            #Contamos el número de usuarios con ese id
            sql = "SELECT COUNT(*) FROM Users WHERE userId =" + str(userId)
            #Ejecutamos el comando
            self.__cursor.execute(sql)
            #Recogemos los resultado
            result=self.__cursor.fetchone()
            # Si el resultado es 1, el usuario existe
            return (result[0] == 1)
        else:
            #El usuario no es administrador. Lanzamos una excepción
            raise Exception("Not Administrator User") 
        
    def isVMExists(self,VMName):
        '''
            Comprueba si una máquina virtual existe 
        '''
        #Comprobamos que el usuario sea un administrador     
        if(self.isTypeOf("Administrator",str(self.__user))):
            #Contamos el número de MV con este nombre
            sql = "SELECT COUNT(*) FROM VMByGroup WHERE VMName ='" + VMName + "'"
            #Ejecutamos el comando
            self.__cursor.execute(sql)
            #Recogemos los resultado
            result=self.__cursor.fetchone()
            # Si la MV existe el número resultado será 1
            return (result[0] == 1)
        else:
            #El usuario no es administrador. Lanazamos una excepción
            raise Exception("Not Administrator User") 
        
              
    def deleteVM(self,VMName,groupId): 
        '''
            Permite eliminar de la base de datos una MV cuyo nombre 
             viene dado como parámetro. En caso de que el usuario dado de alta 
             sea un profesor se comprobará que la MV que se quiere eliminar 
             pertenezca a un grupo asociado a dicho profesor
        '''
        #Comprobamos que el usuario sea un administrador o un profesor del grupo
        if(self.isTypeOf("Administrator",str(self.__user)) or (self.isTypeOf("Teacher",self.__user) and self.isUserInGroup(self,groupId))):

            #Borramos la máquina virtual
            sql = "DELETE FROM VMByGroup WHERE groupId = " + str(groupId) + " AND VMName ='" + VMName + "'"
            #Ejecutamos el comando
            self.__cursor.execute(sql)
            #Gracias al ON DELETE CASCADE se eliminará la apareición de esta VM en el resto de tablas
            #Actualizamos la base de datos
            self.__db.commit() 
        else:
            #El usuario no es administrador. Lanazamos una excepción
            raise Exception("Not Administrator or Teacher User")
        
    def deleteAllVM(self,groupId):
        '''
            Elimina de la base de datos todas las máquinas 
            virtuales asociadas a un determinado grupo
        ''' 
        #Comprobamos que el usuario sea un administrador o un profesor del grupo
        if(self.isTypeOf("Administrator",self.__user) or (self.isTypeOf("Teacher",self.__user) and self.isUserInGroup(self,groupId))):
            #Borramos las máquinas virtuales
            sql = "DELETE FROM VMByGroup WHERE groupId = " + str(groupId) 
            #Ejecutamos el comando
            self.__cursor.execute(sql)
            #Actualizamos la base de datos
            self.__db.commit() 
        else:
            #El usuario no es administrador. Lanzamos una excepción
            raise Exception("Not Administrator or Teacher User")
        
    def createType(self,name):     
        '''
            Esta función será exclusiva para los administradores
             y permitirá crear un nuevo tipo de usuario
        '''
        #Comprobamos que el usuario sea un administrador     
        if(self.isTypeOf("Administrator",self.__user)):
            #insertamos el usuario
            sql = "INSERT  INTO UserType(name) VALUES ('" + name + "')"
            #Ejecutamos el comando
            self.__cursor.execute(sql)
            #Actualizamos la base de datos
            self.__db.commit() 
            #Extraemos el id del tipo que acabamos de crear
            sql = "SELECT typeId FROM UserType WHERE name ='" + name + "'" 
            
            #Ejecutamos el comando
            self.__cursor.execute(sql)
            #Recogemos los resultado
            results=self.__cursor.fetchone()
            #Devolvemos el id 
            return results[0]
        else:
            #El usuario no es administrador. Lanzamos una excepción
            raise Exception("Not Administrator User")   
     

    def deleteType(self,typeId):
        '''
            Esta función será exclusiva para administradores y permite 
             eliminar un tipo de usuarios cuyo identificador se pasa como 
             parámetro.
        '''
        #Comprobamos que el usuario sea un administrador     
        if(self.isTypeOf("Administrator",self.__user)):
            #insertamos el usuario
            sql = "DELETE FROM UserType WHERE typeId =" + str(typeId) 
            #Ejecutamos el comando
            self.__cursor.execute(sql) 
            #Actualizamos la base de datos
            self.__db.commit() 
        else:
            #El usuario no es administrador. Lanazamos una excepción
            raise Exception("Not Administrator User")  
        
    def isTypeExists(self,typeId):
        '''
            Comprueba si un tipo existe 
        '''
        #Comprobamos que el usuario sea un administrador     
        if(self.isTypeOf("Administrator",str(self.__user))):
            #Contamos el número de tipos con el id dado
            sql = "SELECT COUNT(*) FROM UserType WHERE typeId =" + str(typeId)
            #Ejecutamos el comando
            self.__cursor.execute(sql)
            #Recogemos los resultado
            result=self.__cursor.fetchone()
            # Si el resultado es 1, el tipo existe
            return (result[0] == 1)
        else:
            #El usuario no es administrador. Lanzamos una excepción
            raise Exception("Not Administrator User") 
    
    def getGroupId(self,VMName):
        '''
            Devuelve la lista con todos los identificadores de 
             grupos que se encuentran asociados a una máquina virtual
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT groupId FROM VMByGroup WHERE VMName = '" + VMName + "'"     
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Recogemos los resultado
        resultados=self.__cursor.fetchall()
        #Guardamos en una lista los ids resultantes
        groupIds = []
        for r in resultados:
            groupIds.append(r[0])
        #Devolvemos la lista resultado
        return groupIds 
    
    def getUsersId(self,groupId):
        '''
            Permite obtener una lista con los identificadores 
             de los usuario que se encuentran asociados con el grupo.
        ''' 
        #Comprobamos que el usuario sea un administrador o un profesor del grupo
        if(self.isTypeOf("Administrator",self.__user) or (self.isTypeOf("Teacher",self.__user) and self.isUserInGroup(self,groupId))):

            #Borramos las máquinas virtuales
            sql = "SELECT userId FROM ClassGroup WHERE groupId = " + str(groupId) 
            #Ejecutamos el comando
            self.__cursor.execute(sql)
            #Recogemos los resultado
            resultados=self.__cursor.fetchall()
            #Guardamos en una lista los ids resultantes
            usersIds = []
            for r in resultados:
                usersIds.append(r[0])
            #Devolvemos la lista resultado
            return usersIds 
        else:
            #El usuario no es administrador. Lanazamos una excepción
            raise Exception("Not Administrator or Teacher User") 
        
def main():
    #Obtenemos el usuario
    print('Inserte el id de usuario:')
    userId = raw_input()
    #Instanciamos el objeto
    userMan = UserManagement("CygnusCloud","cygnuscloud2012","DBWebServer",userId)
    sigue = 's'
    while(sigue == 's'):
        print("Escoja un numero de prueba (1-13)")
        prueba = raw_input()
        
        if(prueba == '1'):
            #Primera prueba : obtención de tipo
            print("Prueba 1")
            types = userMan.getTypeIds()
            print("Tipos asociados al usuario :")
            for t in types:
                print(t)
        elif(prueba == '2'):  
            #Segunda prueba: grupos asociados al usuario
            print("Prueba 2")
            groupIds = userMan.getUserGroupsIds()
            print("grupos asociados al usuario :")
            for g in groupIds:
                print(g)
        
        elif(prueba == '3'):         
            #tercera prueba: lista de máquinas virtuales
            print("Prueba 3")
            print('Inserte el id de grupo:')
            groupId = raw_input()
            vmNames = userMan.getVMNames(groupId)
            print("máquinas asociadas al grupo :")
            for v in vmNames:
                print(v)
        elif(prueba == '4'):         
            #cuarta prueba: Asignaturas asociadas a un grupo
            print("Prueba 4")
            print('Inserte el id de grupo:')
            groupId = raw_input()
            s = userMan.getSubjects(groupId)
            print("asignatura asociadas al grupo :")
            print(s)
        elif(prueba == '5'):         
            #quinta prueba: profesores asociados a un grupo
            print("Prueba 5")
            print('Inserte el id de grupo:')
            groupId = raw_input()
            teachers = userMan.getTeachers(groupId)
            print("profesores asociados al grupo :")
            for t in teachers:
                print(t)
                
        elif(prueba == '6'):         
            #sexta prueba: eliminación de un usuario
            print("Prueba 6")
            print('Inserte el id del usuario a eliminar:')
            uId = raw_input()
            teachers = userMan.deleteUser(uId)
            print("Usuario eliminado :")
            userMan.showUsers()
            
        elif(prueba == '7'):         
            #septima prueba: Creación de un usuario
            print("Prueba 7")
            print('Inserte el nombre del usuario a crear:')
            name = raw_input()
            print('Inserte la constrasennia:')
            password = raw_input()
            print('Inserte tipo:')
            typeId = raw_input()
            userMan.createUser(name,password,typeId)
            print("Usuario creado :")
            userMan.showUsers()
        elif(prueba == '8'):         
            #octava prueba: eliminación de una MV
            print("Prueba 8")
            print('Inserte el nombre de la maquina a eliminar:')
            name = raw_input()
            print('Inserte el grupo:')
            groupId = raw_input()
            userMan.deleteVM(name,groupId)
            print("Maquina eliminada:")
            print(userMan.getVMNames(groupId))
        elif(prueba == '9'):         
            #novena prueba : eliminación de todas las MV
            print("Prueba 9")
            print('Inserte el grupo cuyas máquinas se quieren eliminar:')
            groupId = raw_input()
            userMan.deleteAllVM(groupId)
            print("Maquinas eliminadas:")
            print(userMan.getVMNames(groupId))
        elif(prueba == '10'):         
            #Decima prueba : Creación de un tipo
            print("Prueba 10")
            print('Inserte el nombre del tipo a crear:')
            name = raw_input()
            userMan.createType(name)
            print("Tipo creado:")
            userMan.showTypes()
        elif(prueba == '11'):         
            #Undecima prueba: Creación de un tipo
            print("Prueba 11")
            print('Inserte el id del tipo a eliminar:')
            type = raw_input()
            userMan.deleteType(type)
            print("Tipo eliminado:")
            userMan.showTypes()
        elif(prueba == '12'):         
            #duodecima prueba: busqueda de grupos con una MV
            print("Prueba 12")
            print('Inserte el nombre de la máquina a buscar:')
            vmName = raw_input()
            groupIds = userMan.getGroupId(vmName)
            print("los grupos con esta máquina son:")
            for g in groupIds:
                print(g)
        elif(prueba == '13'):         
            #Treceaba prueba : lista de usuarios registrados
            print("Prueba 13")
            print('Inserte el id del grupo:')
            groupId = raw_input()
            userIds = userMan.getUsersId(groupId)
            print("los  usuarios registrados en dicho grupo son:")
            for u in userIds:
                print(u)
        print("Desea hacer otra prueba?(s/n)")
        sigue = raw_input()
    
    #Nos desconectamos
    userMan.disconnect()

    
## Comandos a ejecutar de inicio (solo en caso de pruebas)
if __name__ == "__main__":
    main()     