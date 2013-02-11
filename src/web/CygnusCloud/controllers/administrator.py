# coding: utf8


@auth.requires_membership('Administrator')
def runVM():
    createAdressBar()
    return dict()
    
@auth.requires_membership('Administrator')
def servers():
    createAdressBar()
    if(request.args(0) == 'add_remove_servers'):
        form = FORM(T('Servidores'),SELECT('server1','server 2'))
        return dict(form = form)

      
@auth.requires_membership('Administrator')
def users():  
    createAdressBar()
    if(request.args(0) == 'add'):
        #Creamos el primer formulario
        form = FORM(HR(),H2(T('Añadir un nuevo usuario')),DIV( T('Nombre: '),BR(),INPUT(_name = 'name')),
                DIV( T('Contraseña: '),BR(),INPUT(_name ='password')),
                DIV(T('Grupo: '),BR(),SELECT(_name = 'group',*[OPTION(row.role,_value = T(str(row.role))) 
                for row in userDB().select(userDB.auth_group.role)])),HR(),CENTER(INPUT(_type='submit',_name = 'add' ,_value=T('Añadir Usuario'))))                
        
        if form.accepts(request.vars,keepvalues=True) and form.vars.add:
            if(form.vars.name != None) and (form.vars.name != "") and (form.vars.password != None) and (form.vars.password != ""):
                #Si el email no esta repetido
                if(userDB(userDB.auth_user.email == form.vars.name).count() == 0):
                    #Añadimos el nuevo usuario a la base de datos
                    userId = userDB.auth_user.insert(email = form.vars.name,password = userDB.auth_user.password.validate(form.vars.password)[0])
                    groupId = userDB(userDB.auth_group.role == form.vars.group).select(userDB.auth_group.id)[0]
                    userDB.auth_membership.insert(group_id = groupId, user_id = userId)
                    
            #redireccinamos 
            redirect(URL(c='administrator',f='users',args = ['add'],vars = dict(usersFind=request.vars.usersFind) ))
        #Devolvemos el formulario             
        return dict(form = form)
        
    elif(request.args(0) == 'associate_subjects'):
        #creamos el primer formulario
        form1 = createUserSearchForm(request.args(0))
        #Creamos el segundo formulario
        listUsers = request.vars.usersFind or []
        #Comprobamos si se ha tomado como una lista
        if(isinstance(listUsers,str)):
            listUsers = []
            listUsers.append(request.vars.usersFind)
        #Creamos el segundo formulario    
        form2 = FORM(H2(T('Añadir asignatura')),DIV(T('Usuario'),BR(),SELECT(_name = 'usersSelect', *listUsers)),
              DIV( T('Código: '),BR(),INPUT(_name = 'code')),DIV( T('Grupo de clase: '),BR(),
              INPUT(_name ='classGroup')),INPUT(_type = 'submit',_name = 'add',_value = T('Añadir')),
              INPUT(_type="submit",_name = 'remove',_value=T("Eliminar")))
        #Acción según el botón pulsado
        if form2.accepts(request.vars,keepvalues=True) and form2.vars.add:
           if(len(form2.vars.code) >= 4) and (len(form2.vars.classGroup) == 1): 
               #Si no existia ya la relación la añadimos
               if(userDB((userDB.UserGroup.userId == form2.vars.usersSelect) & (userDB.UserGroup.cod == form2.vars.code) & \
               (userDB.UserGroup.curseGroup == form2.vars.classGroup)).count() == 0) and \
               (userDB((userDB.ClassGroup.cod == form2.vars.code) & (userDB.ClassGroup.curseGroup == form2.vars.classGroup)).count() == 1):
                   userDB.UserGroup.insert(userId = form2.vars.usersSelect,cod = form2.vars.code,curseGroup = form2.vars.classGroup)
                   response.flash = T('Usuario asociado.')
               else:
                    response.flash = T('El usuario ya se encuentra asociado al grupo de asignatura o el grupo de asignatura no existe.')
        elif form2.accepts(request.vars,keepvalues=True) and form2.vars.remove:
            if(userDB((userDB.UserGroup.userId == form2.vars.usersSelect) & (userDB.UserGroup.cod == form2.vars.code) & \
            (userDB.UserGroup.curseGroup == form2.vars.classGroup)).count() == 1):
                userDB((userDB.UserGroup.userId == form2.vars.usersSelect) & (userDB.UserGroup.cod == form2.vars.code) & \
                (userDB.UserGroup.curseGroup == form2.vars.classGroup)).delete()
                response.flash = T('Relación eliminada.')
            else:
                response.flash = T('Esta relación no existe.')

  
        #Devolvemos el formulario             
        return dict(form1 = form1,form2 = form2)
        
    elif(request.args(0) == 'remove'):
        #Creamos el formulario de busqueda
        form1 = createUserSearchForm(request.args(0))
        #Creamos el segundo formulario
        listUsers = request.vars.usersFind or []
        #Comprobamos si se ha tomado como una lista
        if(isinstance(listUsers,str)):
            listUsers = []
            listUsers.append(request.vars.usersFind)
        table = createUserTable(listUsers)
        #Creamos el formulario
        form2 = FORM(table,CENTER(INPUT(_type = 'submit',_name = 'remove',  _value = T('Eliminar seleccionado'))))
        
        if form2.accepts(request.vars,keepvalues=True) and form2.vars.remove:
            if(form2.vars.selection != ""):
                #Extraemos el id del usuario
                userId = userDB(userDB.auth_user.email == listUsers[int(form2.vars.selection)]).select()[0].id
                #Borramos su referencia en la tabla relacional
                userDB(userDB.auth_membership.user_id == userId).delete()
                #Borramos el usuario
                userDB(userDB.auth_user.id == userId).delete()        
                #redireccinamos 
                listUsers.remove(listUsers[int(form2.vars.selection)])
                redirect(URL(c='administrator',f='users',args = ['remove'],vars = dict(usersFind=listUsers) ))
        
        #Devolvemos los dos formularios
        return dict(form1 = form1,form2 = form2)

        
