# coding: utf8
from gluon import *
from clusterEndpoint.databases.editionState_t import EDITION_STATE_T
from clusterConnector.clusterConnector import ClusterConnector
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
    editingTable = createDisabledTables()
    #Creamos el formulario
    form = FORM(HR(),_target='_blank')
    form.append(DIV(H2("Máquinas disponibles"),H4(readyTable),BR()))
    form.append(DIV(H2("Máquinas en edicion"),H4(editingTable),BR()))
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
                TD(DIV(INPUT(_type='submit',_name = 'stop',  _value = T('Detener'),_class="button button-blue"),_id = 'o' +  str(j))),
                ))
            else:
                #Extramos el nombre de la máquina y su descripcion
                table.append(TR(\
                TD(INPUT(_type='radio',_name = 'selection',_value = vm['VMID'],_id = "c"+str(j))),\
                TD(LABEL(vminfo[0]["ImageName"])),
                TD(DIV(P(vminfo[0]["ImageDescription"],_class='izquierda'),_id= 'd' + str(j))),
                TD(DIV(INPUT(_type='submit',_name = 'open',  _value = T('Abrir'),_class="button button-blue"),_id = 'o' +  str(j))),
                ))
            j = j + 1
                

    #Creamos el formulario 
    if(request.args(0) == 'stopVM'):
        form = FORM(HR(),LABEL(H2(T('Máquinas en ejecución'))),table)
        if(form.accepts(request.vars)) and (form.vars.stop):
                #Establecemos la conexión con el servidor 
                connector = conectToServer()
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
            activeVMConectData = connector.getActiveVMsData(True,False)
            for vmInfo in activeVMConectData:
                if vmInfo["VMID"] == int(form.vars.selection):
                    print activeVMConectData
                    print "password tam:" + str(vmInfo["VNCPassword"])
                    serverIp = searchVMServerIp(connector.getVMServersData(), vmInfo["VMServerName"])
                    vncInfo = dict(OutputType=2,VNCServerIPAddress=serverIp,VNCServerPort=int(vmInfo["VNCPort"])+1
                        ,VNCServerPassword=str(vmInfo["VNCPassword"]))
            if vncInfo != None:            
                redirect(URL(c='vncClient', f = 'VNCPage', vars = vncInfo)) 
                

    return dict(form = form,num = j)

       
