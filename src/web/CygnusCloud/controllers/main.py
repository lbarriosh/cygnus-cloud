# coding: utf8
# Método encargado de la página de inicio de sesión
def login(): 
    createAdressBar()
    auth.settings.login_onaccept = loginAccess
    #auth.settings.login_next = URL(c='main',f='login')  
    return dict(form=auth.login())
    
def createAdressBar():
    response.menu=[[T('Iniciar sesión'),False,URL('login')],
                   [T('Acerca de'),False,URL('login')]]
                   
def loginAccess(state):
    if(userDB(userDB.auth_membership.user_id == request.vars.id).select()[0].group_id == 'Student'):
        redirect(URL(c='student',f='runVM'))
    else:
        redirect(URL(c='administrator',f='runVM'))
