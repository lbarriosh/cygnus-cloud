# coding: utf8
from clusterConnector.clusterConnector import ClusterConnector
from webConstants import dbStatusName,commandsDBName,webUserName, webUserPass

@auth.requires_membership('Administrator')
def runVM():
    createAdressBar()
    #Establecemos la conexión con el servidor 
    connector = conectToServer()
    if(request.args(0) == 'run'):
        #Creamos el formulario de busqueda
        form1 = FORM(HR(),H2(T('Buscar una asignatura')),DIV( T('Asignatura: '),BR(),INPUT(_name = 'name')),
               INPUT(_type='submit',_class="button button-blue",_name = 'search',_value=T('Buscar')),HR())    
        #Creamos el segundo formulario
        listSubjectsAux = request.vars.subjectsFind or []
        #Comprobamos si se ha tomado como una lista
        print request.vars.subjectsFind    
        if(isinstance(listSubjectsAux,str)):
            listSubjects= [eval(request.vars.subjectsFind)]
        else:
            listSubjects = []
            for l in listSubjectsAux:
                print l
                listSubjects.append(eval(l))
        table = TABLE(_class='data', _name='table')
        table.append(TR(TH('Selección'),TH(T('Cod-Asignatura'),_class='izquierda'),TH(T('Grupo')),TH(T('Nombre')),TH(T('Descripcion'),_class='izquierda')))
        j = 0
        for l in listSubjects:
            i = 0
            subjectName = userDB(userDB.Subjects.code == l[0]).select(userDB.Subjects.name)[0].name
            for s in userDB((userDB.VMByGroup.cod == l[0]) & (userDB.VMByGroup.curseGroup == l[2])).select(userDB.VMByGroup.VMId):
                imageInfo = connector.getBootableImagesData([s.VMId])
                if len(imageInfo) != 0:
                    table.append(TR(TD(INPUT(_type='radio',_name = 'selection',_value = s.VMId,_id = "c"+str(j) )),
                    TD(LABEL(imageInfo[0]["ImageName"]),_class='izquierda'),TD(LABEL(subjectName),_class='izquierda')
                    ,TD(LABEL(l[2])),TD(DIV(P(imageInfo[0]["ImageDescription"]),
                    CENTER(INPUT(_type='submit',_class="button button-blue",_name = 'run',  _value = T('Arrancar')))
                    ,_id = str(j)),_class='izquierda')))
                i = i + 1
                j = j + 1
        
        #Creamos el segundo formulario
        form2 = FORM(LABEL(H2(T('Resultados'))),table,_target='_blank')
            
        #Actuamos frente a la busqueda
        if form1.accepts(request.vars,keepvalues=True) and form1.vars.search:
            if len(form1.vars.name) > 0 :
                try:
                    
                    listSubjectsAux = userDB((userDB.ClassGroup.cod == int(form1.vars.name)) & \
                    (userDB.Subjects.code == userDB.ClassGroup.cod)).select(\
                    userDB.ClassGroup.cod,userDB.ClassGroup.curseGroup,userDB.Subjects.name)
                    listSubjects = [] 
                    for l in listSubjectsAux : 
                            listSubjects.append([l.ClassGroup.cod,l.Subjects.name,l.ClassGroup.curseGroup])
                            
                except ValueError:
                    listSubjectsAux = userDB(userDB.Subjects.code == userDB.ClassGroup.cod).select( \
                    userDB.ClassGroup.cod,userDB.ClassGroup.curseGroup,userDB.Subjects.name)
                    listSubjects = [] 
                    for l in listSubjectsAux :                  
                        if(form1.vars.name != ""):
                                if (form1.vars.name.lower() in l.Subjects.name.lower()):                    
                                    listSubjects.append([l.ClassGroup.cod,l.Subjects.name,l.ClassGroup.curseGroup])
                        else:
                                listSubjects.append([l.ClassGroup.cod,l.Subjects.name,l.ClassGroup.curseGroup])
                
    
                #redireccinamos con los resultados
                redirect(URL(c='administrator',f='runVM',args = ['run'],vars = dict(subjectsFind=listSubjects) ))
        #Actuamos frente al arranque
        if(form2.accepts(request.vars)) and (form2.vars.run):
               if(form2.vars.selection != ""):
                    #Mandamos la ejecución del cliente noVNC
                    commandId = connector.bootUpVM(form2.vars.selection)
                    #Esperamos la contestacion
                    vncInfo = connector.waitForCommandOutput(commandId)
                    redirect(URL(c='vncClient', f = 'VNCPage', vars = vncInfo)) 
                    
        return dict(form1=form1,form2=form2,num = j)
    elif(request.args(0) == 'edit'):   
        #Creamos el formulario de busqueda
        form1 = FORM(HR(),H2(T('Buscar una máquina')),DIV( T('Nombre de la máquina: '),BR(),INPUT(_name = 'vmName')),
            DIV( T('Usuario: '),BR(),INPUT(_name = 'userName')),
            DIV( T('Asignatura: '),BR(),INPUT(_name = 'subject')),
            INPUT(_type='submit',_class="button button-blue",_name = 'search',_value=T('Buscar')),HR()) 
        #Extraemos la lista de MV , si existe.
        vmListAux = request.vars.vmList or []
        if(isinstance(vmListAux,str)):
            vmList = [eval(request.vars.vmList)]
        else:
            vmList = []
            for l in vmListAux:
                vmList.append(eval(l))
        #Quitamos repeticiones
        finalVMList = []
        infoVMList = []
        for vm in vmList:
             if finalVMList.count(vm[0]) == 0:
                 finalVMList.append(vm[0])
                 infoVMList.append(vm)
        #Creamos el formulario de solucion
        vmNames = connector.getBootableImagesData(finalVMList)
        vmSelector = SELECT(_name = 'vms',_id= 'sId') 
        i=0
        for vmName in vmNames:
            vmSelector.append(OPTION(T(str(vmName["ImageName"])),_value = i ,_selected="selected"))
            i = i + 1 
        """  
        #Creamos el segundo formulario
        vmListAux = request.vars.vmList or []
        if(isinstance(vmListAux,str)):
            vmList = [eval(request.vars.vmList)]
        else:
            vmList = []
            for l in vmListAux:
                vmList.append(eval(l)) 
        """
        #Creamos el segundo formulario
        serversSelector = SELECT(_name = 'vms',_id= 'sId')
        servers = connector.getVMServersData()
        i = 0
        for s in servers:
                serversSelector.append(OPTION(T(str(s["VMServerName"])),_value = i ,_selected="selected"))
                i = i + 1
                
        form2 = FORM(LABEL(H2(T('Resultados'))),vmSelector,
               DIV(INPUT(_type='submit',_class="button button-blue",_name = 'deleteAll',_value=T('Eliminar del sistema'),
               _style="width:170px;")),
               DIV(INPUT(_type='submit',_class="button button-blue",_name = 'deployAll',_value=T('Desplegar automáticamente'),
               _style="width:230px;")),
               DIV(serversSelector,INPUT(_type='submit',_class="button button-blue",_name = 'deploy',_value=T('Desplegar en el servidor'),
               _style="width:190px;")))
        #Creamos el tercer y último formulario
        vmServerSelector = SELECT(_name = 'vms',_id= 'sId')
        vmDistribution = connector.getVMDistributionData()
        i = 0
        for vmDist in vmDistribution:
                if finalVMList.count(vmDist["ImageID"]) >= 1:
                    vmName =  connector.getBootableImagesData([vmDist["ImageID"]])[0]["ImageName"] 
                    vmServerSelector.append(OPTION(T("Máquina: ") + vmName + T(", Servidor: ") + vmDist["VMServerName"]
                        ,_value = i ,_selected="selected"))
                    i = i + 1 
        form3 = FORM(LABEL(H2(T('Eliminar máquina en servidor'))),vmServerSelector,
               DIV(INPUT(_type='submit',_class="button button-blue",_name = 'delete',_value=T('Eliminar del servidor'),
                   _style="width:170px;")))       
        #Actuamos frente a la busqueda
        if form1.accepts(request.vars,keepvalues=True) and form1.vars.search:
            listInfo = userDB((userDB.Subjects.code == userDB.ClassGroup.cod) & (userDB.UserGroup.cod == userDB.Subjects.code) & \
                    (userDB.UserGroup.curseGroup== userDB.ClassGroup.curseGroup) & (userDB.UserGroup.cod == userDB.VMByGroup.cod) & \
                    (userDB.UserGroup.curseGroup== userDB.VMByGroup.curseGroup) ).select(userDB.VMByGroup.VMId, \
                    userDB.ClassGroup.cod,userDB.ClassGroup.curseGroup,userDB.Subjects.name,userDB.UserGroup.userId)
            if len(form1.vars.subject) > 0 :
                listSubjects = []
                for l in listInfo :
                    if (form1.vars.subject.lower() in l.Subjects.name.lower()):                    
                        listSubjects.append(l)
                listInfo = listSubjects
            if len(form1.vars.userName) > 0 :
                listSubjects = []
                for l in listInfo :
                    if (form1.vars.userName.lower() in l.UserGroup.userId.lower()):                    
                        listSubjects.append(l)
                listInfo = listSubjects
            if len(form1.vars.vmName) > 0 :
                listSubjects = []
                
                for l in listInfo :
                    vmName = connector.getBootableImagesData([l.VMByGroup.VMId])[0]["ImageName"]
                    if (form1.vars.vmName.lower() in vmName.lower()):                    
                        listSubjects.append(l)
                listInfo = listSubjects
            #Creamos la lista final
            solutionList = []
            for l in listInfo :
                solutionList.append([l.VMByGroup.VMId,l.Subjects.name,l.ClassGroup.cod,l.ClassGroup.curseGroup,l.UserGroup.userId])
            print listInfo
            #redireccinamos con los resultados
            redirect(URL(c='administrator',f='runVM',args = ['edit'],vars = dict(vmList=solutionList) ))
        #Devolvemos el formulario             
        return dict(form1 = form1,form2=form2,form3=form3,num=0)
 
    else:
        #Creamos el formulario de busqueda
        form1 = FORM(HR(),H2(T('Buscar una máquina o usuario')),DIV( T('Nombre de la máquina: '),BR(),INPUT(_name = 'vmName')),
               DIV( T('Usuario: '),BR(),INPUT(_name = 'userName')),
               INPUT(_type='submit',_class="button button-blue",_name = 'search',_value=T('Buscar'),_onclick=[]),HR())    
        #Creamos el segundo formulario
        vmListAux = request.vars.vmList or []
        #Comprobamos si se ha tomado como una lista
            
        if(isinstance(vmListAux,str)):
            vmList = [eval(request.vars.vmList)]
        else:
            vmList = []
            for l in vmListAux:
                vmList.append(eval(l))
        table = TABLE(_class='data', _name='table')
        table.append(TR(TH('Selección'),TH(T('Máquina virtual'),TH(T('Usuario')),TH(T('Servidor')),TH(T('Puerto')))))
        j = 0
        for vm in vmList:  
                if(request.args(0) == 'stop'):          
                    table.append(TR(\
                    TD(INPUT(_type='radio',_name = 'selection',_value = vm[4],_id = "c"+str(j))),\
                    TD(LABEL(vm[0])),
                    TD(LABEL(vm[1])),
                    TD(LABEL(vm[2])),
                    TD(LABEL(vm[3])),
                    TD(DIV(INPUT(_type='submit',_name = 'stop',  _value = T('Detener'),_class="button button-blue")
                        ,_id = str(j)),_class='izquierda')))
                else:
                    table.append(TR(\
                    TD(INPUT(_type='radio',_name = 'selection',_value = vm[4],_id = "c"+str(j))),\
                    TD(LABEL(vm[0])),
                    TD(LABEL(vm[1])),
                    TD(LABEL(vm[2])),
                    TD(LABEL(vm[3])),
                    TD(DIV(INPUT(_type='submit',_name = 'open',  _value = T('Abrir'),_class="button button-blue")
                        ,_id = str(j)),_class='izquierda')))                    
                j = j + 1
        #Creamos el segundo formulario
        if(request.args(0) == 'stop'):
            form2 = FORM(LABEL(H2(T('Resultados'))),table)
        else:
            form2 = FORM(LABEL(H2(T('Resultados'))),table,_target='_blank')
            
        #Actuamos frente a la busqueda
        if form1.accepts(request.vars,keepvalues=True) and form1.vars.search:
            #Establecemos la conexión con el servidor 
            connector = conectToServer()
            #Extraemos la informacion
            vmListAux = connector.getActiveVMsData()
            print vmListAux
            #Inicializamos la lista de asignaturas
            vmList = [] 
            
            #Ejecutamos la busqueda
            for vm in vmListAux:
                #Extraemos el nombre de la máquina
                vmName = connector.getBootableImagesData([vm['VMID']])[0]["ImageName"]
                #Extraemos el nombre de usuario
                userName = userDB(userDB.auth_user.id == vm['UserID']).select(userDB.auth_user.email)
                #Comprobamos si añadimos este elemento a la lista resultado
                toAdd = True
                if((form1.vars.vmName != 0) and not ( form1.vars.vmName.lower() in vmName.lower())):
                    toAdd = False
                if((form1.vars.userName != 0) and not (form1.vars.userName.lower() in userName[0].email.lower())):
                    toAdd = False
                if(toAdd):
                    vmList.append([vmName,userName[0].email,vm['VMServerName'],vm['VNCPort'],vm['VMID']])
            if(request.args(0) == 'stop'):
                #redireccinamos con los resultados
                redirect(URL(c='administrator',f='runVM',args = ['stop'],vars = dict(vmList=vmList) ))
            else:
                redirect(URL(c='administrator',f='runVM',args = ['open'],vars = dict(vmList=vmList) )) 
        #Actuamos frente al arranque
        if(form2.accepts(request.vars)) and (form2.vars.stop):
               if(form2.vars.selection != ""):
                    #Establecemos la conexión con el servidor 
                    connector = conectToServer()
                    #Paramos la máquina virtual
                    print form2.vars.selection
                    commandId = connector.destroyDomain(form2.vars.selection)
                    #Esperamos la contestacion
                    errorInfo = connector.waitForCommandOutput(commandId)
                    if(errorInfo != None):
                        response.flash = T(errorInfo['ErrorMessage'])
                    else:
                        redirect(URL(f = 'runVM',args = ['stop']))
        if(form2.accepts(request.vars)) and (form2.vars.open):
             if(form2.vars.selection != ""):
                activeVMConectData = connector.getActiveVMsData(True,False)
                for vmInfo in activeVMConectData:
                    print form2.vars.selection
                    if vmInfo["VMID"] == int(form2.vars.selection):
                        serverIp = searchVMServerIp(connector.getVMServersData(), vmInfo["VMServerName"])
                        vncInfo = dict(OutputType=2,VNCServerIPAddress=serverIp,VNCServerPort=int(vmInfo["VNCPort"])+1
                                    ,VNCServerPassword=str(vmInfo["VNCPassword"]))
                if vncInfo != None:            
                    redirect(URL(c='vncClient', f = 'VNCPage', vars = vncInfo)) 
                                    
        return dict(form1=form1,form2=form2,num=j)         
