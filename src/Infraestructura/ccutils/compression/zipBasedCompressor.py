# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: zipBasedCompressor.py    
    Version: 3.0
    Description: zip-based compressor definitions
    
    Copyright 2012-13 Luis Barrios Hernández, Samuel Guayerbas Martín

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

from ccutils.processes.childProcessManager import ChildProcessManager

class ZipBasedCompressor():
    '''
    This class creates and extracts zip files by calling the zip and 
    unzip commands.
    '''
    
    def createCompressedFile(self, filePath, fileNameList):
        '''
        Generates a .zip file.
        Args:
            filePath: the new .zip file path
            fileNameList: the files that will be added to the .zip file.
        Returns:
            Nothing
        '''
        args = filePath + " "
        for fileName in fileNameList :
            args += fileName + " "
        try :
            ChildProcessManager.runCommandInForeground("zip -j " + args, Exception)
        except Exception as e:
            if ("Nothing to do" in e.message) :
                pass
            else :
                raise e

    def extractFile(self, path, outputDirectory):
        '''
        Extracts a .zip file.
        Args:
            path: the .zip file path to extract
            outputDirectory: the directory where the .zip file content will be extracted.
        Returns:
            Nothing
        '''
        if (outputDirectory == None) :
            outputDirectory = path.dirname(path)
        ChildProcessManager.runCommandInForeground("unzip " + path + " -d " + outputDirectory, Exception)