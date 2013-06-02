# coding: utf8
def VNCPage():
    print request.controller
    #Devolvemos la información
    if (request.vars.has_key('ErrorMessage')):
        return dict(error = True,errorMessage=request.vars['ErrorMessage'])
    else:
        print request.vars.VNCServerIPAddress
        print request.vars.VNCServerPort
        print request.vars.VNCServerPassword
        print len(request.vars.VNCServerPassword)
        return dict(error = False,ip=request.vars.VNCServerIPAddress,port = request.vars.VNCServerPort,password = request.vars.VNCServerPassword)
