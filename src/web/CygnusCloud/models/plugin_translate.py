#Barra de idiomas
plugin_translate_current_language = 'es'

session._language = request.vars._language or session._language or plugin_translate_current_language
T.force(session._language)
if T.accepted_language != session._language:
    import re
    lang = re.compile('\w{2}').findall(session._language)[0]
    response.files.append(URL(r=request,c='static',f='plugin_translate/jquery.translate-1.4.3-debug-all.js'))
    response.files.append(URL(r=request,c='plugin_translate',f='translate',args=lang+'.js'))

def plugin_translate():
    return FORM(T('Languages:'),A(IMG(_src=URL('static','spain'),_alt = 'spain'),_href = URL(r=request,c='plugin_translate',f='changeLanguage',args = ('es',request.application,request.controller,request.function))),
                       A(IMG(_src=URL('static','england'),_alt = 'england'),_href = URL(r=request,c='plugin_translate',f='changeLanguage',args = ('en',request.application,request.controller,request.function))),
                       A(IMG(_src=URL('static','france'),_alt = 'france'),_href = URL(r=request,c='plugin_translate',f='changeLanguage',args = ('fr',request.application,request.controller,request.function))),
                       A(IMG(_src=URL('static','german'),_alt = 'german'),_href = URL(r=request,c='plugin_translate',f='changeLanguage',args = ('nl',request.application,request.controller,request.function))),
                       A(IMG(_src=URL('static','portugal'),_alt = 'portugal'),_href = URL(r=request,c='plugin_translate',f='changeLanguage',args = ('po',request.application,request.controller,request.function))),
                       A(IMG(_src=URL('static','italy'),_alt = 'italy'),_href = URL(r=request,c='plugin_translate',f='changeLanguage',args = ('it',request.application,request.controller,request.function))),
                       value=session._language)
                       
                       
def changeLanguage(lang):
    #T.set_current_languages(lang)
    redirect(URL('deafult','index'))
    #redirect(URL(r=request,args=request.args))
