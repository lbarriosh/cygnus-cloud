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
    listSubjects = userDB((userDB.UserGroup.userId == auth.user['email']) & \
     (userDB.Subjects.code == userDB.UserGroup.cod)).select(userDB.Subjects.name,userDB.UserGroup.cod,userDB.UserGroup.curseGroup)
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
        form.append(DIV(H3(B(T(userDB(userDB.Subjects.code == listSubjects[i].UserGroup.cod)
            .select(userDB.Subjects.name)[0].name))),BR(),H4(table),BR()))
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
    
    createNotificationAdvise(form,conectToServer())             
    return dict(form = form,num = j)
       
#Método encargado de manejar la página de arranque de máquinas para el usuario
@auth.requires_membership('Student')
def runningVM():
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
            vminfo =  connector.getBootableImagesData([vm['VMID']])
            if(request.args(0) == 'stopVM'):
                table.append(TR(\
                TD(INPUT(_type='radio',_name = 'selection',_value = vm['VMID'],_id = "c"+str(j))),\
                TD(LABEL(vminfo[0]["ImageName"])),
                TD(DIV(P(vminfo[0]["ImageDescription"],_class='izquierda'),_id= 'd' + str(j))),
                TD(DIV(INPUT(_type='submit',_name = 'restart',  _value = T('Reiniciar'),_class="button button-blue"),_id ='s' +  str(j))),
                TD(DIV(INPUT(_type='submit',_name = 'stop',  _value = T('Detener'),_class="button button-blue"),_id = 'r' +  str(j)))))
            else:
                table.append(TR(\
                TD(INPUT(_type='radio',_name = 'selection',_value = vm['VMID'],_id = "c"+str(j))),\
                TD(LABEL(vminfo[0]["ImageName"])),
                TD(DIV(P(vminfo[0]["ImageDescription"],_class='izquierda'),_id= 'd' + str(j))),
                TD(DIV(INPUT(_type='submit',_name = 'open',  _value = T('Abrir'),_class="button button-blue"),_id = 's' + str(j)))))
            j = j + 1

    #Creamos el formulario
   
    if(request.args(0) == 'stopVM'):
        form = FORM(HR(),LABEL(H2(T('Máquinas en ejecución'))),table)
        if(form.accepts(request.vars)) and (form.vars.stop):
                #Paramos la máquina virtual
                commandId = connector.destroyDomain(form.vars.selection)
                #Esperamos la contestacion
                errorInfo = connector.waitForCommandOutput(commandId)
                if(errorInfo != None):
                    response.flash = T(errorInfo['ErrorMessage'])
                else:
                    redirect(URL(f = 'stopVM'))
    else:
        form = FORM(HR(),LABEL(H2(T('Máquinas en ejecución'))),table,_target='_blank')
        if(form.accepts(request.vars)) and (form.vars.open):
            activeVMConectData = connector.getActiveVMsData(False,False)
            for vmInfo in activeVMConectData:
                if vmInfo["VMID"] == int(form.vars.selection):
                    print activeVMConectData
                    print "password tam:" + str(vmInfo["VNCPassword"])
                    serverIp = searchVMServerIp(connector.getVMServersData(), vmInfo["VMServerName"])
                    vncInfo = dict(OutputType=2,VNCServerIPAddress=serverIp,VNCServerPort=int(vmInfo["VNCPort"])+1
                        ,VNCServerPassword=str(vmInfo["VNCPassword"]))
            if vncInfo != None:            
                redirect(URL(c='vncClient', f = 'VNCPage', vars = vncInfo)) 
    createNotificationAdvise(form,connector)             
    return dict(form = form,num = j)

#Método encargado de mostrar las notificaciones pendientes
@auth.requires_membership('Student')
def showNotifications():
    #actualizamos la barra
    createAdressBar()
    #Establecemos la conexión con el servidor 
    connector = conectToServer()
    #Creamos la tabla
    table = TABLE(_class='data', _name='table')
    table.append(TR(TH('Tipo'),TH('Notificación',_class='izquierda')))
    notifications = connector.getPendingNotifications()
    if len(notifications) == 0:
        form = FORM(CENTER(LABEL(T("No hay notificaciones pendientes."))))
    else:
        for note in notifications:
            table.append(TR(TD(note["outputType"]),TD(note["commandOutput"],_class='izquierda')))
        form = FORM(CENTER(table))
    return dict(form=form)
    
    
    
def createAdressBar():
    response.menu=[[T('Arrancar máquina'),False,URL('runVM')],
                        [SPAN(T('Máquinas arrancadas'), _class='highlighted'), False,URL(f ='runVM',args = ['run']),[
                            (T('Detener máquina'),False,URL(f = 'runningVM',args = ['stopVM'])),
                            (T('Abrir máquina'),False,URL(f = 'runningVM',args = ['openVM']))]],
                        [T('Notificaciones'),False,URL('showNotifications')]]
    
def createTable(subject,j):
    connector = conectToServer()
    table = TABLE(_class='data', _name='table')
    table.append(TR(TH('Selección'),TH(T('Nombre')),TH('Descripcion',_class='izquierda')))
    i = 0
    for l in userDB((userDB.VMByGroup.cod == subject.UserGroup.cod) & (userDB.VMByGroup.curseGroup == subject.UserGroup.curseGroup)).select(userDB.VMByGroup.VMId):
        imageInfo = connector.getBootableImagesData([l.VMId])
        if len(imageInfo) != 0:
                table.append(TR(TD(INPUT(_type='radio',_name = 'selection',_value = l.VMId,_id = "c"+str(i + j))),
                TD(LABEL(imageInfo[0]["ImageName"]),_class='izquierda'),TD(LABEL(subject.Subjects.name),_class='izquierda')
                ,TD(LABEL(subject.UserGroup.curseGroup)),TD(DIV(P(imageInfo[0]["ImageDescription"]),
                CENTER(INPUT(_type='submit',_class="button button-blue",_name = 'run',  _value = T('Arrancar')))
                ,_id = str(i + j)),_class='izquierda')))
        i = i + 1  
    
    return [table,i + j]
    
def conectToServer():
    #Establecemos la conexión con el servidor principal
    print "Usuario " + userDB(userDB.auth_user.id == auth.user_id).select(userDB.auth_user.email)[0].email
    connector = ClusterConnector(auth.user_id)
    connector.connectToDatabases(dbStatusName,commandsDBName,webUserName, webUserPass)
    return connector

def searchVMServerIp(servers, serverName):
    for s in servers:
        if s["VMServerName"] == serverName:
            return s["VMServerIP"]
    return None

def createNotificationAdvise(form,connector):
    notificationNumber= connector.countPendingNotifications()
    print notificationNumber
    if notificationNumber > 0 :
        form.append(DIV(A("Tiene " + str(notificationNumber) + " notificaciones pendientes.",_href=URL(c='student',f='showNotifications')),
            _style="background:#1d75fb;position:absolute;top:30%;right:10%;"))
