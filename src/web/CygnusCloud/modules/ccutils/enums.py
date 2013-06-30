# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: enums.py    
    Version: 1.0
    Description: enum types syntax extension
    
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

def enum(*sequence):
    """
    This function extends Python's syntax in order to handle enum types. 
    The integer values assigned to the enum constants will be generated automatically.    
    Args:
        sequence: a list of values
    Returns:
        an Enum object that represents the enum type. 
        For example, if it has the values A and B, <Enum Object>.A returns the
        integer value associated with the A enum constant.         
        @attention: The attribute reverse_mapping returns the enum constant
        assigned to an integer.
    """
    values = dict(zip(sequence, range(len(sequence))))
    reverse_values = dict((value, key) for key, value in values.iteritems())
    values['reverse_mapping'] = reverse_values
    return type('Enum', (), values)