@auth.requires_membership('Administrator')
def servers():
    createAdressBar()
    #Establecemos la conexión con el servidor principal
    connector = conectToServer()
    
    if(request.args(0) == 'add_servers'):
        #Creamos el primer formulario
        form = FORM(HR(),H2(T('Añadir un nuevo servidor')),DIV(T('Nombre: '),BR(),INPUT(_name = 'name',
                _style="width:63%;"),_style="position:absolute;left:10%;"),
                DIV( T('Dirección IP: '),BR(),INPUT(_name ='ipDir',_style="width:87%;"),_style="position:absolute;left:25%;"),
                DIV( T('Puerto: '),BR(),INPUT(_name ='port',_style="width:40%;"),_style="position:absolute;left:45%;"),
                DIV(BR(), T('Imagen base: '),INPUT(_type="checkbox",_name ='isVanilla',_style="width:30px;")
                ,_style="position:absolute;left:58%;"),BR(),BR(),
                DIV(HR(),CENTER(INPUT(_type='submit',_class="button button-blue",_name = 'add' ,_value=T('Añadir Servidor'),_style="width:150px;"))))                
        
        if form.accepts(request.vars,keepvalues=True) and form.vars.add:
            if(len(form.vars.name) > 0) and (len(form.vars.ipDir) > 0) and (len(form.vars.port) > 0):
                #Registramos el servidor
                try:                      
                       commandID = connector.registerVMServer(form.vars.ipDir,int(form.vars.port),form.vars.name,form.vars.isVanilla)
                       errorInfo = connector.waitForCommandOutput(commandID)
                       if(errorInfo != None):
                           response.flash = T(errorInfo['ErrorMessage'])
                       else:
                           #redireccinamos 
                           redirect(URL(c='administrator',f='servers',args = ['add_servers'] ))
                except ValueError:
                       response.flash = T('E puerto debe ser un entero.')
            
        #Devolvemos el formulario             
        return dict(form = form)
    elif(request.args(0) == 'remove_servers'): 
         
        infoServer = request.vars.info or ['No info','No info','No info','No info',False]
        print infoServer 

        i = 0
        select = SELECT(_name = 'server',_id= 'sId')
        servers = connector.getVMServersData()
        print "Servers: " + str(servers)
        for s in servers:
            select.append(OPTION(T(str(s["VMServerName"])),_value = i ,_selected="selected"))
            i = i + 1    
       
        buttons = DIV() 
        # Solo mostramos el botón de detener si hay una máquina seleccionada
        if(infoServer[0] != 'No info'):
            buttons.append(DIV(INPUT(_type='submit',_class="button button-blue",_name = 'change' ,_value=T('Aplicar cambios'),_style="width:170px;")
            ,_style="position:relative;left:20%;float:left;"))
            buttons.append(DIV(INPUT(_type='submit',_class="button button-blue",_name = 'remove' ,_value=T('Eliminar servidor'),_style="width:170px;"),_style="position:relative;left:25%;float:left;"))
          
        # Si no está arrancado, añadimos el botón de arrancar
        if(infoServer[3] == "Apagado"):
            buttons.append(DIV(INPUT(_type='submit',_class="button button-blue",_name = 'run' ,_value=T('Arrancar servidor'),_style="width:170px;")
            ,_style="position:relative;left:30%;float:left;"))

        form1 = FORM(DIV(DIV(H4(T('Servidores')),select),
        DIV(INPUT(_type='submit',_class="button button-blue",_name = 'search' ,_value=T('Buscar servidor'),_style="width:150px;")
        ),BR(),
        DIV( T('Nombre: '),BR(),INPUT(_name = 'name',_value=infoServer[0],_style="width:75%;"),_style="position:relative;float:left;"),
        DIV( T('Dirección IP: '),BR(),
        INPUT(_name='ip',_value=infoServer[1],_style="width:95%;"),_style="position:absolute;left:25%;float:left;"),
        DIV( T('Puerto: '),BR(),INPUT(_name ='port',_value=infoServer[2],_style="width:50%;"),_style="position:absolute;left:50%;float:left"),
        DIV(BR(), T('Imagen base: '),INPUT(_type="checkbox",_name ='isVanilla',_checked=infoServer[4],_style="width:30px;")
                ,_style="position:absolute;left:65%;"),BR(),_style="margin-bottom:100px;"),DIV(buttons,BR(),_style="margin-bottom:10px;"))           
        
        if form1.accepts(request.vars,keepvalues=True) and form1.vars.search:
            sInfo = connector.getVMServersData()[int(form1.vars.server)]
            print "Servers registrados:" + str(sInfo)
            redirect(URL(c='administrator',f='servers',args = ['remove_servers'],vars = dict(info = [sInfo["VMServerName"],\
            sInfo["VMServerIP"],sInfo["VMServerListenningPort"],sInfo["VMServerStatus"],sInfo["IsVanillaServer"],form1.vars.server]) ))
            
        if form1.accepts(request.vars,keepvalues=True) and form1.vars.remove: 
             #Damos de baja el servidor
             print infoServer[0] 
             commandID = connector.unregisterVMServer(infoServer[0],False)
             errorInfo = connector.waitForCommandOutput(commandID)
             if(errorInfo != None):
                 response.flash = T(errorInfo['ErrorMessage'])
             else:
                 redirect(URL(c='administrator',f='servers',args = ['remove_servers'] ))
        if form1.accepts(request.vars,keepvalues=True) and form1.vars.run:
            #Arrancamos el servidor
            commandID = connector.bootUpVMServer(infoServer[0])
            print infoServer[0]
            errorInfo = connector.waitForCommandOutput(commandID)
            if(errorInfo != None):
                response.flash = T(errorInfo['ErrorMessage'])  
            else:
                sInfo = connector.getVMServersData()[int(infoServer[5])]
                redirect(URL(c='administrator',f='servers',args = ['remove_servers'],vars = dict(info = [sInfo["VMServerName"],\
            sInfo["VMServerIP"],sInfo["VMServerListenningPort"],sInfo["VMServerStatus"],sInfo["IsVanillaServer"]]) ))
            
        if form1.accepts(request.vars,keepvalues=True) and form1.vars.change:
            #Arrancamos el servidor
            commandID = connector.changeVMServerConfiguration(infoServer[0],form1.vars.name,form1.vars.ip,form1.vars.port,form1.vars.isVanilla)
            errorInfo = connector.waitForCommandOutput(commandID)
            if(errorInfo != None):
                response.flash = T(errorInfo['ErrorMessage'])  
            else:
                sInfo = connector.getVMServersData()[int(infoServer[5])]
                redirect(URL(c='administrator',f='servers',args = ['remove_servers'],vars = dict(info = [sInfo["VMServerName"],\
                sInfo["VMServerIP"],sInfo["VMServerListenningPort"],sInfo["VMServerStatus"],sInfo["IsVanillaServer"]]) ))  
        return dict(form1= form1)   
    elif(request.args(0) == 'servers_state'):  
        select = SELECT(_name = 'server',_id= 'sId')
        servers = connector.getVMServersData()
        i=0
        for s in servers:
            select.append(OPTION(T(str(s["VMServerName"])),_value = i ,_selected="selected"))
            i = i + 1 
        form1 = FORM(H2("Estado de los servidores"),DIV(H4(T('Servidores')),select,
            INPUT(_type='submit',_class="button button-blue",_name = 'search' ,_value=T('Mostrar estado'),_style="width:150px;")))
        #Extraemos información de estado
        serverInfo = None
        if len(servers) > 0 :
            
            serverName = request.vars.serverName or servers[0]["VMServerName"]
            serverInfo = connector.getVirtualMachineServerStatus(serverName)
            print serverName
            if serverInfo != None:
                statePercentages=dict(RAMPercentage=100*serverInfo["RAMInUse"]/serverInfo["RAMSize"],
                                    diskPercentage=100*serverInfo["FreeStorageSpace"]/serverInfo["AvailableStorageSpace"],
                                    temporarySpacePercentage=100*serverInfo["FreeTemporarySpace"]/serverInfo["AvailableTemporarySpace"],
                                    CPUsPercentage=100*serverInfo["ActiveVCPUs"]/serverInfo["PhysicalCPUs"])
                
                table = TABLE(_class='state_table', _name='table')
                table.append(TR(TH(serverName,_class='izquierda state_table'),TH("Usado",_class='state_table'),TH("Total",_class='state_table')))
                table.append(TR(TD("Maquinas activas",_class='izquierda state_table')
                    ,TD(serverInfo["ActiveHosts"],_class='state_table'),TD("",_class='state_table')))
                table.append(TR(TD("Memoria RAM",_class='izquierda state_table')
                    ,TD(str(serverInfo["RAMInUse"]/1024)+ "MB",_class='state_table')
                    ,TD(str(serverInfo["RAMSize"]/1024)+ "MB",_class='state_table')))
                table.append(TR(TD("Espacio en disco",_class='izquierda state_table')
                    ,TD(str((serverInfo["AvailableStorageSpace"]-serverInfo["FreeStorageSpace"])/1024)+ "MB",_class='state_table')
                    ,TD(str(serverInfo["AvailableStorageSpace"]/1024)+ "MB",_class='state_table')))
                table.append(TR(TD("Espacio temporal",_class='izquierda state_table')
                    ,TD(str((serverInfo["AvailableTemporarySpace"]-serverInfo["FreeTemporarySpace"])/1024)+ "MB",_class='state_table')
                    ,TD(str(serverInfo["AvailableTemporarySpace"]/1024)+ "MB",_class='state_table'))) 
                table.append(TR(TD("Número de CPUs",_class='izquierda state_table'),TD(serverInfo["ActiveVCPUs"],_class='state_table')
                    ,TD(serverInfo["PhysicalCPUs"],_class='state_table')))
            
        if serverInfo == None:
                statePercentages=dict(RAMPercentage=0,
                                    diskPercentage=0,
                                    temporarySpacePercentage=0,
                                    CPUsPercentage=0)
                table = TABLE(_class='state_table', _name='table')
                table.append(TR(TH(serverName,_class='izquierda state_table'),TH("Usado",_class='state_table'),TH("Total",_class='state_table')))
                table.append(TR(TD("Maquinas activas",_class='izquierda state_table'),TD("0",_class='state_table'),TD("",_class='state_table')))
                table.append(TR(TD("Memoria RAM",_class='izquierda state_table'),TD("0",_class='state_table'),TD("0",_class='state_table')))
                table.append(TR(TD("Espacio en disco",_class='izquierda state_table'),TD("0",_class='state_table'),TD("0",_class='state_table')))
                table.append(TR(TD("Espacio temporal",_class='izquierda state_table'),TD("0",_class='state_table'),TD("0",_class='state_table'))) 
                table.append(TR(TD("Número de CPUs",_class='izquierda state_table'),TD("0",_class='state_table'),TD("0",_class='state_table')))                            
        
        #Formulario con la tabla
        form2 = FORM(table) 
        
        #Extraemos información del repositorio
        repositoryInfo = connector.getImageRepositoryStatus()
        if repositoryInfo != None:
            repoStatePercentage=dict(diskPercentage=100*repositoryInfo["FreeDiskSpace"]/repositoryInfo["AvailableDiskSpace"])
            repoTable = TABLE(_class='state_table', _name='table')
            repoTable.append(TR(TH("Repositorio",_class='izquierda state_table')
                    ,TH("Usado",_class='state_table'),TH("Total",_class='state_table')))
            repoTable.append(TR(TD("Estado",_class='izquierda state_table')
                    ,TD(repositoryInfo["RepositoryStatus"],_class='state_table'),TD("",_class='state_table')))
            repoTable.append(TR(TD("Espacio en disco",_class='izquierda state_table')
                    ,TD(str((repositoryInfo["AvailableDiskSpace"]-repositoryInfo["FreeDiskSpace"])/1024)+ "MB",_class='state_table')
                    ,TD(str(repositoryInfo["AvailableDiskSpace"]/1024)+ "MB",_class='state_table')))
        else:
            repoStatePercentage=dict(diskPercentage=0)
            repoTable = TABLE(_class='state_table', _name='table')
            repoTable.append(TR(TH("Repositorio",_class='izquierda state_table')
                    ,TH("Usado",_class='state_table'),TH("Total",_class='state_table')))
            repoTable.append(TR(TD("Estado",_class='izquierda state_table')
                    ,TD("No encontrado",_class='state_table'),TD("",_class='state_table')))
            repoTable.append(TR(TD("Espacio en disco",_class='izquierda state_table')
                    ,TD(str(0)+ "MB",_class='state_table')
                    ,TD(str(0)+ "MB",_class='state_table')))                        
        form3=FORM(repoTable)
        #Comprobamos si se ha pulsado en buscar
        if form1.accepts(request.vars,keepvalues=True) and form1.vars.search:
            if form1.vars.server:
                redirect(URL(c='administrator',f='servers',args = ['servers_state']
                         ,vars = dict(serverName=servers[int(form1.vars.server)]["VMServerName"]))) 
                     
        return dict(form1 = form1,form2=form2,form3=form3,statePercentages = statePercentages,repoStatePercentage=repoStatePercentage) 
        
    elif(request.args(0) == 'stop_system'):
        #Creamos el primer formulario
        form = FORM(HR(),H2(T('Parar infraestructura')),             
                CENTER(DIV( T('Forzar detención de máquinas virtuales: '
                    ),INPUT(_type="checkbox",_name ='stopVMs',_style="width:30px;"))),
                DIV(CENTER(INPUT(_type='submit',_class="button button-red",_name = 'stopSystem' ,_value=T('Detener infraestructura'),_style="width:220px;height:40px;font-size:16px;-moz-border-radius: .8em;border-radius: .8em;")))
                ) 
        btn = form.element("input",_type="submit")
        btn["_onclick"] = "return confirm('¿Esta seguro que desea detener la infraestructura?');"                                   
        if form.accepts(request.vars,keepvalues=True) and form.vars.stopSystem:
                    connector.shutDownInfrastructure(form.vars.stopVM=="on")
        return dict(form = form)


      
