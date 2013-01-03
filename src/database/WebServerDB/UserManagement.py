# -*- coding: UTF8 -*-
import MySQLdb

class UserManagement():
    '''
        Clase encargada de gestionar las acciones que un usario logueado puede
        realizar sobre la base de datos de la web.
     
    '''

    def __init__(self,sqlUser,sqlPass,logUser):
        '''
        Constructor de la clase
        '''
        #Guardamos los atributos
        self.sqlUser = sqlUser
        self.sqlPass = sqlPass
        self.user = logUser
        #Seleccionamos la base de datos que vamos a manejar
        # Nos conectamos a MySql 
        self.db = self.connect()
        self.cursor = self.db.cursor()
        # Extraemos la lista con los tipos asociados a
        #  el usuario
        self.typeIds = self.getTypeIds()
        
    def connect(self):
        #Seleccionamos la base de datos que vamos a manejar
        # Nos conectamos a MySql 
        db=MySQLdb.connect(host='localhost',user= self.sqlUser,passwd= self.sqlPass)
        cursor=db.cursor()
        #Creamos la consulta encargada de extraer los datos
        sql = "USE DBWebServer"     
        #Ejecutamos el comando
        cursor.execute(sql)
        #devolvemos el cursor
        return db
    
    def disconnect(self):
        #cerramos las conexiones
        self.cursor.close()
        self.db.close()
    
    def showUsers(self):
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT * FROM Users"     
        #Ejecutamos el comando
        self.cursor.execute(sql)
        #Recogemos los resultado
        results=self.cursor.fetchall()
        #Guardamos en una lista los ids resultantes
        for r in results:
            print(r)
            
    def showTypes(self):
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT * FROM UserType"     
        #Ejecutamos el comando
        self.cursor.execute(sql)
        #Recogemos los resultado
        results=self.cursor.fetchall()
        #Guardamos en una lista los ids resultantes
        for r in results:
            print(r)  
              
        
    def getTypeIds(self):
        '''
            Esta función devuelve la lista de tipos asociados
            al usuario logueado
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT typeId FROM TypeOf WHERE userId = " + self.user     
        #Ejecutamos el comando
        self.cursor.execute(sql)
        #Recogemos los resultado
        resultados=self.cursor.fetchall()
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
        sql = "SELECT groupId FROM ClassGroup WHERE userId = " + self.user     
        #Ejecutamos el comando
        self.cursor.execute(sql)
        #Recogemos los resultado
        resultados=self.cursor.fetchall()
        #Guardamos en una lista los ids resultantes
        groupIds = []
        for r in resultados:
            groupIds.append(r[0])
        #Devolvemos la lista resultado
        return groupIds  
    
    def getVMNames(self,idGroup):
        '''
            Esta función devuelve una lista con los diferentes nombres 
             de las máquinas virtuales asociadas a un determinado grupo.
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT VMName FROM VMByGroup WHERE groupId = " + idGroup     
        #Ejecutamos el comando
        self.cursor.execute(sql)
        #Recogemos los resultado
        resultados=self.cursor.fetchall()
        #Guardamos en una lista los ids resultantes
        vmNames = []
        for r in resultados:
            vmNames.append(r[0])
        #Devolvemos la lista resultado
        return vmNames
    
    def getSubjects(self,idGroup):
        '''
            Esta función devuelve una tupla con el nombre de la asignatura asociada
             al grupo pasado como parámetro, el curso en la que se imparte dicha 
             asignatura, el año académico en el que se imparte y el grupo de clase 
             asociado
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT subject,curse,yearGroup,curseGroup FROM UserGroup WHERE groupId = " + idGroup     
        #Ejecutamos el comando
        self.cursor.execute(sql)
        #Recogemos los resultado
        resultado=self.cursor.fetchone()
        #Devolvemos la lista resultado
        return resultado 
    
    def getTeachers(self,idGroup):
        '''
            Esta función devuelve el nombre de los profesores 
            que se encuentran asociados a dicho grupo.
        '''     
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT u.name FROM Users u,ClassGroup cg,UserType ut,TypeOf tof" 
        sql += " WHERE u.userId = cg.userId AND u.userId = tof.userId AND tof.typeId = ut.typeId " 
        sql += " AND ut.name = 'Teacher' AND cg.groupId = " + idGroup     
        #Ejecutamos el comando
        self.cursor.execute(sql)
        #Recogemos los resultado
        resultados=self.cursor.fetchall()
        #Guardamos en una lista los ids resultantes
        teachersNames = []
        for r in resultados:
            teachersNames.append(r[0])
        #Devolvemos la lista resultado
        return teachersNames
    
    def isTypeOf(self,nameType,userId):
        '''
            Esta función comprueba si un determinado usuario es
            del tipo que se indica como argumento
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT ut.name FROM UserType ut,TypeOf tof " 
        sql += "WHERE ut.typeId = tof.typeId AND tof.userId = " + userId     
        #Ejecutamos el comando
        self.cursor.execute(sql)
        #Recogemos los resultado
        resultado=self.cursor.fetchone()
        #Comprobamos si los nombres coinicden
        return (resultado[0] ==  nameType)      
         
    def deleteUser(self,userId):
        '''
            Esta función será una función exclusiva para los administradores y 
             con ella se dará de baja en la base de datos el usuario cuyo 
             identificador se pasa como argumento
        '''
        #Comprobamos que el usuario sea un administrador     
        if(self.isTypeOf("Administrator",self.user)):
            #borramos el usuario
            sql = "DELETE FROM Users WHERE userId =" + userId 
            #Ejecutamos el comando
            self.cursor.execute(sql) 
            # Gracias al ON DELETE CASCADE debería borrarse sus referencias en
            #  el resto de las tablas
            #Actualizamos la base de datos
            self.db.commit() 
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
        if(self.isTypeOf("Administrator",self.user)):
            #insertamos el usuario
            sql = "INSERT  INTO Users(name,pass) VALUES ('" + name + "','" + password + "')"
            #Ejecutamos el comando
            self.cursor.execute(sql) 
            
            #Extraemos el id del usuario que acabamos de crear
            sql = "SELECT userId FROM Users WHERE name ='" + name + "' AND pass = '" + password +"'"
            
            #Ejecutamos el comando
            self.cursor.execute(sql)
            #Recogemos los resultado
            resultados=self.cursor.fetchall()
            #Cogemos el utlimo
            userId = self.cursor.lastrowid
            #Añadimos el tipo
            sql = "INSERT  INTO TypeOf(userId,typeId) VALUES (" + str(userId) + "," + str(typeId) + ")"
            #Ejecutamos el comando
            self.cursor.execute(sql)
            #Actualizamos la base de datos
            self.db.commit() 
            #Si todo ha salido bien devolvemos el id
            return userId 
            
        else:
            #El usuario no es administrador. Lanazamos una excepción
            raise Exception("Not Administrator User") 
 
    def isUserInGroup(self,groupId): 
        '''
            Esta función indica si el usuario pertence a un grupo
        '''
        # Extraemos los grupos del usuario
        groups = self.getUserGroupsIds()
        #Devolvemos true si existe al menos una vez el grupo en la lista
        return (groups.count(groupId) >= 1)
        
        
              
    def deleteVM(self,VMName,groupId): 
        '''
            Esta función permite eliminar de la base de datos una MV cuyo nombre 
             viene dado como parámetro. En caso de que el usuario dado de alta 
             sea un profesor se comprobará que la MV que se quiere eliminar 
             pertenezca a un grupo asociado a dicho profesor
        '''
        #Comprobamos que el usuario sea un administrador o un profesor del grupo
        if(self.isTypeOf("Administrator",self.user) or (self.isTypeOf("Teacher",self.user) and self.isUserInGroup(self,groupId))):

            #Borramos la máquina virtual
            sql = "DELETE FROM VMByGroup WHERE groupId = " + groupId + " AND VMName ='" + VMName + "'"
            #Ejecutamos el comando
            self.cursor.execute(sql)
            #Gracias al ON DELETE CASCADE se eliminará la apareición de esta VM en el resto de tablas
            #Actualizamos la base de datos
            self.db.commit() 
        else:
            #El usuario no es administrador. Lanazamos una excepción
            raise Exception("Not Administrator or Teacher User")
        
    def deleteAllVM(self,groupId):
        '''
            Esta función elimina de la base de datos todas las máquinas 
            virtuales asociadas a un determinado grupo
        ''' 
        #Comprobamos que el usuario sea un administrador o un profesor del grupo
        if(self.isTypeOf("Administrator",self.user) or (self.isTypeOf("Teacher",self.user) and self.isUserInGroup(self,groupId))):
            #Borramos las máquinas virtuales
            sql = "DELETE FROM VMByGroup WHERE groupId = " + groupId 
            #Ejecutamos el comando
            self.cursor.execute(sql)
            #Actualizamos la base de datos
            self.db.commit() 
        else:
            #El usuario no es administrador. Lanazamos una excepción
            raise Exception("Not Administrator or Teacher User")
        
    def createType(self,name):     
        '''
            Esta función será exclusiva para los administradores
             y permitirá crear un nuevo tipo de usuario
        '''
        #Comprobamos que el usuario sea un administrador     
        if(self.isTypeOf("Administrator",self.user)):
            #insertamos el usuario
            sql = "INSERT  INTO UserType(name) VALUES ('" + name + "')"
            #Ejecutamos el comando
            self.cursor.execute(sql)
            #Actualizamos la base de datos
            self.db.commit()  
        else:
            #El usuario no es administrador. Lanazamos una excepción
            raise Exception("Not Administrator User")    

    def deleteType(self,typeId):
        '''
            Esta función será exclusiva para administradores y permite 
             eliminar un tipo de usuarios cuyo identificador se pasa como 
             parámetro.
        '''
        #Comprobamos que el usuario sea un administrador     
        if(self.isTypeOf("Administrator",self.user)):
            #insertamos el usuario
            sql = "DELETE FROM UserType WHERE typeId =" + typeId 
            #Ejecutamos el comando
            self.cursor.execute(sql) 
            #Actualizamos la base de datos
            self.db.commit() 
        else:
            #El usuario no es administrador. Lanazamos una excepción
            raise Exception("Not Administrator User")  
    
    def getGroupId(self,VMName):
        '''
            Esta función devuelve la lista con todos los identificadores de 
             grupos que se encuentran asociados a una máquina virtual
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT groupId FROM VMByGroup WHERE VMName = '" + VMName + "'"     
        #Ejecutamos el comando
        self.cursor.execute(sql)
        #Recogemos los resultado
        resultados=self.cursor.fetchall()
        #Guardamos en una lista los ids resultantes
        groupIds = []
        for r in resultados:
            groupIds.append(r[0])
        #Devolvemos la lista resultado
        return groupIds 
    
    def getUsersId(self,groupId):
        '''
            Esta función permite obtener una lista con los identificadores 
             de los usuario que se encuentran asociados con el grupo.
        ''' 
        #Comprobamos que el usuario sea un administrador o un profesor del grupo
        if(self.isTypeOf("Administrator",self.user) or (self.isTypeOf("Teacher",self.user) and self.isUserInGroup(self,groupId))):

            #Borramos las máquinas virtuales
            sql = "SELECT userId FROM ClassGroup WHERE groupId = " + groupId 
            #Ejecutamos el comando
            self.cursor.execute(sql)
            #Recogemos los resultado
            resultados=self.cursor.fetchall()
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
    userMan = UserManagement("CygnusCloud","cygnuscloud2012",userId)
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
            #tercera prueba: lista de máquinas virtuales
            print("Prueba 4")
            print('Inserte el id de grupo:')
            groupId = raw_input()
            s = userMan.getSubjects(groupId)
            print("asignatura asociadas al grupo :")
            print(s)
        elif(prueba == '5'):         
            #tercera prueba: lista de máquinas virtuales
            print("Prueba 5")
            print('Inserte el id de grupo:')
            groupId = raw_input()
            teachers = userMan.getTeachers(groupId)
            print("profesores asociados al grupo :")
            for t in teachers:
                print(t)
                
        elif(prueba == '6'):         
            #tercera prueba: lista de máquinas virtuales
            print("Prueba 6")
            print('Inserte el id del usuario a eliminar:')
            uId = raw_input()
            teachers = userMan.deleteUser(uId)
            print("Usuario eliminado :")
            userMan.showUsers()
            
        elif(prueba == '7'):         
            #tercera prueba: lista de máquinas virtuales
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
            #tercera prueba: lista de máquinas virtuales
            print("Prueba 8")
            print('Inserte el nombre de la maquina a eliminar:')
            name = raw_input()
            print('Inserte el grupo:')
            groupId = raw_input()
            userMan.deleteVM(name,groupId)
            print("Maquina eliminada:")
            print(userMan.getVMNames(groupId))
        elif(prueba == '9'):         
            #tercera prueba: lista de máquinas virtuales
            print("Prueba 9")
            print('Inserte el grupo cuyas máquinas se quieren eliminar:')
            groupId = raw_input()
            userMan.deleteAllVM(groupId)
            print("Maquinas eliminadas:")
            print(userMan.getVMNames(groupId))
        elif(prueba == '10'):         
            #tercera prueba: lista de máquinas virtuales
            print("Prueba 10")
            print('Inserte el nombre del tipo a crear:')
            name = raw_input()
            userMan.createType(name)
            print("Tipo creado:")
            userMan.showTypes()
        elif(prueba == '11'):         
            #tercera prueba: lista de máquinas virtuales
            print("Prueba 11")
            print('Inserte el id del tipo a eliminar:')
            type = raw_input()
            userMan.deleteType(type)
            print("Tipo eliminado:")
            userMan.showTypes()
        elif(prueba == '12'):         
            #tercera prueba: lista de máquinas virtuales
            print("Prueba 12")
            print('Inserte el nombre de la máquina a buscar:')
            vmName = raw_input()
            groupIds = userMan.getGroupId(vmName)
            print("los grupos con esta máquina son:")
            for g in groupIds:
                print(g)
        elif(prueba == '13'):         
            #tercera prueba: lista de máquinas virtuales
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