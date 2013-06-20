'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
   
    File: vncClient.py   
    Version: 1.0
    Description: vnc client page controller
   
    Copyright 2012-13 Luis Barrios Hernández, Adrián Fernández Hernández, 
                      Samuel Guayerbas Martín

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

'''
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