@auth.requires_membership('Administrator')
def users():  
    createAdressBar()
    if(request.args(0) == 'add'):
        #Creamos el primer formulario
        form = FORM(HR(),H2(T('Añadir un nuevo usuario')),DIV( T('Nombre: '),BR(),INPUT(_name = 'name')),
                DIV( T('Contraseña: '),BR(),INPUT(_name ='password')),
                DIV(T('Grupo: '),BR(),SELECT(_name = 'group',*[OPTION(T(str(row.role)),_value = row.role,_selected="selected") 
                for row in userDB().select(userDB.auth_group.role)])),HR(),CENTER(INPUT(_type='submit',_class="button button-blue",_name = 'add' ,_value=T('Añadir Usuario'),_style="width:130px")))                
        
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
              INPUT(_name ='classGroup')),INPUT(_type = 'submit',_class="button button-blue",_name = 'add',_value = T('Añadir')),
              INPUT(_type="submit",_class="button button-blue",_name = 'remove',_value=T("Eliminar")))
        #Acción según el botón pulsado
        if form2.accepts(request.vars,keepvalues=True) and form2.vars.add:
           if(len(form2.vars.code) >= 3) and (len(form2.vars.classGroup) == 1): 
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
        form2 = FORM(table,CENTER(INPUT(_type = 'submit',_class="button button-blue",_name = 'remove',  _value = T('Eliminar seleccionado'),_style="width:170px")))
        
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
        form = FORM(HR(),H2(T('Añadir un nueva asignatura')),DIV( T('Código: '),BR(),INPUT(_name = 'cod',_style="width:30%;"),_style="position:absolute;left:10%;"),
                DIV( T('Nombre: '),BR(),INPUT(_name ='name'),_style="position:absolute;left:18%;"),BR(),BR(),BR(),
                DIV( T('Año: '),BR(),INPUT(_name ='year',_style="width:35%;"),_style="position:absolute;left:10%;"),
                DIV( T('Curso: '),BR(),INPUT(_name ='curse',_style="width:29%;"),_style="position:absolute;left:20%;"),
                DIV( T('Grupo: '),BR(),INPUT(_name ='group',_style="width:10%;"),_style="position:absolute;left:28%;"),BR(),BR(),BR(),
                HR(),CENTER(INPUT(_type='submit',_class="button button-blue",_name = 'add' ,_value=T('Añadir'))))                
        
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
        form2 = FORM(table,CENTER(INPUT(_type = 'submit',_class="button button-blue",_name = 'remove',  _value = T('Eliminar seleccionado'),_style="width:170px;")))
        
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
              INPUT(_name ='classGroup')),INPUT(_type = 'submit',_class="button button-blue",_name = 'add',_value = T('Añadir')),
              INPUT(_type="submit",_class="button button-blue",_name = 'remove',_value=T("Eliminar")))
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
 
    response.menu=[[SPAN(T('Máquinas virtuales'), _class='highlighted'), False,URL(f ='runVM',args = ['run']),[
                        (T('Arrancar'),False,URL(f = 'runVM',args = ['run'])),
                        (T('Detener'),False,URL(f = 'runVM',args = ['stop'])),
                        (T('Abrir'),False,URL(f = 'runVM',args = ['open'])),
                        (T('Editar'),False,URL(f = 'runVM',args = ['edit']))]],
                    [SPAN(T('Administrar servidores'), _class='highlighted'), False, URL(f = 'servers',args = ['add_servers']),[
                        (T('Añadir servidor'),False,URL(f = 'servers',args = ['add_servers'])),
                        (T('Editar servidor'),False,URL(f = 'servers',args = ['remove_servers'])),
                        (T('Estado del sistema'),False,URL(f = 'servers',args = ['servers_state'])),
                        (T('Parar infraestructura'),False,URL(f = 'servers',args = ['stop_system']))]],
                    [SPAN(T('Administrar usuarios'), _class='highlighted'), False, URL(f = 'users',args = ['add']),[
                        (T('Eliminar'),False,URL(f = 'users',args = ['remove'])),
                        (T('Añadir'),False,URL(f = 'users',args = ['add'])),
                        (T('Asociar asignaturas'),False,URL(f = 'users',args = ['associate_subjects']))]],
                    [SPAN(T('Administrar asignaturas'), _class='highlighted'), False, URL(f = 'subjects',args = ['add']),[
                       (T('Añadir'),False,URL(f = 'subjects',args = ['add'])),
                       (T('Eliminar'),False,URL(f = 'subjects',args = ['remove']))]]]
                       