def createVanillaVM():
    #actualizamos la barra
    createAdressBar()
    progressBarStyle = LOAD(url=URL('static', 'progressBar.html', scheme='http'),ajax=False)
    connector = conectToServer()
    vanillaImagesIds = connector.getBaseImagesData()
    maxValues = connector.getMaxVanillaImageFamilyData()
    table = TABLE(_class='data', _name='table')
    j= 0
    for id in vanillaImagesIds:
        vanillaInfo = connector.getVanillaImageFamilyData(id["VanillaImageFamilyID"])
        osId = connector.getImageData(id["ImageID"])["OSFamily"]
        variantId = connector.getImageData(id["ImageID"])["OSVariant"]
        picturePath = userDB((userDB.pictureByOSId.osId == osId) & (userDB.pictureByOSId.variantId == variantId)
                             & (userDB.pictureByOSId.pictureId == userDB.osPictures.osPictureId )).select(userDB.osPictures.picturePath)[0].picturePath
        subTable = createVanillaImageTable(vanillaInfo["RAMSize"],
                    vanillaInfo["VCPUs"],vanillaInfo["OSDiskSize"],vanillaInfo["DataDiskSize"],
                    maxValues["RAMSize"],maxValues["VCPUs"],maxValues["OSDiskSize"],maxValues["DataDiskSize"])
        table.append(TR(
            TH(IMG(_src=URL('static',str(picturePath)), _alt="memoryIcon",_style="width:35px;"),_style="text-align: right;"),
            TH(LABEL(vanillaInfo["Name"]),_style="font-size:17px;text-align: left;"),_id="t"+str(j)))
        table.append(TR(TD(INPUT(_type='radio',_name = 'selection',_value=str(osId) + 'c' + str(variantId) + 'c' + str(id["ImageID"]) ,_id ="s"+str(j))),
        DIV(subTable,_class='vanillaTR'),_id="r" + str(j)))
        j = j + 1
        
        
    osFamily = SELECT(_name = 'osType',_id= 'osTypeSelect')
    osFamilyData = connector.getOSTypes()
    osFamily.append(OPTION(T("Todos"), _value = '-1' ,_selected="selected"))
    for osf in  osFamilyData:
        osFamily.append(OPTION(osf["FamilyName"],_value = osf["FamilyID"]))
        
    osFamilyVariant = SELECT(_name = 'osVariant',_id= 'osVariantSelect')
    num = 0
    osFamilyVariant.append(OPTION(T("Todas"),_id= num, _value = '-1c-1' ,_selected="selected"))
    for o in  osFamilyData:
        osFamilyVariantData = connector.getOSTypeVariants(o["FamilyID"])
        for osf in  osFamilyVariantData:
            num = num + 1
            osFamilyVariant.append(OPTION(osf["VariantName"],_id = num , _value = str(o["FamilyID"]) + 'c' + str(osf["VariantID"])))
               
    
    form = FORM(DIV( T('Nombre: '),BR(),INPUT(_name = 'newVMName')),BR(),
                DIV( T('Descripcion: '),BR(),TEXTAREA(_name = 'description')),BR(),
                LABEL(H2(T('Imágenes base disponibles:'))),
                DIV(H3(T("Seleccione el Sistema operativo")),BR(),osFamily,osFamilyVariant),BR(),
                CENTER(table),BR(),
                CENTER(INPUT(_type='submit',_name = 'createVM',  _value = T('Crear máquina virtual')
                    ,_class="button button-blue",_style="width:180px;")))
                    
    if form.accepts(request.vars,keepvalues=True) and form.vars.createVM:
           #Creamos la MV
           if len(form.vars.selection) > 0:
                       """
                       print form.vars.selection.split('c')[2]
                       commandId = connector.createImage(form.vars.selection.split('c')[2], form.vars.newVMName, form.vars.description)
                       errorInfo = connector.waitForCommandOutput(commandId)
                       if errorInfo != None:
                               response.flash = T(errorInfo['ErrorMessage'])
                       else:
                                response.flash = "Petición de creación enviada"
                       
                       """      
                       errorInfo = connector.createImage(form.vars.selection.split('c')[2], form.vars.newVMName, form.vars.description)  
                       if(len(connector.getCommandOutput(errorInfo))==0):
                           response.flash = "Petición de creación enviada"
                       else:
                           response.flash = connector.getCommandOutput(errorInfo)
                       
           else:
                   response.flash = "Debe seleccionar una imagen base"
    
           
    return dict(form = form,progressBarStyle=progressBarStyle,num = num,num2 = j)

          
