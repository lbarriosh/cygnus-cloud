# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: codesTranslator.py    
    Version: 3.0
    Description: codes translator interface
    
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
class CodesTranslator(object):
    """
    This abstract class defines the interface common to all the codes translators
    """
    def processVMServerSegment(self, data):
        """
        Translates the codes included on a virtual machine server configuration
        segment.
        Args:
            data: the segment to process
        Returns:
            the processed segment
        """
        raise NotImplementedError
    
    def processImageCopiesDistributionSegment(self, data):
        """
        Translates the codes included on an image copies status 
        segment.
        Args:
            data: the segment to process
        Returns:
            the processed segment
        """
        raise NotImplementedError
    
    def translateRepositoryStatusCode(self, code):
        """
        Translates an image repository error code
        Args:
            the code to be translated
        Returns:
            a string containing the code's translation
        """
        raise NotImplementedError
    
    def translateErrorDescriptionCode(self, code):
        """
        Translates an error description code
        Args:
            the code to be translated
        Returns:
            a string containing the code's translation
        """
        raise NotImplementedError
    
    def translateNotificationCode(self, code):
        """
        Translates a notification code
        Args:
            the code to be translated
        Returns:
            a string containing the code's translation
        """
        raise NotImplementedError