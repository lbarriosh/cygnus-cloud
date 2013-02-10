# -*- coding: UTF8 -*-
'''
Web status database writer

@author: Luis Barrios Hernández
@version: 1.0
'''

from database.utils.connector import BasicDatabaseConnector

class SystemStatusDatabaseWriter(BasicDatabaseConnector):
    def __init__(self, sqlUser, sqlPassword, databaseName):
        BasicDatabaseConnector.__init__(self, sqlUser, sqlPassword, databaseName)
        self.__vmServerSegments = []
        self.__imageSegments = []
        
    def processVMServerSegment(self, segmentNumber, segmentCount, data):
        self.__vmServerSegments.append(data)
        if (len(self.__vmServerSegments) == segmentCount) :
            # Write changes to the database
            command = "DELETE FROM VirtualMachineServer;"
            self._executeUpdate(command)
            command = "INSERT INTO VirtualMachineServer VALUES " + SystemStatusDatabaseWriter.__segmentsToStr(self.__vmServerSegments)
            self.__vmServerSegments = []            
            self._executeUpdate(command)
                        
    @staticmethod
    def __segmentsToStr(segmentList):
        isFirstSegment = True
        command = ""
        for segment in segmentList :
            for segmentTuple in segment :
                if (isFirstSegment) :
                    isFirstSegment = False
                else :
                    command += ", "
                command += str(segmentTuple)
        command += ";"
        return command    