def editVM():
    createAdressBar()
    #Creamos la primera tabla
    connector = conectToServer()
    stoppedImages = TABLE(_class='data', _name = 'stoppedImagesSelect')
    stoppedImages.append(TR(TH('Selección'),TH(T('Nombre'),_class='izquierda'),TH(T('Descripción')),_class='izquierda'))
    runningImages = TABLE(_class='data',_name = 'runningImagesSelect')
    runningImages.append(TR(TH('Selección'),TH(T('Nombre'),_class='izquierda'),TH(T('Descripción')),_class='izquierda'))
    editedImages = connector.getEditedImageIDs(auth.user_id)
    print connector.getPendingNotifications()
    num1= 0
    num2= 0
    for image in editedImages:
        imageInfo = connector.getImageData(image)
        print str(imageInfo["State"]) + 'W' + str(image)
        if (imageInfo["State"] == EDITION_STATE_T.TRANSFER_TO_REPOSITORY) or (imageInfo["State"] == EDITION_STATE_T.VM_ON) or \
                (imageInfo["State"] == EDITION_STATE_T.AUTO_DEPLOYMENT) or (imageInfo["State"] == EDITION_STATE_T.AUTO_DEPLOYMENT_ERROR):
            runningImages.append(TR(TD(INPUT(_type='radio',_name = 'selection1',_value = str(imageInfo["State"]) + 'w' + str(image),
                _id="b"+str(num2))),
                TD(LABEL(imageInfo["ImageName"]),_class='izquierda'),
                TD(DIV(P(imageInfo["ImageDescription"]),_id = "n2" + str(num2)),_class='izquierda')))
            num2= num2 + 1
        else:
            if imageInfo["State"] == EDITION_STATE_T.CHANGES_NOT_APPLIED:
                numSubjects = userDB(userDB.VMByGroup.VMId==imageInfo["ImageID"]).count()
                if numSubjects > 0:
                    state = imageInfo["State"]
                else:
                    state = 8
            #    imageId = imageInfo["ImageID"]
            else:
                state = imageInfo["State"]
            imageId = image
            stoppedImages.append(TR(TD(INPUT(_type='radio',_name = 'selection2',_value = str(state) + 'w' + str(imageId),
                _id="a"+str(num1))),
                TD(LABEL(imageInfo["ImageName"]),_class='izquierda'),
                TD(DIV(P(imageInfo["ImageDescription"]),_id = "n1" + str(num1)),_class='izquierda')))
            num1= num1 + 1  
    #Añadimos imagenes que no estan en edición (pueden comenzar a editarse o eliminarse)
    listSubjects = userDB((userDB.UserGroup.userId == auth.user['email'])).select(userDB.UserGroup.cod,userDB.UserGroup.curseGroup)   
    for s in listSubjects:
       i = 0
       subjectName = userDB(userDB.Subjects.code == s.cod).select(userDB.Subjects.name)[0].name
       for l in userDB((userDB.VMByGroup.cod == s.cod) & (userDB.VMByGroup.curseGroup == s.curseGroup)).select(userDB.VMByGroup.VMId):
           imageInfo =  connector.getBootableImagesData([l.VMId])
           if len(imageInfo) != 0:
               stoppedImages.append(TR(TD(INPUT(_type='radio',_name = 'selection2',_value = "1" + 'w' + str(l.VMId),
                 _id="a"+str(num1))),
                 TD(LABEL(imageInfo[0]["ImageName"]),_class='izquierda'),
                 TD(DIV(P(imageInfo[0]["ImageDescription"]),_id = "n1" + str(num1)),_class='izquierda')))
               num1= num1 + 1 
    #Creamos los formularios
    form1 =  FORM(LABEL(H2(T('Máquinas detenidas'))),stoppedImages,BR(),
        CENTER(DIV(INPUT(_type='submit',_class="button button-blue",_name = 'edit',  _value = T('Editar'),_id='editButton'),
        INPUT(_type='submit',_class="button button-blue",_name = 'delete',  _value = T('Eliminar'),_id='deleteButton',
            _style="width:90px;"),
        INPUT(_type='submit',_class="button button-blue",_name = 'continueEditing',
              _value = T('Seguir editando'),_id='continueEditingButton',_style="width:140px;"),
        INPUT(_type='submit',_class="button button-blue",_name = 'saveChanges',  _value = T('Aplicar cambios'),_id='saveChangesButton',
            _style="width:140px;"))),
       
        CENTER(LABEL("Máquina no disponible",_id='notAvaibleSMessage')),BR())
    
    form2 =  FORM(LABEL(H2(T('Máquinas en ejecución'))),runningImages,BR(),
        CENTER(DIV(INPUT(_type='submit',_class="button button-blue",_name = 'open',  _value = T('Abrir'),_id='openButton'),
        INPUT(_type='submit',_class="button button-blue",_name = 'stop',_value = T('Detener'),_id='stopButton'))),
        CENTER(LABEL("Máquina no disponible",_id='notAvaibleRMessage')),BR(),_target='_blank')
    
    if form1.accepts(request.vars,keepvalues=True) and form1.vars.continueEditing:
           #Creamos la MV
           """
           if len(form1.vars.selection2) > 0:
                       print form1.vars.selection2.split('w')[1]
                       errorInfo = connector.editImage(form1.vars.selection2.split('w')[1])
                       evaluateCommand(connector,errorInfo,"Petición de arranque de máquina en edición enviada")
           else:
                   response.flash = "Debe seleccionar una imagen base"
          """
           print form1.vars.selection2.split('w')[1]
           commandId = connector.editImage(form1.vars.selection2.split('w')[1])
           errorInfo = connector.waitForCommandOutput(commandId)
           if errorInfo != None:
               response.flash = T(errorInfo['ErrorMessage'])
           else:
               response.flash = "Petición de creación enviada"          
                   
    if form1.accepts(request.vars,keepvalues=True) and form1.vars.edit:
           #Creamos la MV
           if len(form1.vars.selection2) > 0:
                       errorInfo = connector.editImage(form1.vars.selection2.split('w')[1])
                       evaluateCommand(connector,errorInfo,"Petición de edición enviada")

           else:
                   response.flash = "Debe seleccionar una imagen base"
    if form1.accepts(request.vars,keepvalues=True) and form1.vars.delete:
           #Creamos la MV
           if len(form1.vars.selection2) > 0:
                       print form1.vars.selection2.split('w')[1]
                       errorInfo = connector.deleteImageFromInfrastructure(form1.vars.selection2.split('w')[1])
                       evaluateCommand(connector,errorInfo,"Petición de eliminación enviada")

           else:
                   response.flash = "Debe seleccionar una imagen base"                  
    if form1.accepts(request.vars,keepvalues=True) and form1.vars.saveChanges:
           #Creamos la MV
           if len(form1.vars.selection2) > 0:
                       errorInfo = connector.deployEditedImage(form1.vars.selection2.split('w')[1])
                       evaluateCommand(connector,errorInfo,"Petición de edición enviada")

           else:
                   response.flash = "Debe seleccionar una imagen base"
    if form2.accepts(request.vars,keepvalues=True) and form2.vars.open:
           #Creamos la MV
           vncInfo=None
           if len(form2.vars.selection1) > 0:
                       #Mandamos la ejecución del cliente noVNC
                        activeVMConectData = connector.getActiveVMsData(True,True)
                        print activeVMConectData
                        print form2.vars.selection1.split('w')[1]
                        for vmInfo in activeVMConectData:
                            if vmInfo["DomainUID"] == form2.vars.selection1.split('w')[1]:
                                
                                serverIp = searchVMServerIp(connector.getVMServersData(), vmInfo["VMServerName"])
                                vncInfo = dict(OutputType=2,VNCServerIPAddress=serverIp,VNCServerPort=int(vmInfo["VNCPort"])+ 1
                                        ,VNCServerPassword=str(vmInfo["VNCPassword"]))
                        if vncInfo != None:            
                            redirect(URL(c='vncClient', f = 'VNCPage', vars = vncInfo)) 

           else:
                   response.flash = "Debe seleccionar una imagen base"
                   
    
    if form2.accepts(request.vars,keepvalues=True) and form2.vars.stop:
           #Creamos la MV
           if len(form2.vars.selection1) > 0:
                #Paramos la máquina virtual
                commandId = connector.destroyDomain(form2.vars.selection1.split('w')[1])
                #Esperamos la contestacion
                errorInfo = connector.waitForCommandOutput(commandId)
                if(errorInfo != None):
                    response.flash = T(errorInfo['ErrorMessage'])
                else:
                    redirect(URL(f = 'editVM'))

           else:
                   response.flash = "Debe seleccionar una imagen base"
    return dict(form1=form1,form2=form2,num1=num1,num2=num2)
    
