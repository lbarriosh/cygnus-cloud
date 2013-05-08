# -*- coding: UTF8 -*-
'''
Command handler class unit tests.
@author: Luis Barrios Hernández
@version: 1.0
'''
import unittest
from clusterServer.connector.commandsHandler import COMMAND_OUTPUT_TYPE, COMMAND_TYPE, CommandsHandler

class CommandsHandlerTest(unittest.TestCase):

    def test_createVMServerRegistrationCommand(self):
        result = CommandsHandler.createVMServerRegistrationCommand("VMServerIP", 1, "VMServerName")
        expectedResult = (COMMAND_TYPE.REGISTER_VM_SERVER, "VMServerIP$1$VMServerName")
        self.assertEquals(result, expectedResult, "createVMServerRegistrationCommand does not work")

    def test_createVMServerUnregistrationOrShutdownCommand(self):
        result = CommandsHandler.createVMServerUnregistrationOrShutdownCommand(True, "VMServerIP", True)
        expectedResult = (COMMAND_TYPE.UNREGISTER_OR_SHUTDOWN_VM_SERVER, "True$VMServerIP$True")
        self.assertEquals(result, expectedResult, "createVMServerUnregistrationOrShutdownCommand does not work")
        
    def test_createVMServerBootCommand(self):
        result = CommandsHandler.createVMServerBootCommand("Server1")
        expectedResult = (COMMAND_TYPE.BOOTUP_VM_SERVER, "Server1")
        self.assertEquals(result, expectedResult, "createVMServerBootCommand does not work")
        
    def test_createVMBootCommand(self):
        result = CommandsHandler.createVMBootCommand(1, 1)
        expectedResult = (COMMAND_TYPE.VM_BOOT_REQUEST, "1$1")
        self.assertEquals(result, expectedResult, "createVMBootCommand does not work")
        
    def test_createHaltCommand(self):
        result = CommandsHandler.createHaltCommand(True)
        expectedResult = (COMMAND_TYPE.HALT, "True")
        self.assertEquals(result, expectedResult, "createHaltCommand does not work")
        
    def test_commandArgumentsDeserialization(self):
        arguments = ["VMServerIP$1$VMServerName", "True$VMServerName$True", "VMServerName",
                     "1$1", "True"]
        commandTypes = [COMMAND_TYPE.REGISTER_VM_SERVER, COMMAND_TYPE.UNREGISTER_OR_SHUTDOWN_VM_SERVER,
                        COMMAND_TYPE.BOOTUP_VM_SERVER, COMMAND_TYPE.VM_BOOT_REQUEST, 
                        COMMAND_TYPE.HALT]
        expectedResults = [{"VMServerIP":"VMServerIP", "VMServerPort" : 1, "VMServerName" : "VMServerName"},
                           {"Unregister":True, "VMServerNameOrIP":"VMServerName", "Halt":True},
                           {"VMServerNameOrIP" : "VMServerName"}, {"VMID" : 1, "UserID" : 1},
                           {"HaltVMServers" : True}]
        i = 0
        while (i < len(arguments)) :
            result = CommandsHandler.deserializeCommandArgs(commandTypes[i], arguments[i])
            self.assertEquals(result, expectedResults[i], "deserializeCommandArgs does not work")
            i += 1
            
    def test_createVMServerBootUpErrorOutput(self):
        result = CommandsHandler.createVMServerRegistrationErrorOutput("ServerName", "Message")
        expectedResult = (COMMAND_OUTPUT_TYPE.VM_SERVER_REGISTRATION_ERROR, "ServerName$Message")
        self.assertEquals(result, expectedResult, "createVMServerBootUpErrorOutput does not work")

    def test_createVMServerRegistrationErrorOutput(self):
        result = CommandsHandler.createVMServerRegistrationErrorOutput("ServerName", "Message")
        expectedResult = (COMMAND_OUTPUT_TYPE.VM_SERVER_REGISTRATION_ERROR, "ServerName$Message")
        self.assertEquals(result, expectedResult, "createVMServerRegistrationErrorOutput does not work")

    def test_createVMBootFailureErrorOutput(self):
        result = CommandsHandler.createVMBootFailureErrorOutput(1, 1, "Message")
        expectedResult = (COMMAND_OUTPUT_TYPE.VM_BOOT_FAILURE, "1$1$Message")
        self.assertEquals(result, expectedResult, "createVMBootFailureErrorOutput does not work")
        
    def test_createVMConnectionDataOutput(self):
        result = CommandsHandler.createVMConnectionDataOutput(1, "IP", 1, "pass")
        expectedResult = (COMMAND_OUTPUT_TYPE.VM_CONNECTION_DATA, "1$IP$1$pass")
        self.assertEquals(result, expectedResult, "createVMConnectionDataOutput does not work")
        
    def test_commandOutputDeserialization(self):
        outputs = ["ServerName$Error", "1$1$Error", "1$IP$1$Pass"]
        outputTypes = [COMMAND_OUTPUT_TYPE.VM_SERVER_BOOTUP_ERROR, 
                       COMMAND_OUTPUT_TYPE.VM_BOOT_FAILURE, COMMAND_OUTPUT_TYPE.VM_CONNECTION_DATA]
        expectedResults = [{"ServerNameOrIPAddress": "ServerName", "ErrorMessage" : "Error"},
                           {"VMID" : 1, "UserID" : 1, "ErrorMessage" : "Error"},
                           {"UserID" : 1, "VNCServerIPAddress" : "IP", "VNCServerPort" : 1,
                            "VNCServerPassword" : "Pass"}]
        i = 0
        while (i < len(outputs)) :
            result = CommandsHandler.deserializeCommandOutput(outputTypes[i], outputs[i])
            self.assertEquals(result, expectedResults[i], "deserializeCommandOutput does not work")
            i += 1            

if __name__ == "__main__":
    unittest.main()