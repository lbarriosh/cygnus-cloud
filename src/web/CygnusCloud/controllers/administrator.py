# coding: utf8
def runVM():
    createAdressBar()
    return dict()
def servers():
    createAdressBar()
    if(request.args(0) == 'add_remove_servers'):
        menu = createServersBar()
        form = FORM(T('Servidores'),SELECT('server1','server 2'))
        return dict(form = form,menu = menu)
    
def createAdressBar():
    response.menu=[[T('Arrancar máquina'),False,URL('runVM')],[T('Administrar servidores'),False,URL(f = 'servers',args = ['add_remove_servers'])],
                    [T('Administrar usuarios'),False,URL('users')],[T('Administrar asignaturas'),False,URL('subjects')]]
                    
                   
def createServersBar():
    menu = MENU([[T('Añadir/Eliminar'),False,URL(f = 'servers',args = ['add_remove_servers'])],[T('Añadir/Eliminar'),False,URL(f = 'servers',args = ['add_remove_servers'])]], _class = 'web2py-menu web2py-menu-horizontal')
    return menu