def associateSubjects():
    createAdressBar()
    #Creamos fromulario para asociar las máquinas en espera
    #TODO: Cambiar por waiting
    connector = conectToServer()
    waitingImages = connector.getEditedImageIDs(auth.user_id)
    waitingSelect = SELECT(_name = 'waitingImagesSelect')
    editedSelect = SELECT(_name = 'editedImagesSelect',_id='editedImagesSelect')
    for image in waitingImages:
        imageInfo = connector.getImageData(image)
        waitingSelect.append(OPTION(imageInfo["ImageName"],_value = imageInfo["ImageID"]))
        if len(userDB(userDB.VMByGroup.VMId==imageInfo["ImageID"]).select()) > 0:
            if request.vars.selectedIndex == str(imageInfo["ImageID"]):
                editedSelect.append(OPTION(imageInfo["ImageName"],_value = imageInfo["ImageID"],_selected='selected'))
            else:
                editedSelect.append(OPTION(imageInfo["ImageName"],_value = imageInfo["ImageID"])) 
             
             
    subjects = userDB((userDB.UserGroup.userId==auth.user['email']) & (userDB.UserGroup.cod == userDB.Subjects.code)
        ).select(userDB.UserGroup.cod,userDB.Subjects.name,userDB.UserGroup.curseGroup)
    subjectsSelect = SELECT(_name = 'userSubjectsSelect')
    for s in subjects:
        subjectsSelect.append(OPTION(str(s.UserGroup.cod) + " " + s.Subjects.name + "- Grupo: " + s.UserGroup.curseGroup 
            ,_value = str(s.UserGroup.cod)+'-'+s.UserGroup.curseGroup))

         
    form1 = FORM(H2(T('Asociar máquinas virtuales')),TABLE(TR(TH("Nombre",_class='izquierda'),TH("Grupo de asignatura",_class='izquierda'),_style="margin:0;")
       ,TR(waitingSelect,subjectsSelect)),CENTER(INPUT(_type='submit',_name = 'asociateSubject',  _value = T('Asociar asignatura')
        ,_class="button button-blue",_style="width:180px;")))
        
    #Extraemos la lista de asignaturas si procede
    listSubjectsAux = request.vars.subjectsFind or []
    #Comprobamos si se ha tomado como una lista 
    if(isinstance(listSubjectsAux,str)):
        listSubjects = [eval(request.vars.subjectsFind)]
    else:
        listSubjects = []
        for l in listSubjectsAux:
            listSubjects.append(eval(l))
            
    searchTable = TABLE(TR(TH("Nombre",_class='izquierda'),_style="margin:0;")
       ,TR(TD(editedSelect,INPUT(_type='submit',_name = 'search',  _value = T('Buscar')
        ,_class="button button-blue",_style="width:100px;"),_class='izquierda')))
    if listSubjectsAux != []:
       
        subjectsSelect = SELECT(_name = 'searchSubjectsSelect')
        for s in listSubjects:
           subjectName = userDB(userDB.Subjects.code==s[0]).select(userDB.Subjects.name)[0].name
           subjectsSelect.append(OPTION(str(s[0]) + " " + subjectName + "- Grupo: " + s[1]
               ,_value = str(s[0])+'-'+s[1]))
        searchTable.append(TR(subjectsSelect,CENTER(INPUT(_type='submit',_name = 'remove',  _value = T('Desvincular máquina')
        ,_class="button button-blue",_style="width:180px;")),_id='searchSolution'))

    form2 = FORM(H2(T('Desvincular máquinas virtuales')),searchTable)    
    
            #Acción según el botón pulsado
    if form1.accepts(request.vars,keepvalues=True) and form1.vars.asociateSubject:
           if(len(form1.vars.userSubjectsSelect) >= 1) and (len(form1.vars.waitingImagesSelect) >= 1): 
               userDB.VMByGroup.insert(VMId = form1.vars.waitingImagesSelect,cod = form1.vars.userSubjectsSelect.split('-')[0],
                   curseGroup = form1.vars.userSubjectsSelect.split('-')[1])
               response.flash = T('Máquina virtual asociada correctamente.')
               
    if form2.accepts(request.vars,keepvalues=True) and form2.vars.search:
           #Buscamos las asignaturas asociadas a esta máquina
           subjects =  userDB(userDB.VMByGroup.VMId == form2.vars.editedImagesSelect).select(userDB.VMByGroup.cod,userDB.VMByGroup.curseGroup)
           listSubjects = [] 
           for s in subjects : 
               listSubjects.append([s.cod,s.curseGroup])
           redirect(URL(c='teacher', f = 'associateSubjects', vars = {'subjectsFind':listSubjects,
               'selectedIndex':form2.vars.editedImagesSelect}))
    if form2.accepts(request.vars,keepvalues=True) and form2.vars.remove:
          #Borramos la entrada
          deleteInfo = userDB((userDB.VMByGroup.VMId==form2.vars.editedImagesSelect) &
                  (userDB.VMByGroup.cod==form2.vars.searchSubjectsSelect.split('-')[0]) & 
                  (userDB.VMByGroup.curseGroup==form2.vars.searchSubjectsSelect.split('-')[1])
                  ).delete()


          response.flash = T('Máquina virtual desvinculada.')
          redirect(URL(c='teacher',f='associateSubjects'))
        
    return dict(form1=form1,form2=form2)
            
         
   
