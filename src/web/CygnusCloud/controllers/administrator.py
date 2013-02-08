# coding: utf8
@auth.requires_membership('Administrator')
def runVM():
    createAdressBar()
    return dict()
    
@auth.requires_membership('Administrator')
def servers():
    createAdressBar()
    if(request.args(0) == 'add_remove_servers'):
        form = FORM(T('Servidores'),SELECT('server1','server 2'))
        return dict(form = form)
        
@auth.requires_membership('Administrator')
def users():
    createAdressBar()
    if(request.args(0) == 'add'):
        #Creamos el primer formulario
        form1 = FORM(H2(T('Añadir un nuevo usuario')),DIV(DIV( T('Nombre: '),BR(),INPUT(_name = 'name')),DIV( T('Contraseña: '),BR(),INPUT(_name ='password')),_class = "control-group"),
                DIV(T('Grupo: '),BR(),SELECT(_name = 'group',*[OPTION(row.role,_value = T(str(row.role))) for row in userDB().select(userDB.auth_group.role)])))
                
        return dict(form1 = form1)
    
    
def createAdressBar():
    response.menu=[[SPAN(T('Arrancar máquina'), _class='highlighted'), False,URL('runVM'),[]],
                    [SPAN(T('Administrar servidores'), _class='highlighted'), False, URL(f = 'servers',args = ['add_remove_servers']),[
                        (T('Añadir/Eliminar'),False,URL(f = 'servers',args = ['add_remove_servers']))]],
                    [SPAN(T('Administrar usuarios'), _class='highlighted'), False, URL(f = 'users',args = ['remove']),[
                        (T('Eliminar'),False,URL(f = 'users',args = ['remove'])),
                        (T('Añadir'),False,URL(f = 'users',args = ['add']))]],
                    [SPAN(T('Administrar asignaturas'), _class='highlighted'), False, URL(f = 'subjects',args = ['add']),[
                       (T('Añadir'),False,URL(f = 'subjects',args = ['add'])),
                       (T('Eliminar'),False,URL(f = 'subjects',args = ['remove'])),
                       (T('Admistrar máquinas'),False,URL(f = 'subjects',args = ['addVM']))]]]