@auth.requires_membership('Administrator')
def subjects():
    createAdressBar()
    if(request.args(0) == 'add'):              
        #Creamos el primer formulario
        form = FORM(HR(),H2(T('Añadir un nueva asignatura')),DIV( T('Código: '),BR(),INPUT(_name = 'cod',_size = '30px')),
                DIV( T('Nombre: '),BR(),INPUT(_name ='name')),
                DIV( T('Año: '),BR(),INPUT(_name ='year')),
                DIV( T('Curso: '),BR(),INPUT(_name ='curse')),
                DIV( T('Grupo de clase: '),BR(),INPUT(_name ='group')),
                HR(),CENTER(INPUT(_type='submit',_name = 'add' ,_value=T('Añadir'))))                
        
        if form.accepts(request.vars) and form.vars.add:
            if(len(form.vars.cod) >= 4) and (len(form.vars.name) != 0) and (len(form.vars.year) == 4) and (len(form.vars.curse) == 1) and \
                (len(form.vars.group) == 1):
                #Si los valores correspondientes son enteros
                try:
                    #Si no existe ya ese grupo
                    if(userDB((userDB.ClassGroup.cod == form.vars.cod) & (userDB.ClassGroup.curseGroup == form.vars.group)).count() == 0):
                        #Si no existe la asignatura, la creamos
                        if(userDB(userDB.Subjects.code == form.vars.cod).count() == 0):
                            userDB.Subjects.insert(code = int(form.vars.cod),name = form.vars.name)
                        userDB.ClassGroup.insert(yearGroup = int(form.vars.year),cod = int(form.vars.cod),curse = int(form.vars.curse),\
                            curseGroup = form.vars.group)
                except ValueError:
                          response.flash = T('Formato de números erroneo')
            #redireccinamos 
            redirect(URL(c='administrator',f='subjects',args = ['add'],vars = dict(usersFind=request.vars.usersFind) ))
        #Devolvemos el formulario             
        return dict(form = form)  
         
    if(request.args(0) == 'remove'): 
        #Creamos el formulario de busqueda
        form1 = createSubjectsSearchForm(request.args(0))
        #Creamos el segundo formulario
        listSubjectsAux = request.vars.subjectsFind or []
        #Comprobamos si se ha tomado como una lista
        
        if(isinstance(listSubjectsAux,str)):
            listSubjects = [eval(request.vars.subjectsFind)]
        else:
            listSubjects = []
            for l in listSubjectsAux:
                    print l
                    listSubjects.append(eval(l))
            #listSubjects.append(request.vars.subjectsFind)
        print listSubjects
        table = createSubjectTable(listSubjects)
        #Creamos el formulario
        form2 = FORM(table,CENTER(INPUT(_type = 'submit',_name = 'remove',  _value = T('Eliminar seleccionado'))))
        
        if form2.accepts(request.vars,keepvalues=True) and form2.vars.remove:
            if(form2.vars.selection != ""):
                #Borramos su referencia en la tabla relacional
                userDB((userDB.UserGroup.cod == listSubjects[int(form2.vars.selection)][0]) & \
                (userDB.UserGroup.curseGroup == listSubjects[int(form2.vars.selection)][1])).delete()
                #Borramos el grupo
                userDB((userDB.ClassGroup.cod == listSubjects[int(form2.vars.selection)][0]) & \
                (userDB.ClassGroup.curseGroup == listSubjects[int(form2.vars.selection)][1])).delete()        
                #redireccinamos 
                listSubjects.remove(listSubjects[int(form2.vars.selection)])
                redirect(URL(c='administrator',f='subjects',args = ['remove'],vars = {'subjectsFind':listSubjects} ))
        
        #Devolvemos los dos formularios
        return dict(form1 = form1,form2 = form2)
    #Página de asociación de asignaturas con máquinas virtuales       
    if(request.args(0) == 'addVM'): 
       #Creamos el formulario de busqueda
        form1 = createSubjectsSearchForm(request.args(0))
        #Creamos el segundo formulario
        listSubjectsAux = request.vars.subjectsFind or []
        #Comprobamos si se ha tomado como una lista
        
        if(isinstance(listSubjectsAux,str)):
            listSubjects = [eval(request.vars.subjectsFind)]
        else:
            listSubjects = []
            for l in listSubjectsAux:
                    print l
                    listSubjects.append(eval(l))
            #listSubjects.append(request.vars.subjectsFind)
        print listSubjects
        table = createSubjectTable(listSubjects)
        #Creamos el segundo formulario    
        form2 = FORM(H2(T('Añadir máquina virtual')),DIV(T('Cod-Grupo de clase'),BR(),SELECT(_name = 'usersSelect',\
               *[OPTION(T(str(listSubjects[i][0]) + '-' + listSubjects[i][1])  ,_value = i) for i in range(len(listSubjects))])),
              DIV( T('Código: '),BR(),INPUT(_name = 'code')),DIV( T('Grupo de clase: '),BR(),
              INPUT(_name ='classGroup')),INPUT(_type = 'submit',_name = 'add',_value = T('Añadir')),
              INPUT(_type="submit",_name = 'remove',_value=T("Eliminar")))
        #Acción según el botón pulsado
        if form2.accepts(request.vars,keepvalues=True) and form2.vars.add:
           if(len(form2.vars.code) >= 4) and (len(form2.vars.classGroup) == 1): 
               #Si no existia ya la relación la añadimos
               if(userDB((userDB.UserGroup.userId == form2.vars.usersSelect) & (userDB.UserGroup.cod == form2.vars.code) & \
               (userDB.UserGroup.curseGroup == form2.vars.classGroup)).count() == 0) and \
               (userDB((userDB.ClassGroup.cod == form2.vars.code) & (userDB.ClassGroup.curseGroup == form2.vars.classGroup)).count() == 1):
                   userDB.UserGroup.insert(userId = form2.vars.usersSelect,cod = form2.vars.code,curseGroup = form2.vars.classGroup)
                   response.flash = T('Usuario asociado.')
               else:
                    response.flash = T('El usuario ya se encuentra asociado al grupo de asignatura o el grupo de asignatura no existe.')
        elif form2.accepts(request.vars,keepvalues=True) and form2.vars.remove:
            if(userDB((userDB.UserGroup.userId == form2.vars.usersSelect) & (userDB.UserGroup.cod == form2.vars.code) & \
            (userDB.UserGroup.curseGroup == form2.vars.classGroup)).count() == 1):
                userDB((userDB.UserGroup.userId == form2.vars.usersSelect) & (userDB.UserGroup.cod == form2.vars.code) & \
                (userDB.UserGroup.curseGroup == form2.vars.classGroup)).delete()
                response.flash = T('Relación eliminada.')
            else:
                response.flash = T('Esta relación no existe.')

  
        #Devolvemos el formulario             
        return dict(form1 = form1,form2 = form2)
          
          
    
