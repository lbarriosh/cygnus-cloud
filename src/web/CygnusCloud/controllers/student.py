'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
   
    File: student.py   
    Version: 2.0
    Description: student controller
   
    Copyright 2012-13 Luis Barrios Hernández, Adrián Fernández Hernández, 
                      Samuel Guayerbas Martín

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

'''

# coding: utf8
from gluon import *
from clusterConnector.clusterConnector import ClusterConnector
from webConstants import dbStatusName,commandsDBName,webUserName, webUserPass
if  session.authorized: redirect(URL(r=request,c='main',f='login'))

'''    
    Método encargado de manejar la página de arranque de máquinas para el usuario
'''
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
        #Extraemos el escudo de la facultad asociada a la carrera
        careerName = userDB((listSubjects[i].UserGroup.cod == userDB.ClassGroup.cod) & \
         (listSubjects[i].UserGroup.curseGroup == userDB.ClassGroup.curseGroup)).select(userDB.ClassGroup.career)[0].career
        facultyPath = userDB(careerName == userDB.careerPictures.careerName ).select(userDB.careerPictures.picturePath)[0].picturePath 
        #Añadimos la información al formulario
        form.append(DIV(TABLE(TR(TH(IMG(_src=URL('static',str(facultyPath)),_style="width:30px;height:30px;",_class='profile')), \
             TH(H3(B(T(userDB(userDB.Subjects.code == listSubjects[i].UserGroup.cod)
            .select(userDB.Subjects.name)[0].name))),_class='izquierda'))),H4(table,_style="margin-left:60px;"),BR()))
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

'''       
    Método encargado de manejar la página de arranque de máquinas para el usuario
'''
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
            #Creamos la tabla dependiendo de la subsección en la que nos encontremos
            if(request.args(0) == 'stopVM'):
                # página de detención de máquinas en ejecución
                table.append(TR(\
                TD(INPUT(_type='radio',_name = 'selection',_value = vm['VMID'],_id = "c"+str(j))),\
                TD(LABEL(vminfo[0]["ImageName"])),
                TD(DIV(P(vminfo[0]["ImageDescription"],_class='izquierda'),_id= 'd' + str(j))),
                TD(DIV(INPUT(_type='submit',_name = 'restart',  _value = T('Reiniciar'),_class="button button-blue"),_id ='s' +  str(j))),
                TD(DIV(INPUT(_type='submit',_name = 'stop',  _value = T('Detener'),_class="button button-blue"),_id = 'r' +  str(j)))))
            else:
                # página de apertura de máquinas en ejecución
                table.append(TR(\
                TD(INPUT(_type='radio',_name = 'selection',_value = vm['VMID'],_id = "c"+str(j))),\
                TD(LABEL(vminfo[0]["ImageName"])),
                TD(DIV(P(vminfo[0]["ImageDescription"],_class='izquierda'),_id= 'd' + str(j))),
                TD(DIV(INPUT(_type='submit',_name = 'open',  _value = T('Abrir'),_class="button button-blue"),_id = 's' + str(j)))))
            j = j + 1

    #Creamos el formulario dependiendo de la subsección en la que nos encontremos 
    if(request.args(0) == 'stopVM'):
        form = FORM(HR(),LABEL(H2(T('Máquinas en ejecución'))),table)
        if(form.accepts(request.vars)) and (form.vars.stop):
            activeVMConectData = connector.getActiveVMsData(False,False)
            for vmInfo in activeVMConectData:
                if vmInfo["VMID"] == int(form.vars.selection):
                    #Paramos la máquina virtual
                    commandId = connector.destroyDomain(vmInfo["DomainUID"])
                    #Esperamos la contestacion
                    errorInfo = connector.waitForCommandOutput(commandId)
                    if(errorInfo != None):
                        response.flash = T(errorInfo['ErrorMessage'])
                    else:
                        redirect(URL(f = 'runningVM' , args = ['stopVM']))
        if(form.accepts(request.vars)) and (form.vars.restart):
            activeVMConectData = connector.getActiveVMsData(False,False)
            for vmInfo in activeVMConectData:
                if vmInfo["VMID"] == int(form.vars.selection):
                    #Forzamos el reinicio
                    commandId = connector.rebootDomain(vmInfo["DomainUID"])
                    #Esperamos la contestacion
                    errorInfo = connector.waitForCommandOutput(commandId)
                    if(errorInfo != None):
                        response.flash = T(errorInfo['ErrorMessage'])
                    else:
                        redirect(URL(f = 'runningVM' , args = ['stopVM']))
    else:
        form = FORM(HR(),LABEL(H2(T('Máquinas en ejecución'))),table,_target='_blank')
        if(form.accepts(request.vars)) and (form.vars.open):
            activeVMConectData = connector.getActiveVMsData(False,False)
            for vmInfo in activeVMConectData:
                if vmInfo["VMID"] == int(form.vars.selection):
                    # Extraemos la información de conexión
                    serverIp = searchVMServerIp(connector.getVMServersData(), vmInfo["VMServerName"])
                    vncInfo = dict(OutputType=2,VNCServerIPAddress=serverIp,VNCServerPort=int(vmInfo["VNCPort"])+1
                        ,VNCServerPassword=str(vmInfo["VNCPassword"]))
            if vncInfo != None:            
                redirect(URL(c='vncClient', f = 'VNCPage', vars = vncInfo)) 
    # Creamos la etiqueta de notificaciones pendientes
    createNotificationAdvise(form,connector)      
    # Devolvemos el formulario        
    return dict(form = form,num = j)

'''
    Método encargado de mostrar las notificaciones pendientes