def createAdressBar():
    response.menu=[[T('Arrancar máquina'),False,URL('runVM')],
                   [SPAN(T('Máquinas arrancadas'), _class='highlighted'), False,URL(f ='runVM',args = ['run']),[
                        (T('Detener máquina'),False,URL(f = 'runningVM',args = ['stopVM'])),
                        (T('Abrir máquina'),False,URL(f = 'runningVM',args = ['openVM']))]],
                   [T('Crear nueva máquina'),False,URL('createVanillaVM')],[T('Editar máquina'),False,URL('editVM')]
                   ,[T('Asociar asignaturas'),False,URL('associateSubjects')]]
    
def createReadyTable(j):
    connector = conectToServer()
    listSubjects = userDB((userDB.UserGroup.userId == auth.user['email'])).select(userDB.UserGroup.cod,userDB.UserGroup.curseGroup)
    table = TABLE(_class='data', _name='table')
    table.append(TR(TH('Selección'),TH(T('Nombre')),TH(T("Asignatura asociada"),_class='izquierda'),
            TH("Grupo"),TH('Descripcion',_class='izquierda')))
   
    for s in listSubjects:
        i = 0
        subjectName = userDB(userDB.Subjects.code == s.cod).select(userDB.Subjects.name)[0].name
        for l in userDB((userDB.VMByGroup.cod == s.cod) & (userDB.VMByGroup.curseGroup == s.curseGroup)).select(userDB.VMByGroup.VMId):
            imageInfo = connector.getBootableImagesData([l.VMId])
            if len(imageInfo) != 0:
                table.append(TR(TD(INPUT(_type='radio',_name = 'selection',_value = l.VMId,_id = "c"+str(i + j)            )),
                TD(LABEL(imageInfo[0]["ImageName"]),_class='izquierda'),TD(LABEL(subjectName),_class='izquierda')
                ,TD(LABEL(s.curseGroup)),TD(DIV(P(imageInfo[0]["ImageDescription"]),
                CENTER(INPUT(_type='submit',_class="button button-blue",_name = 'run',  _value = T('Arrancar')))
                ,_id = str(i + j)),_class='izquierda')))
            i = i + 1
        j = j + i
        
    pass
    return [table,j]
    
