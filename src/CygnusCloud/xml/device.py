'''
Created on Jan 10, 2013

@author: luis
'''

from utils.enums import enum

DEVICE_TYPE = enum("IDE_DISK", "CD_ROM", "HARD_DISK")

class Device(object):
    def __init__(self, type):
        self.__type = type
        
        
        