def createUserSearchForm(state):        
    listTypes = []
    listTypes.append(OPTION(T('Todos'),_value = 'all'))
    for row in userDB().select(userDB.auth_group.role):
        listTypes.append(OPTION(T(str(row.role)),_value = row.role )) 
        
    form1 = FORM(HR(),H2(T('Buscar un usuario')),DIV( T('Nombre: '),BR(),INPUT(_name = 'name')),
           DIV(T('Grupo: '),BR(),SELECT(_name = 'group', *listTypes)),
           INPUT(_type='submit',_class="button button-blue",_name = 'search',_value=T('Buscar'),_onclick=[]),HR())    
    
    if form1.accepts(request.vars,keepvalues=True) and form1.vars.search:
        query = ""
        if(form1.vars.group != 'all'):
            query =  (userDB.auth_group.role  ==  form1.vars.group) & (userDB.auth_group.id == userDB.auth_membership.group_id) 
            query &= userDB.auth_membership.user_id  ==  userDB.auth_user.id
                
        rows = userDB(query).select(userDB.auth_user.email)

        #Extraemos la lista de usuarios 
        listUsersAux = [] 
        for row in rows :                  
            if(form1.vars.name != "") and (form1.vars.name != None):
                    if (form1.vars.name.lower() in row.email.lower()):                    
                        listUsersAux.append(row.email)
            else:
                    listUsersAux.append(row.email)
        #redireccinamos con los resultados
        redirect(URL(c='administrator',f='users',args = [state],vars = dict(usersFind=listUsersAux) ))
     
    return form1
    