def createDisabledTables():
    connector = conectToServer()
    editingImageIds = connector.getEditedImageIDs(auth.user_id)
    editingTable = TABLE(_class='data', _name='table')
    editingTable.append(TR(TH('Selección'),TH(T('Nombre')),TH(T("Asignatura asociada"),_class='izquierda'),
            TH("Grupo")))
    for image in editingImageIds:
        imageInfo = connector.getImageData(image)
        subjectsInfo = userDB((userDB.VMByGroup.VMId == imageInfo["ImageID"])).select(userDB.VMByGroup.cod,userDB.VMByGroup.curseGroup)
        if len(subjectsInfo) == 0 :
            editingTable.append(TR(TD(INPUT(_type='radio',_name = 'selection',_value = imageInfo["ImageID"],_disabled="disabled" )),
                             TD(LABEL(imageInfo["ImageName"]),_class='izquierda'),
                             _class='notAvaible'))
        else:
            for s in subjectsInfo:
                subjectName = userDB(userDB.Subjects.code == s.cod).select(userDB.Subjects.name)[0].name
                editingTable.append(TR(TD(INPUT(_type='radio',_name = 'selection',_value = imageInfo["ImageID"],_disabled="disabled" )),
                             TD(LABEL(imageInfo["ImageName"]),_class='izquierda'),TD(LABEL(subjectName),_class='izquierda'),TD(LABEL(s.curseGroup)),
                             _class='notAvaible'))

    """
    waitingImages = connector.getEditedImageIDs(auth.user_id)
    waitingTable  = TABLE(_class='data', _name='table')
    waitingTable.append(TR(TH('Selección'),TH(T('Nombre')),TH(T("Asignatura asociada"),_class='izquierda'),
            TH("Grupo"))) 
            
    #TODO: cambiar por waiting                                                
    for image in waitingImages:
           print image
           imageInfo = connector.getImageData(image)
           subjectsInfo = userDB((userDB.VMByGroup.VMId == image)).select(userDB.VMByGroup.cod,userDB.VMByGroup.curseGroup)
           
           for s in subjectsInfo:    
               subjectName = userDB(userDB.Subjects.code == s.cod).select(userDB.Subjects.name)[0].name
               waitingTable.append(TR(TD(INPUT(_type='radio',_name = 'selection',_value = image,_disabled="disabled" )),
                  TD(LABEL(imageInfo["ImageName"]),_class='izquierda'),TD(LABEL(""),_class='izquierda'),TD(LABEL("")),
                  _class='notAvaible')) 
    """
    return editingTable

                          
            
    
