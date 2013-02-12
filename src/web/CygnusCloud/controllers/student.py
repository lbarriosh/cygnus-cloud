# coding: utf8

#Método encargado de manejar la página de arranque de máquinas para el usuario
@auth.requires_membership('Student')
def runVM():
    #actualizamos la barra
    createAdressBar()
    #Creamos el formulario
    print auth.user['email']
    listSubjects = userDB((userDB.UserGroup.userId == auth.user['email'])).select(userDB.UserGroup.cod,userDB.UserGroup.curseGroup)
    
    tables = []
    for l in listSubjects:
        tables.append(createTable(l))
    #Creamos el formulario
    form = FORM(HR())
    i = 0
    for table in tables:
        
        form.append(DIV(H3(T(userDB(userDB.Subjects.code == listSubjects[i].cod).select(userDB.Subjects.name)[0].name)),BR(),CENTER(table),BR()))
    form.append(DIV(CENTER(INPUT(_type='submit',_name = 'run',  _value = T('Arrancar'))),CENTER(H3(T('Descripcion:')))))
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
        TD(INPUT(_type='radio',_name = 'selection',_value = i)),\
        TD(LABEL(l.name))))
        i = i + 1
    pass
    return table
