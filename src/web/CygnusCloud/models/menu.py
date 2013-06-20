'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
   
    File: menu.py   
    Version: 2.0
    Description: some web utilities definitions
   
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

# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

response.logo = A(IMG(src=URL('static','images/favicon.png'),_alt="My Logo"),XML('&trade;&nbsp;'),
                  _class="brand",_href=URL('main','about'))
response.title = ' '.join(
    word.capitalize() for word in request.application.split('_'))
response.subtitle = T('customize me!')

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Your Name <you@example.com>'
response.meta.description = 'a cool new app'
response.meta.keywords = 'web2py, python, framework'
response.meta.generator = 'Web2py Web Framework'

## your http://google.com/analytics id
response.google_analytics_id = None

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################


DEVELOPMENT_MENU = True

#########################################################################
## provide shortcuts for development. remove in production
#########################################################################

def _():

    # shortcuts
    app = request.application
    ctr = request.controller
        
if DEVELOPMENT_MENU: _()