def createAdressBar():
 
    response.menu=[[SPAN(T('Arrancar máquina'), _class='highlighted'), False,URL('runVM'),[]],
                    [SPAN(T('Administrar servidores'), _class='highlighted'), False, URL(f = 'servers',args = ['add_remove_servers']),[
                        (T('Añadir/Eliminar'),False,URL(f = 'servers',args = ['add_remove_servers']))]],
                    [SPAN(T('Administrar usuarios'), _class='highlighted'), False, URL(f = 'initUsers',args = ['remove']),[
                        (T('Eliminar'),False,URL(f = 'users',args = ['remove'])),
                        (T('Añadir'),False,URL(f = 'users',args = ['add'])),
                        (T('Asociar asignaturas'),False,URL(f = 'users',args = ['associate_subjects']))]],
                    [SPAN(T('Administrar asignaturas'), _class='highlighted'), False, URL(f = 'subjects',args = ['add']),[
                       (T('Añadir'),False,URL(f = 'subjects',args = ['add'])),
                       (T('Eliminar'),False,URL(f = 'subjects',args = ['remove'])),
                       (T('Administrar máquinas'),False,URL(f = 'subjects',args = ['addVM']))]]]
                       
def createUserSearchForm(state):        
    listTypes = []
    listTypes.append(OPTION('all',_value = T('All')))
    for row in userDB().select(userDB.auth_group.role):
        listTypes.append(OPTION(row.role,_value = T(str(row.role)))) 
        
    form1 = FORM(HR(),H2(T('Buscar un usuario')),DIV( T('Nombre: '),BR(),INPUT(_name = 'name')),
           DIV(T('Grupo: '),BR(),SELECT(_name = 'group', *listTypes)),
           INPUT(_type='submit',_name = 'search',_value=T('Buscar'),_onclick=[]),HR())    
    
    if form1.accepts(request.vars,keepvalues=True) and form1.vars.search:
        query = ""
        if(form1.vars.group != 'All'):
            query =  (userDB.auth_group.role  ==  form1.vars.group) & (userDB.auth_group.id == userDB.auth_membership.group_id) 
            query &= userDB.auth_membership.user_id  ==  userDB.auth_user.id
                
        rows = userDB(query).select(userDB.auth_user.email)

        #Extraemos la lista de usuarios 
        listUsersAux = [] 
        for row in rows :                  
            if(form1.vars.name != "") and (form1.vars.name != None):
                    if (form1.vars.name in row.email):                    
                        listUsersAux.append(row.email)
            else:
                    listUsersAux.append(row.email)
        #redireccinamos con los resultados
        redirect(URL(c='administrator',f='users',args = [state],vars = dict(usersFind=listUsersAux) ))
     
    return form1
    