def createSubjectsSearchForm(state):        

        
    form1 = FORM(HR(),H2(T('Buscar una asignatura')),DIV( T('Código: '),BR(),INPUT(_name = 'cod',_style="width:40%;"),_style="position:absolute;left:10%;"),
                DIV( T('Nombre: '),BR(),INPUT(_name ='name'),_style="position:absolute;left:20%;"),BR(),BR(),BR(),
                DIV( T('Año: '),BR(),INPUT(_name ='year',_style="width:25%;"),_style="position:absolute;left:10%;"),
                DIV( T('Curso: '),BR(),INPUT(_name ='curse',_style="width:15%;"),_style="position:absolute;left:18%;"),
                DIV( T('Grupo: '),BR(),INPUT(_name ='group',_style="width:15%;"),_style="position:absolute;left:24%;"),BR(),BR(),BR(),
                INPUT(_type='submit',_class="button button-blue",_name = 'search',_value=T('Buscar'),_onclick=[]),HR())    
    
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
                    add = form1.vars.name.lower() in userDB(row.cod == userDB.Subjects.code).select()[0].name.lower() 
            if(form1.vars.cod != "") and (add):
                    add = form1.vars.cod in str(row.cod)                    
            if(add):
                    listSubjectsAux.append([row.cod,row.curseGroup])
        #redireccinamos con los resultados
        redirect(URL(c='administrator',f='subjects',args = [state],vars = dict(subjectsFind=listSubjectsAux) ))
     
    return form1


