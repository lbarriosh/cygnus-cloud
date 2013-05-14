# coding: utf8
from gluon import *
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
    [editingTable,waitingTable] = createDisabledTables()
    #Creamos el formulario
    form = FORM(HR(),_target='_blank')
    form.append(DIV(H2("Máquinas disponibles"),H4(readyTable),BR()))
    form.append(DIV(H2("Máquinas en edicion"),H4(editingTable),BR()))
    form.append(DIV(H2("Máquinas no registradas"),H4(waitingTable),BR()))
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
    #actualizamos la barra
    createAdressBar()
    progressBarStyle = LOAD(url=URL('static', 'progressBar.html', scheme='http'),ajax=False)
    connector = conectToServer()
    vanillaImagesIds = connector.getBaseImagesData()
    maxValues = connector.getMaxVanillaImageFamilyData()
    table = TABLE(_class='data', _name='table')
    j= 0
    for id in vanillaImagesIds:
        vanillaInfo = connector.getVanillaImageFamiliyData(id["VanillaImageFamilyID"])
        osId = connector.getImageData(id["ImageID"])["OSFamily"]
        variantId = connector.getImageData(id["ImageID"])["OSVariant"]
        picturePath = userDB((userDB.pictureByOSId.osId == osId) & (userDB.pictureByOSId.variantId == variantId)
                             & (userDB.pictureByOSId.pictureId == userDB.osPictures.osPictureId )).select(userDB.osPictures.picturePath)[0].picturePath
        print picturePath
        subTable = createVanillaImageTable(vanillaInfo["RAMSize"],
                    vanillaInfo["VCPUs"],vanillaInfo["OSDiskSize"],vanillaInfo["DataDiskSize"],
                    maxValues["RAMSize"],maxValues["VCPUs"],maxValues["OSDiskSize"],maxValues["DataDiskSize"])
        table.append(TR(
            TH(IMG(_src=URL('static',str(picturePath)), _alt="memoryIcon",_style="width:35px;"),_style="text-align: right;"),
            TH(LABEL(vanillaInfo["Name"]),_style="font-size:17px;text-align: left;"),_id="t"+str(j)))
        table.append(TR(TD(INPUT(_type='radio',_name = 'selection',_value=str(osId) + 'c' + str(variantId),_id ="s"+str(j))),
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
                LABEL(H2(T('Máquinas vanila disponibles:'))),
                DIV(H3(T("Seleccione el Sistema operativo")),BR(),osFamily,osFamilyVariant),BR(),
                CENTER(table),BR(),
                CENTER(INPUT(_type='submit',_name = 'createVM',  _value = T('Crear máquina virtual')
                    ,_class="button button-blue",_style="width:180px;")))
    print j
    return dict(form = form,progressBarStyle=progressBarStyle,num = num,num2 = j)
          
       
   
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
    
def createDisabledTables():
    connector = conectToServer()
    editingImages = connector.getEditedImageIDs(auth.user_id)
    editingTable = TABLE(_class='data', _name='table')
    editingTable.append(TR(TH('Selección'),TH(T('Nombre')),TH(T("Asignatura asociada"),_class='izquierda'),
            TH("Grupo")))
    for image in editingImages:
        imageInfo = connector.getImageData(image)
        subjectsInfo = userDB((userDB.VMByGroup.VMId == image)).select(userDB.VMByGroup.cod,userDB.VMByGroup.curseGroup)
        for s in subjectsInfo:
            subjectName = userDB(userDB.Subjects.code == s.cod).select(userDB.Subjects.name)[0].name
            editingTable.append(TR(TD(INPUT(_type='radio',_name = 'selection',_value = image,_disabled="disabled" )),
                         TD(LABEL(imageInfo["ImageName"]),_class='izquierda'),TD(LABEL(subjectName),_class='izquierda'),TD(LABEL(s.curseGroup)),
                         _class='notAvaible'))


    waitingImages = connector.getNewImageIDs(auth.user_id)
    waitingTable  = TABLE(_class='data', _name='table')
    waitingTable.append(TR(TH('Selección'),TH(T('Nombre')),TH(T("Asignatura asociada"),_class='izquierda'),
            TH("Grupo")))                                                 
    for image in editingImages:
           print image
           imageInfo = connector.getImageData(image)
           subjectsInfo = userDB((userDB.VMByGroup.VMId == image)).select(userDB.VMByGroup.cod,userDB.VMByGroup.curseGroup)
           
           for s in subjectsInfo:    
               subjectName = userDB(userDB.Subjects.code == s.cod).select(userDB.Subjects.name)[0].name
               waitingTable.append(TR(TD(INPUT(_type='radio',_name = 'selection',_value = image,_disabled="disabled" )),
                  TD(LABEL(imageInfo["ImageName"]),_class='izquierda'),TD(LABEL(""),_class='izquierda'),TD(LABEL("")),
                  _class='notAvaible')) 

    return (editingTable,waitingTable)
              
             
            
    
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
           ,TD(LABEL("Memoria Ram"),_class='vanillaData'),
           TD(DIV(SPAN(SPAN(),_style="width:" + str(pRam) + "%;"),_class="meter animate"),_class='vanillaData')
           ,TD(LABEL(str("%.0f" %(ramSize/1024))+" Mb"),_class='vanillaData'),_class='vanillaData'))
       table.append(TR(TD(IMG(_src=URL('static','images/cpuIcon.png'), _alt="cpuIcon",_style="width:35px;"),_class='vanillaData')
           ,TD(LABEL("Número Cpus"),_class='vanillaData'),
           TD(DIV(SPAN(SPAN(),_style="width:" + str(pCPUs) + "%;"),_class="meter animate red"),_class='vanillaData')
           ,TD(LABEL(cpuNumber),_class='vanillaData'),_class='vanillaData'))
       table.append(TR(TD(IMG(_src=URL('static','images/osDiskIcon.png'), _alt="memoryIcon",_style="width:30px;"),_class='vanillaData')
           ,TD(LABEL("Espacio disco"),_class='vanillaData'),
           TD(DIV(SPAN(SPAN(),_style="width:" + str(pOsDisk) + "%;"),_class="meter animate blue"),_class='vanillaData')
           ,TD(LABEL(str("%.0f" %(osDiskSize/1024))+" Mb")),_class='vanillaData'))
       table.append(TR(TD(IMG(_src=URL('static','images/dataDiskIcon.png'), _alt="memoryIcon",_style="width:30px;"),_class='vanillaData')
           ,TD(LABEL("Espacio datos"),_class='vanillaData'),
           TD(DIV(SPAN(SPAN(),_style="width:" + str(pDataDisk) + "%;"),_class="meter animate orange"),_class='vanillaData')
           ,TD(LABEL(str("%.0f" %(dataDiskSize/1024))+" Mb")),_class='vanillaData'))
           
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