'''
@auth.requires_membership('Student')
def showNotifications():
    #actualizamos la barra
    createAdressBar()
    #Establecemos la conexión con el servidor 
    connector = conectToServer()
    #Creamos la tabla
    table = TABLE(_class='state_table', _name='table')
    table.append(TR(TH('Tipo',_class='state_table'),TH('Notificación',_class='izquierda state_table')))
    notifications = connector.getPendingNotifications()
    if len(notifications) == 0:
        form = FORM(CENTER(LABEL(T("No hay notificaciones pendientes."))))
    else:
        for note in notifications:
            table.append(TR(TD(note[0],_class='state_table'),TD(note[1],_class='izquierda state_table')))
        form = FORM(table)
    return dict(form=form)
    
    
'''
    Método encargado de crear la barra de acceso
'''
def createAdressBar():
    response.menu=[[T('Arrancar máquina'),False,URL('runVM')],
                        [SPAN(T('Máquinas arrancadas'), _class='highlighted'), False,URL(f ='runningVM',args = ['stopVM']),[
                            (T('Detener máquina'),False,URL(f = 'runningVM',args = ['stopVM'])),
                            (T('Abrir máquina'),False,URL(f = 'runningVM',args = ['openVM']))]],
                        [T('Notificaciones'),False,URL('showNotifications')]]
                        

'''
    Método encargado de crear las máquinas asociadas a una determinada asigantura 
'''  
def createTable(subject,j):
    # Nos conectamos al endpoint
    connector = conectToServer()
    #Creamos la tabla
    table = TABLE(_class='data', _name='table')
    table.append(TR(TH('Selección'),TH(T('Nombre')),TH('Descripcion',_class='izquierda')))
    i = 0
    for l in userDB((userDB.VMByGroup.cod == subject.UserGroup.cod) & \
            (userDB.VMByGroup.curseGroup == subject.UserGroup.curseGroup)).select(userDB.VMByGroup.VMId):
        imageInfo = connector.getBootableImagesData([l.VMId])
        if len(imageInfo) != 0:
                table.append(TR(TD(INPUT(_type='radio',_name = 'selection',_value = l.VMId,_id = "c"+str(i + j))),
                TD(LABEL(imageInfo[0]["ImageName"]),_class='izquierda')
                ,TD(DIV(P(imageInfo[0]["ImageDescription"]),
                CENTER(INPUT(_type='submit',_class="button button-blue",_name = 'run',  _value = T('Arrancar')))
                ,_id = str(i + j)),_class='izquierda')))
        i = i + 1  
    
    return [table,i + j]

   
'''
    Método encargado de establecer la conexión con el endpoint
'''    
def conectToServer():
    #Establecemos la conexión con el servidor principal
    print "Usuario " + userDB(userDB.auth_user.id == auth.user_id).select(userDB.auth_user.email)[0].email
    connector = ClusterConnector(auth.user_id)
    connector.connectToDatabases(dbStatusName,commandsDBName,webUserName, webUserPass)
    return connector

'''
    Método encargado de realizar la busqued a de información de un servidor
'''
def searchVMServerIp(servers, serverName):
    for s in servers:
        if s["VMServerName"] == serverName:
            return s["VMServerIP"]
    return None
    
'''
    Método encargado de crear la etiqueta de notificaciones pendientes
'''
def createNotificationAdvise(form,connector):
    # Extraemos el número de notificaciones pendientes
    notificationNumber= connector.countPendingNotifications()
    if notificationNumber == 1 :
        form.append(DIV(IMG(_src=URL('static','images/mail.png'),_style="width:35px;height:35px;vertical-align: middle;"), \
            A("Tiene " + str(notificationNumber) + " notificación pendiente.",_href=URL(c='student',f='showNotifications'),_style="padding: 8px;"),
            _class="notificationTag"))
    elif notificationNumber > 1 :
        form.append(DIV(IMG(_src=URL('static','images/mail.png'),_style="width:35px;height:35px;vertical-align: middle;"), \
            A("Tiene " + str(notificationNumber) + " notificaciones pendientes.",_href=URL(c='student',f='showNotifications'), \
            _style="padding: 8px;"),_class="notificationTag"))