def createUserTable(listUsers):
    table = TABLE(_class='data', _name='table')
    table.append(TR(TH('Selección'),TH(T('Nombre')), TH(T('Grupo'))))
    i = 0
    for l in listUsers:
        table.append(TR(\
        TD(INPUT(_type='radio',_name = 'selection',_value = i)),\
        TD(LABEL(l)),\
        TD(LABEL(userDB((userDB.auth_user.email==l) & (userDB.auth_membership.user_id == userDB.auth_user.id) \
         & (userDB.auth_membership.group_id == userDB.auth_group.id)).select(userDB.auth_group.role)[0].role))))
        i = i + 1
    pass
    return table
    
def createSubjectTable(listSubjects):
    table = TABLE(_class='data', _name='table')
    table.append(TR(TH('Selección'),TH(T('Cod-Asignatura'),_class='izquierda'),TH(T('Grupo'))))
    i = 0
    for l in listSubjects:
        table.append(TR(\
        TD(INPUT(_type='radio',_name = 'selection',_value = i)),\
        TD(LABEL(str(l[0]) + '-' + userDB(l[0] == userDB.Subjects.code).select()[0].name),_width = '50%',_class='izquierda'),
        TD(LABEL(l[1]))))
        i = i + 1
    pass
    return table
    
    
def conectToServer():
    #Establecemos la conexión con el servidor principal
    connector = ClusterConnector(auth.user_id)
    connector.connectToDatabases(dbStatusName,commandsDBName,webUserName, webUserPass)
    return connector
    
def searchVMServerIp(servers, serverName):
    for s in servers:
        if s["VMServerName"] == serverName:
            return s["VMServerIP"]
    return None