def conectToServer():
    #Establecemos la conexión con el servidor principal
    connector = ClusterConnector(auth.user_id)
    connector.connectToDatabases(dbStatusName,commandsDBName,webUserName, webUserPass)
    return connector
    
def createVanillaImageTable(ramSize,cpuNumber,osDiskSize,dataDiskSize,maxRam,maxCpuNumber,maxOsDisk,maxDataDisk):
       pRam = ((ramSize*100)/maxRam)
       pCPUs = ((cpuNumber*100)/maxCpuNumber)
       pOsDisk = ((osDiskSize*100)/maxOsDisk)
       pDataDisk = ((dataDiskSize*100)/maxDataDisk)
       
       table = TABLE(_class='data', _name='table')
       table.append(TR(TD(IMG(_src=URL('static','images/memoryIcon.png'), _alt="memoryIcon",_style="width:35px;"),_class='vanillaData')
           ,TD(LABEL("Memoria RAM"),_class='vanillaData'),
           TD(DIV(SPAN(SPAN(),_style="width:" + str(pRam) + "%;"),_class="meter animate"),_class='vanillaData')
           ,TD(LABEL(str("%.0f" %(ramSize/1024))+" MB"),_class='vanillaData'),_class='vanillaData'))
       table.append(TR(TD(IMG(_src=URL('static','images/cpuIcon.png'), _alt="cpuIcon",_style="width:35px;"),_class='vanillaData')
           ,TD(LABEL("Número CPUs"),_class='vanillaData'),
           TD(DIV(SPAN(SPAN(),_style="width:" + str(pCPUs) + "%;"),_class="meter animate red"),_class='vanillaData')
           ,TD(LABEL(cpuNumber),_class='vanillaData'),_class='vanillaData'))
       table.append(TR(TD(IMG(_src=URL('static','images/osDiskIcon.png'), _alt="memoryIcon",_style="width:30px;"),_class='vanillaData')
           ,TD(LABEL("Disco SO"),_class='vanillaData'),
           TD(DIV(SPAN(SPAN(),_style="width:" + str(pOsDisk) + "%;"),_class="meter animate blue"),_class='vanillaData')
           ,TD(LABEL(str("%.0f" %(osDiskSize/1024))+" MB")),_class='vanillaData'))
       table.append(TR(TD(IMG(_src=URL('static','images/dataDiskIcon.png'), _alt="memoryIcon",_style="width:30px;"),_class='vanillaData')
           ,TD(LABEL("Disco datos"),_class='vanillaData'),
           TD(DIV(SPAN(SPAN(),_style="width:" + str(pDataDisk) + "%;"),_class="meter animate orange"),_class='vanillaData')
           ,TD(LABEL(str("%.0f" %(dataDiskSize/1024))+" MB")),_class='vanillaData'))
           
       return table

       
def searchMaxValues(rows):
    maxRam = 0
    maxCPUs = 0
    maxOsDisk = 0
    maxDataDisk = 0
    for r in rows:
        if(r["ramSize"] > maxRam):
            maxRam = r["ramSize"]
        if(r["vCPUs"] > maxCPUs):
            maxCPUs = r["vCPUs"]
        if(r["osDiskSize"] > maxOsDisk):
            maxOsDisk = r["osDiskSize"]
        if(r["dataDiskSize"] > maxDataDisk):
            maxDataDisk = r["dataDiskSize"]
    return (maxRam,maxCPUs,maxOsDisk,maxDataDisk)
    
def evaluateCommand(connector,commandId,message):
    if(len(connector.getCommandOutput(commandId))==0):
        response.flash = message
    else:
        response.flash = connector.getCommandOutput(commandId)
        
def searchVMServerIp(servers, serverName):
    for s in servers:
        if s["VMServerName"] == serverName:
            return s["VMServerIP"]
    return None
