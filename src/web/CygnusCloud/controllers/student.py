# coding: utf8
from gluon import *

#Método encargado de manejar la página de arranque de máquinas para el usuario
@auth.requires_membership('Student')
def runVM():
    #actualizamos la barra
    createAdressBar()
    #Creamos el formulario
    print request.vars.actualDescription
    listSubjects = userDB((userDB.UserGroup.userId == auth.user['email'])).select(userDB.UserGroup.cod,userDB.UserGroup.curseGroup)
    
    tables = []
    for l in listSubjects:
        tables.append(createTable(l))
    #Creamos el formulario
    form = FORM(HR())
    i = 0
    divMaquinas = DIV(_id='maquinas')
    for table in tables:
        
        divMaquinas.append(DIV(H4(T(userDB(userDB.Subjects.code == listSubjects[i].cod).select(userDB.Subjects.name)[0].name)),BR(),H5(table),BR()))
        
    form.append(divMaquinas)
    form.append(DIV(H4(T('Descripcion:')), P(_id = 'newInfo'), INPUT(_type='submit',_name = 'run',  _value = T('Arrancar')), _id = 'descripcion'))
    
    if(form.accepts(request.vars)) and (form.vars.run):
            if(form.vars.selection != ""):
                #TODO: Configurar cliente VNC...
                #Abrimos una nueva pestaña
                form.append(DIV(T('Máquina arrancada disponible aquí: '),A(eval(form.vars.selection)[0], 
                _href=URL(c='vncClient', f = 'VNCPage'), _target='_blank',_select = 'selected'), _id = 'maquina'))
    return dict(form = form)
       
   
def createAdressBar():
    response.menu=[[T('Arrancar máquina'),False,URL('runVM')]]
    
def createTable(subject):
    table = TABLE(_class='data', _name='table')
    table.append(TR(TH('S.'),TH(T('Nombre'))))
    i = 0
    for l in userDB((userDB.VMByGroup.cod == subject.cod) & (userDB.VMByGroup.curseGroup == subject.curseGroup) & \
        (userDB.Images.VMId == userDB.VMByGroup.VMId)).select(userDB.Images.name):
        table.append(TR(\
        TD(INPUT(_type='radio',_name = 'selection',_value = [subject.cod , subject.curseGroup, i], _onclick = "ajax('selectRadioButton', ['selection'], 'newInfo')")),\
        TD(LABEL(l.name))))
        i = i + 1
    pass
    return table

def selectRadioButton():
    #Extraemos la descripcion actual
    descriptionAct = userDB((userDB.VMByGroup.cod == eval(request.vars.selection)[0]) & \
         (userDB.VMByGroup.curseGroup == eval(request.vars.selection)[1]) & \
        (userDB.Images.VMId == userDB.VMByGroup.VMId)).select(userDB.Images.description)[eval(request.vars.selection)[2]].description
    return descriptionAct
