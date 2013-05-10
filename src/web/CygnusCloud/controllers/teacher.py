# coding: utf8
from gluon import *
from clusterServer.connector.clusterServerConnector import ClusterServerConnector
from webConstants import dbStatusName,commandsDBName,webUserName, webUserPass

#Método encargado de manejar la página de arranque de máquinas para el usuario
@auth.requires_membership('Teacher')
def runVM():
    #actualizamos la barra
    createAdressBar()
   
    #Calculamos las tablas
    j = 0
    [readyTable,j] = createReadyTable(j)
    #TODO: Descomentar cuando proceda
    #[editingTable,waitingTable,j] = createDisabledTables(j)
    #Creamos el formulario
    form = FORM(HR(),_target='_blank')
    form.append(DIV(H2("Máquinas disponibles"),H4(readyTable),BR()))
    #form.append(DIV(H2("Máquinas en edicion"),H4(editingTable),BR()))
    #form.append(DIV(H2("Máquinas no registradas"),H4(waitingTable),BR()))
    i = 0
    divMaquinas = DIV(_id='maquinas')   
    
        
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
@auth.requires_membership('Teacher')
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
       
       
def createVanillaVM():
    info = LOAD(url=URL('static', 'progressBar.html', scheme='http'),ajax=False)
    table = createVanillaImageTable("Imagen 1",1048576,2,5242880,3145728,3145728,4,8388608,8388608)
    form = FORM(HR(),LABEL(H2(T('Máquinas vanilla'))),table)
    return dict(form = form,info=info)
          
       
   
def createAdressBar():
    response.menu=[[T('Arrancar máquina'),False,URL('runVM')],[T('Detener máquina'),False,URL('stopVM')],
                   [T('Crear nueva máquina'),False,URL('createVanillaVM')],[T('Editar máquina'),False,URL('editVM')]]
    
def createReadyTable(j):
    listSubjects = userDB((userDB.UserGroup.userId == auth.user['email'])).select(userDB.UserGroup.cod,userDB.UserGroup.curseGroup)
    table = TABLE(_class='data', _name='table')
    table.append(TR(TH('Selección'),TH(T('Nombre')),TH(T("Asignatura asociada"),_class='izquierda'),
            TH("Grupo"),TH('Descripcion',_class='izquierda')))
   
    for s in listSubjects:
        i = 0
        subjectName = userDB(userDB.Subjects.code == s.cod).select(userDB.Subjects.name)[0].name
        for l in userDB((userDB.VMByGroup.cod == s.cod) & (userDB.VMByGroup.curseGroup == s.curseGroup) & \
            (userDB.Images.VMId == userDB.VMByGroup.VMId)).select(userDB.Images.name):
            descInfo = userDB((userDB.VMByGroup.cod == s.cod) & \
                 (userDB.VMByGroup.curseGroup == s.curseGroup) & \
                 (userDB.Images.VMId == userDB.VMByGroup.VMId)).select(userDB.Images.VMId,userDB.Images.description)
            
            table.append(TR(TD(INPUT(_type='radio',_name = 'selection',_value = descInfo[i].VMId,_id = "c"+str(i + j)
                )),TD(LABEL(l.name),_class='izquierda'),TD(LABEL(subjectName),_class='izquierda'),TD(LABEL(s.curseGroup)),TD(DIV(P(descInfo[i].description),
                CENTER(INPUT(_type='submit',_class="button button-blue",_name = 'run',  _value = T('Arrancar')))
                ,_id = str(i + j)),_class='izquierda')))
            i = i + 1
        j = j + i
        
    pass
    return [table,j]
    
