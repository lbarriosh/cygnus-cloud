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
        db=MySQLdb.connect(host='localhost',user= self.sqlUser,passwd= self.sqlPass)
        cursor=db.cursor()
        #Creamos la consulta encargada de extraer los datos
        sql = "USE DBWebServer"     
        #Ejecutamos el comando
        cursor.execute(sql)
        # Extraemos la lista con los tipos asociados a
        #  el usuario
        self.typeIds = self.getTypeIds()
        
        
            
    def getTypeIds(self):
        '''
            Esta función devuelve la lista de tipos asociados
            al usuario logueado
        '''
        # Nos conectamos a MySql 
        db=MySQLdb.connect(host='localhost',user= self.sqlUser,passwd= self.sqlPass)
        cursor=db.cursor()
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT typeId FROM TypeOf WHERE userId = " + self.user     
        #Ejecutamos el comando
        cursor.execute(sql)
        #Recogemos los resultado
        resultados=cursor.fetchall()
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
        # Nos conectamos a MySql 
        db=MySQLdb.connect(host='localhost',user= self.sqlUser,passwd= self.sqlPass)
        cursor=db.cursor()
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT groupId FROM ClassGroup WHERE userId = " + self.user     
        #Ejecutamos el comando
        cursor.execute(sql)
        #Recogemos los resultado
        resultados=cursor.fetchall()
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
        # Nos conectamos a MySql 
        db=MySQLdb.connect(host='localhost',user= self.sqlUser,passwd= self.sqlPass)
        cursor=db.cursor()
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT VMName FROM VMByGroup WHERE groupId = " + idGroup     
        #Ejecutamos el comando
        cursor.execute(sql)
        #Recogemos los resultado
        resultados=cursor.fetchall()
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
        # Nos conectamos a MySql 
        db=MySQLdb.connect(host='localhost',user= self.sqlUser,passwd= self.sqlPass)
        cursor=db.cursor()
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT subject,curse,yearGroup,curseGroup FROM UserGroup WHERE groupId = " + idGroup     
        #Ejecutamos el comando
        cursor.execute(sql)
        #Recogemos los resultado
        resultado=cursor.fetchone()
        #Devolvemos la lista resultado
        return resultado 
    
    def getTeachers(self,idGroup):
        '''
            Esta función devuelve el nombre de los profesores 
            que se encuentran asociados a dicho grupo.
        '''     
        # Nos conectamos a MySql 
        db=MySQLdb.connect(host='localhost',user= self.sqlUser,passwd= self.sqlPass)
        cursor=db.cursor()
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT u.name FROM Users u,UserGroup ug,UserType ut,TypeOf to" 
        sql += "WHERE u.userId = ug.userId AND to.typeId = ut.typeId " 
        sql += " AND ut.name = 'Teacher' AND ug.groupId = " + idGroup     
        #Ejecutamos el comando
        cursor.execute(sql)
        #Recogemos los resultado
        resultados=cursor.fetchall()
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
        # Nos conectamos a MySql 
        db=MySQLdb.connect(host='localhost',user= self.sqlUser,passwd= self.sqlPass)
        cursor=db.cursor()
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT ut.name FROM UserType ut,TypeOf to" 
        sql += "WHERE ut.typeId = to.typeId AND to.userId = " + userId     
        #Ejecutamos el comando
        cursor.execute(sql)
        #Recogemos los resultado
        resultado=cursor.fetchone()
        #Comprobamos si los nombres coinicden
        return (resultado ==  nameType)      
         
    def deleteUser(self,userId):
        '''
            Esta función será una función exclusiva para los administradores y 
             con ella se dará de baja en la base de datos el usuario cuyo 
             identificador se pasa como argumento
        '''
        #Comprobamos que el usuario sea un administrador     
        if(self.isTypeOf("Administrator",self.user)):
            # Nos conectamos a MySql 
            db=MySQLdb.connect(host='localhost',user= self.sqlUser,passwd= self.sqlPass)
            cursor=db.cursor()
            #borramos el usuario
            sql = "DELETE FROM Users WHERE userId =" + userId 
            #Ejecutamos el comando
            cursor.execute(sql) 
            # Gracias al ON DELETE CASCADE debería borrarse sus referencias en
            #  el resto de las tablas
        else:        # Nos conectamos a MySql 
        db=MySQLdb.connect(host='localhost',user= self.sqlUser,passwd= self.sqlPass)
        cursor=db.cursor()
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT groupId FROM ClassGroup WHERE userId = " + self.user     
        #Ejecutamos el comando
        cursor.execute(sql)
        #Recogemos los resultado
        resultados=cursor.fetchall()
        #Guardamos en una lista los ids resultantes
        groupIds = []
        for r in resultados:
            groupIds.append(r[0])
        #Devolvemos la lista resultado
        return groupIds 
            #El usuario no es administrador. Lanazamos una excepción
            raise Exception("Not Administrator User")
    
    def createUser(self,name,password,TypeId):
        '''
            Esta función será una función exclusiva para los administradores 
             y con ella se dará de alta de forma interna a un nuevo usuario,
             cuyo nombre y contraseña se pasan como argumento.
        '''
        #Comprobamos que el usuario sea un administrador     
        if(self.isTypeOf("Administrator",self.user)):
            # Nos conectamos a MySql 
            db=MySQLdb.connect(host='localhost',user= self.sqlUser,passwd= self.sqlPass)
            cursor=db.cursor()
            #insertamos el usuario
            sql = "INSERT  INTO Users VALUES ('" + name + "','" + password + "')"
            #Ejecutamos el comando
            cursor.execute(sql) 
            
            #Extraemos el id del usuario que acabamos de crear
            sql = "SELECT userId FROM Users WHERE name =" + name + " AND pass = " + password
            
            #Ejecutamos el comando
            cursor.execute(sql)
            #Recogemos los resultado
            resultados=cursor.fetchall()
            #Cogemos el utlimo
            userId = resultados[cursor.rowcount -1][0]
            #Añadimos el tipo
            sql = "INSERT  INTO TypeOf VALUES (" + userId +")"
            #Ejecutamos el comando
            cursor.execute(sql)
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
            # Nos conectamos a MySql 
            db=MySQLdb.connect(host='localhost',user= self.sqlUser,passwd= self.sqlPass)
            cursor=db.cursor()
            #Borramos la máquina virtual
            sql = "DELETE FROM VMByGroup WHERE groupId = " + groupId + " AND VMName =" + VMName
            #Ejecutamos el comando
            cursor.execute(sql)
            #Gracias al ON DELETE CASCADE se eliminará la apareición de esta VM en el resto de tablas
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
            # Nos conectamos a MySql 
            db=MySQLdb.connect(host='localhost',user= self.sqlUser,passwd= self.sqlPass)
            cursor=db.cursor()
            #Borramos las máquinas virtuales
            sql = "DELETE FROM VMByGroup WHERE groupId = " + groupId 
            #Ejecutamos el comando
            cursor.execute(sql)
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
            # Nos conectamos a MySql 
            db=MySQLdb.connect(host='localhost',user= self.sqlUser,passwd= self.sqlPass)
            cursor=db.cursor()
            #insertamos el usuario
            sql = "INSERT  INTO UserType VALUES ('" + name + "')"
            #Ejecutamos el comando
            cursor.execute(sql) 
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
            # Nos conectamos a MySql 
            db=MySQLdb.connect(host='localhost',user= self.sqlUser,passwd= self.sqlPass)
            cursor=db.cursor()
            #insertamos el usuario
            sql = "DELETE FROM UserType WHERE typeId =" + typeId 
            #Ejecutamos el comando
            cursor.execute(sql) 
        else:
            #El usuario no es administrador. Lanazamos una excepción
            raise Exception("Not Administrator User")  
    
    def getGroupId(self,VMName):
        '''
            Esta función devuelve la lista con todos los identificadores de 
             grupos que se encuentran asociados a una máquina virtual
        '''
        # Nos conectamos a MySql 
        db=MySQLdb.connect(host='localhost',user= self.sqlUser,passwd= self.sqlPass)
        cursor=db.cursor()
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT groupId FROM VMByGroup WHERE VMName = " + VMName     
        #Ejecutamos el comando
        cursor.execute(sql)
        #Recogemos los resultado
        resultados=cursor.fetchall()
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
            # Nos conectamos a MySql 
            db=MySQLdb.connect(host='localhost',user= self.sqlUser,passwd= self.sqlPass)
            cursor=db.cursor()
            #Borramos las máquinas virtuales
            sql = "SELECT userId FROM ClassGroup WHERE groupId = " + groupId 
            #Ejecutamos el comando
            cursor.execute(sql)
            #Recogemos los resultado
            resultados=cursor.fetchall()
            #Guardamos en una lista los ids resultantes
            usersIds = []
            for r in resultados:
                usersIds.append(r[0])
                #Devolvemos la lista resultado
                return usersIds 
        else:
            #El usuario no es administrador. Lanazamos una excepción
            raise Exception("Not Administrator or Teacher User")      