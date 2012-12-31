# -*- coding: utf8 -*-
'''
A module with functions that generate enum types
@author: Luis Barrios Hernández
@version:  1.0
'''

def enum(*sequence):
    """
    A function that generates an enum type using its arguments. 
    @attention: The integer values assigned to the enum constants 
    will be generated automatically.    
    @attention: The attribute reverse_mapping returns the enum constant
    assigned to an integer.
    """
    values = dict(zip(sequence, range(len(sequence))))
    reverse_values = dict((value, key) for key, value in values.iteritems())
    values['reverse_mapping'] = reverse_values
    return type('Enum', (), values)


if __name__ == '__main__':
    Days = enum('MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY')
    print Days.WEDNESDAY
    print Days.reverse_mapping[2]