def createSubjectsSearchForm(state):        

        
    form1 = FORM(HR(),H2(T('Buscar una asignatura')),DIV( T('Codigo: '),BR(),INPUT(_name = 'cod')),
           DIV(T('Nombre: '),BR(),INPUT(_name = 'name')),
           DIV(T('Año: '),BR(),INPUT(_name = 'year')),
           DIV(T('Curso: '),BR(),INPUT(_name = 'curse')),
           DIV(T('Grupo de clase: '),BR(),INPUT(_name = 'group')),
           INPUT(_type='submit',_name = 'search',_value=T('Buscar'),_onclick=[]),HR())    
    
    if form1.accepts(request.vars,keepvalues=True) and form1.vars.search:
        query = ""
        tag = False
        if(len(form1.vars.year) != 0):
            query =  userDB.ClassGroup.yearGroup  ==  form1.vars.year
            tag = True
        if(len(form1.vars.curse) != 0):
            if(tag): 
                query &=  userDB.ClassGroup.curse  ==  form1.vars.curse  
            else:
                query =  userDB.ClassGroup.curse  ==  form1.vars.curse
                tag = True      
        if(len(form1.vars.group) != 0):
            if(tag): 
                query &=  userDB.ClassGroup.curseGroup  ==  form1.vars.group  
            else:
                query =  userDB.ClassGroup.curseGroup  ==  form1.vars.group
                tag = True   
                
        rows = userDB(query).select(userDB.ClassGroup.cod,userDB.ClassGroup.curseGroup)

        #Extraemos la lista de usuarios 
        listSubjectsAux = [] 
        for row in rows :
            add = True                  
            if(form1.vars.name != ""):
                    add = form1.vars.name in userDB(row.cod == userDB.Subjects.code).select()[0].name 
            if(form1.vars.cod != "") and (add):
                    add = form1.vars.cod in str(row.cod)                    
            if(add):
                    listSubjectsAux.append([row.cod,row.curseGroup])
        #redireccinamos con los resultados
        redirect(URL(c='administrator',f='subjects',args = [state],vars = dict(subjectsFind=listSubjectsAux) ))
     
    return form1


def createUserTable(listUsers):
    table = TABLE(_class='data', _name='table')
    table.append(TR(TH('S.'),TH(T('Nombre')), TH(T('Contraseña')), TH(T('Grupo'))))
    i = 0
    for l in listUsers:
        table.append(TR(\
        TD(INPUT(_type='radio',_name = 'selection',_value = i)),\
        TD(LABEL(l)),\
        TD(LABEL(userDB(userDB.auth_user.email==l).select(userDB.auth_user.password)[0].password)),\
        TD(LABEL(userDB((userDB.auth_user.email==l) & (userDB.auth_membership.user_id == userDB.auth_user.id) \
         & (userDB.auth_membership.group_id == userDB.auth_group.id)).select(userDB.auth_group.role)[0].role))))
        i = i + 1
    pass
    return table
    
def createSubjectTable(listSubjects):
    table = TABLE(_class='data', _name='table')
    table.append(TR(TH('S.'),TH(T('Cod-Asignatura'),TH(T('Grupo')))))
    i = 0
    for l in listSubjects:
        table.append(TR(\
        TD(INPUT(_type='radio',_name = 'selection',_value = i)),\
        TD(LABEL(str(l[0]) + '-' + userDB(l[0] == userDB.Subjects.code).select()[0].name),_width = '50%'),
        TD(LABEL(l[1]))))
        i = i + 1
    pass
    return table
