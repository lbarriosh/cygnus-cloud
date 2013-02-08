def translate():
    return "jQuery(document).ready(function(){jQuery('body').translate('%s');});" % request.args(0).split('.')[0]
    
    
def changeLanguage():
    session._language = request.args[0]
    #T.force(request.args[0])
    #T.set_current_languages(str(request.args[0]),str(request.args[0]) + '-' +  str(request.args[0]))
    if(len(request.args) == 5):
        redirect(URL(request.args[1],request.args[2], request.args[3],args=(request.args[4])))
    else:
        redirect(URL(request.args[1],request.args[2], request.args[3]))
    return
