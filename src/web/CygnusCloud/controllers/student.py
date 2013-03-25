# coding: utf8
from gluon import *
from clusterServer.connector.clusterServerConnector import ClusterServerConnector
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
        form.append(DIV(H3(T(userDB(userDB.Subjects.code == listSubjects[i].cod).select(userDB.Subjects.name)[0].name)),BR(),H4(table),BR()))
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
       
   
def createAdressBar():
    response.menu=[[T('Arrancar máquina'),False,URL('runVM')]]
    
def createTable(subject,j):
    table = TABLE(_class='data', _name='table')
    table.append(TR(TH('S.'),TH(T('Nombre'),TH('Descripcion'))))
    i = 0
    for l in userDB((userDB.VMByGroup.cod == subject.cod) & (userDB.VMByGroup.curseGroup == subject.curseGroup) & \
        (userDB.Images.VMId == userDB.VMByGroup.VMId)).select(userDB.Images.name):
        descInfo = userDB((userDB.VMByGroup.cod == subject.cod) & \
             (userDB.VMByGroup.curseGroup == subject.curseGroup) & \
             (userDB.Images.VMId == userDB.VMByGroup.VMId)).select(userDB.Images.VMId,userDB.Images.description)
        table.append(TR(TD(INPUT(_type='radio',_name = 'selection',_value = descInfo[i].VMId,_id = "c"+str(i + j)
        ),TD(LABEL(l.name)),TD(DIV(P(descInfo[i].description),CENTER(INPUT(_type='submit',_name = 'run',  _value = T('Arrancar'))),_id = str(i + j))))))
        i = i + 1
        
    pass
    return [table,i + j]
    
def conectToServer():
    #Establecemos la conexión con el servidor principal
    connector = ClusterServerConnector(auth.user_id)
    connector.connectToDatabases(dbStatusName,commandsDBName,webUserName, webUserPass)
    return connector
