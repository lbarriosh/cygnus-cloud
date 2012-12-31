# -*- coding: utf8 -*-
"""
This module contains all the packet-related definitions.
@author: Luis Barrios Hernández
@version: 1.0
"""

from utils.enums import enum
from network.exceptions.packetException import PacketException

Packet_TYPE = enum('TICK', 'DATA')

class Packet(object):
    """
    A class that stands for a packet
    @attention: Packet instances MUST ONLY be created through a NetworkManager
    to avoid priority issues. That issues can cause serious errors in the network
    subsystem.
    """
    def __init__(self, packetType, priority):
        """
        Creates an empty packet with the type and priority given as arguments
        """
        self.__priority = priority
        self.__packetType = packetType
        self.__data = ''
        
    def writeInt(self, value):
        """
        Writes an integer value into the packet
        """
        self.__commonWriteCode(value, int, "int", True)
        
    def writeLong(self, value):
        """
        Writes a long integer value into the packet
        """
        try :
            self.__commonWriteCode(value, long, "long", True)
        except PacketException as e:
            if isinstance(value, int) :
                self.__commonWriteCode(value, long, "long", False)
            else : raise e
        
    def writeString(self, value):
        """
        Writes a string into the packet
        """
        if not isinstance(value, str):
            raise PacketException("The given value is not an " + self.__extractTypeName(str) + " instance")
        if '·' in value :
            raise PacketException('Strings cannot contain the \'·\' character')
        self.__commonWriteCode(value, str, "string", False)       
  
    
    def writeFloat(self, value):
        """
        Writes a float value into the packet
        """
        self.__commonWriteCode(value, float, "float", True)
        
    def writeBool(self, value):
        """
        Writes a boolean value into the packet
        """
        self.__commonWriteCode(value, bool, "bool", True)
        
    def __eq__(self, other):
        if isinstance(other, Packet):
            return (self.__priority == other.__priority) and (self.__packetType == other.__packetType) \
                and (self.__data == other.__data)
        else: 
            return False
        
    def __extractTypeName(self, dataType):
        (head, center, dataTypeStr)  = str(dataType).partition("\'")
        (dataTypeStr, center, tail) = dataTypeStr.partition("\'")
        return dataTypeStr
    
    def __commonWriteCode(self, value, dataType, field, checkType):
        """
        Code shared by all write opperations
        """
        if checkType and not isinstance(value, dataType):            
            raise PacketException("The given value is not an " + self.__extractTypeName(str(dataType)) + " instance")
        dataToAdd = str(value)
        newLength = len(self.__data) + len(field) + len(dataToAdd) + 2
        if (newLength > 16000):
            raise PacketException("There\'s not enough space to hold a " + self.__extractTypeName(str(dataType))\
                                   + " value")
        self.__data.join(field)
        self.__data.join('·' + dataToAdd + '·')
        
