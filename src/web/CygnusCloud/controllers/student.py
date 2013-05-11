# coding: utf8
from gluon import *
from clusterConnector.clusterConnector import ClusterConnector
from webConstants import dbStatusName,commandsDBName,webUserName, webUserPass

#Método encargado de manejar la página de arranque de máquinas para el usuario
@auth.requires_membership('Student')
def runVM():
    #actualizamos la barra
    createAdressBar()
    #Creamos el formulario
    print request.vars.actualDescription
    listSubjects = userDB((userDB.UserGroup.userId == auth.user['email'])).select(userDB.UserGroup.cod,userDB.UserGroup.curseGroup)
    #Calculamos las tablas
    tables = []
    j = 0
    for l in listSubjects:
        [table,j] = createTable(l,j)
        tables.append(table)
    #Creamos el formulario
    form = FORM(HR(),_target='_blank')
    i = 0
    divMaquinas = DIV(_id='maquinas')
    for table in tables:     
        form.append(DIV(H3(B(T(userDB(userDB.Subjects.code == listSubjects[i].cod).select(userDB.Subjects.name)[0].name))),BR(),H4(table),BR()))
        i = i + 1
    if(form.accepts(request.vars)) and (form.vars.run):
            if(form.vars.selection != ""):
                #Establecemos la conexión con el servidor 
                connector = conectToServer()
                #Mandamos la ejecución del cliente noVNC
                print form.vars.selection
                commandId = connector.bootUpVM(form.vars.selection)
                #Esperamos la contestacion
                vncInfo = connector.waitForCommandOutput(commandId)
                redirect(URL(c='vncClient', f = 'VNCPage', vars = vncInfo)) 
                 
    return dict(form = form,num = j)
       
#Método encargado de manejar la página de arranque de máquinas para el usuario
@auth.requires_membership('Student')
def stopVM():
    #actualizamos la barra
    createAdressBar()
    #Establecemos la conexión con el servidor 
    connector = conectToServer()
    #Extraemos las máquinas arrancadas por este usuario
    vmList = connector.getActiveVMsData(True)
    
    table = TABLE(_class='data', _name='table')
    table.append(TR(TH('Selección'),TH(T('Máquina virtual'),TH(T('Descripción'),_class='izquierda'))))
    j = 0
    for vm in vmList: 
        #Creamos la tabla con los resultados   
        if(vm['UserID'] == auth.user_id):
            #Extramos el nombre de la máquina y su descripcion
            vminfo = userDB(userDB.Images.VMId == vm['VMID']).select(userDB.Images.name,userDB.Images.description)
            table.append(TR(\
            TD(INPUT(_type='radio',_name = 'selection',_value = vm['VMID'],_id = "c"+str(j))),\
            TD(LABEL(vminfo[0].name)),
            TD(DIV(P(vminfo[0].description,_class='izquierda'),_id= 'd' + str(j))),
            TD(DIV(INPUT(_type='submit',_name = 'stop',  _value = T('Detener'),_class="button button-blue"),_id = str(j)))))
            j = j + 1

    #Creamos el formulario
    form = FORM(HR(),LABEL(H2(T('Máquinas en ejecución'))),table)
    if(form.accepts(request.vars)) and (form.vars.stop):
            #Establecemos la conexión con el servidor 
            connector = conectToServer()
            #Paramos la máquina virtual
            print form.vars.selection
            commandId = connector.destroyDomain(form.vars.selection)
            #Esperamos la contestacion
            errorInfo = connector.waitForCommandOutput(commandId)
            if(errorInfo != None):
                response.flash = T(errorInfo['ErrorMessage'])
            else:
                redirect(URL(f = 'stopVM'))
                 
    return dict(form = form,num = j)
       
   
def createAdressBar():
    response.menu=[[T('Arrancar máquina'),False,URL('runVM')],[T('Detener máquina'),False,URL('stopVM')]]
    
def createTable(subject,j):
    table = TABLE(_class='data', _name='table')
    table.append(TR(TH('Selección'),TH(T('Nombre')),TH('Descripcion',_class='izquierda')))
    i = 0
    for l in userDB((userDB.VMByGroup.cod == subject.cod) & (userDB.VMByGroup.curseGroup == subject.curseGroup) & \
        (userDB.Images.VMId == userDB.VMByGroup.VMId)).select(userDB.Images.name):
        descInfo = userDB((userDB.VMByGroup.cod == subject.cod) & \
             (userDB.VMByGroup.curseGroup == subject.curseGroup) & \
             (userDB.Images.VMId == userDB.VMByGroup.VMId)).select(userDB.Images.VMId,userDB.Images.description)
        table.append(TR(TD(INPUT(_type='radio',_name = 'selection',_value = descInfo[i].VMId,_id = "c"+str(i + j)
        ),TD(LABEL(l.name),_class='izquierda'),TD(DIV(P(descInfo[i].description),CENTER(INPUT(_type='submit',_class="button button-blue",_name = 'run',  _value = T('Arrancar'))),_id = str(i + j)),_class='izquierda'))))
        i = i + 1
        
    pass
    return [table,i + j]
    
def conectToServer():
    #Establecemos la conexión con el servidor principal
    print "Usuario " + userDB(userDB.auth_user.id == auth.user_id).select(userDB.auth_user.email)[0].email
    connector = ClusterConnector(auth.user_id)
    connector.connectToDatabases(dbStatusName,commandsDBName,webUserName, webUserPass)
    return connector