def createDisabledTables(j):
    connector = conectToServer()
    disabledImages = connector.getEditedImages(auth.user_id)
    editingTable = TABLE(_class='data', _name='table')
    editingTable.append(TR(TH('Selección'),TH(T('Nombre')),TH(T("Asignatura asociada"),_class='izquierda'),
            TH("Grupo"),TH('Descripcion',_class='izquierda')))
    waitingTable = editingTable = TABLE(_class='data', _name='table')
    waitingTable.append(TR(TH('Selección'),TH(T('Nombre')),TH(T("Asignatura asociada"),_class='izquierda'),
            TH("Grupo"),TH('Descripcion',_class='izquierda')))
    for image in disabledImages:
        imageInfo = connector.getBootableImagesData(image)
        if imageInfo["bootable"]:
               subjectsInfo = userDB((VMByGroup.VMId == image)).select(userDB.VMByGroup.cod,userDB.VMByGroup.curseGroup)
               for s in subjectsInfo:
                   subjectName = userDB(userDB.Subjects.code == s.cod).select(userDB.Subjects.name)[0].name
                   waitingTable.append(TR(TD(INPUT(_type='radio',_name = 'selection',_value = descInfo[i].VMId,_id = "c"+str(i + j) )),
                         TD(LABEL(imageInfo["ImageName"]),_class='izquierda'),TD(LABEL(subjectName),_class='izquierda'),TD(LABEL(s.curseGroup)),
                         TD(DIV(P(imageInfo["ImageDescription"]),_id = str(i + j)),_class='izquierda'),_class='notAvaible'))
        else:
           editingTable.append(TR(TD(INPUT(_type='radio',_name = 'selection',_value = descInfo[i].VMId,_id = "c"+str(i + j) )),
              TD(LABEL(imageInfo["ImageName"]),_class='izquierda'),TD(LABEL(""),_class='izquierda'),TD(LABEL("")),
              TD(DIV(P(imageInfo["ImageDescription"]),_id = str(i + j)),_class='izquierda'),_class='notAvaible'))            
            
    
def conectToServer():
    #Establecemos la conexión con el servidor principal
    connector = ClusterServerConnector(auth.user_id)
    connector.connectToDatabases(dbStatusName,commandsDBName,webUserName, webUserPass)
    return connector
    
def createVanillaImageTable(name,ramSize,cpuNumber,osDiskSize,dataDiskSize,maxRam,maxCpuNumber,maxOsDisk,maxDataDisk):
       pRam = ((ramSize*100)/maxRam)
       pCPUs = ((cpuNumber*100)/maxCpuNumber)
       pOsDisk = ((osDiskSize*100)/maxOsDisk)
       pDataDisk = ((dataDiskSize*100)/maxDataDisk)
       
       table = TABLE(_class='data', _name='table')
       table.append(TR(TD(LABEL(name),_style="font-size:17px;")))
       table.append(TR(TD(IMG(_src=URL('static','images/memoryIcon.png'), _alt="memoryIcon",_style="width:35px;"),_class='vanillaData')
           ,TD(LABEL("Memoria Ram"),_class='vanillaData'),
           TD(DIV(SPAN(SPAN(),_style="width:" + str(pRam) + "%;"),_class="meter animate"),_class='vanillaData')
           ,TD(LABEL(ramSize),_class='vanillaData'),_class='vanillaData'))
       table.append(TR(TD(IMG(_src=URL('static','images/cpuIcon.png'), _alt="cpuIcon",_style="width:35px;"),_class='vanillaData')
           ,TD(LABEL("Número Cpus"),_class='vanillaData'),
           TD(DIV(SPAN(SPAN(),_style="width:" + str(pCPUs) + "%;"),_class="meter animate red"),_class='vanillaData')
           ,TD(LABEL(cpuNumber),_class='vanillaData'),_class='vanillaData'))
       table.append(TR(TD(IMG(_src=URL('static','images/osDiskIcon.png'), _alt="memoryIcon",_style="width:30px;"),_class='vanillaData')
           ,TD(LABEL("Espacio disco"),_class='vanillaData'),
           TD(DIV(SPAN(SPAN(),_style="width:" + str(pOsDisk) + "%;"),_class="meter animate blue"),_class='vanillaData')
           ,TD(LABEL(osDiskSize))))
       table.append(TR(TD(IMG(_src=URL('static','images/dataDiskIcon.png'), _alt="memoryIcon",_style="width:30px;"),_class='vanillaData')
           ,TD(LABEL("Espacio datos"),_class='vanillaData'),
           TD(DIV(SPAN(SPAN(),_style="width:" + str(pDataDisk) + "%;"),_class="meter animate orange"),_class='vanillaData')
           ,TD(LABEL(dataDiskSize))))
       return table
