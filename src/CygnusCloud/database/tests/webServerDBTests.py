# -*- coding: UTF8 -*-
import unittest

from database.webServer.userAccess import UserAccess
from database.webServer.userManagement import UserManagement
from database.utils.configuration import DBConfigurator

class DBWebServerTests(unittest.TestCase):
    '''
        Clase encargada de realizar los test unitarios asociados 
    '''
       
    def test_loginUsaer(self):
        userA = UserAccess("CygnusCloud","cygnuscloud2012","WebServerDBTest")
        id1 = userA.login("Admin1", "0000")
        id2 = 8
        self.assertEquals(id1, id2, "User not match")
        
    def test_userTypes(self):
        userM = UserManagement("CygnusCloud","cygnuscloud2012","WebServerDBTest",2)
        l1 = userM.getTypeIds()
        l2 = [1,3]
        self.assertEquals(l1, l2, "Not same types")
        
    def test_userGroups(self):
        userM = UserManagement("CygnusCloud","cygnuscloud2012","WebServerDBTest",2)
        l1 = userM.getUserGroupsIds()
        l2 = [1,2]
        self.assertEquals(l1, l2, "Not same groups")
        
    def test_groupVMs(self):
        userM = UserManagement("CygnusCloud","cygnuscloud2012","WebServerDBTest",2)
        l1 = userM.getVMNames(1)
        l2 = ["VMName1","VMName2"]
        self.assertEquals(l1, l2, "Not same VMS")
        
    def test_groupSubjects(self):
        userM = UserManagement("CygnusCloud","cygnuscloud2012","WebServerDBTest",2)
        l1 = userM.getSubjects(1)
        l2 = ("Subject1",1,2012,"a")
        self.assertEquals(l1, l2, "Not same Subjects")   
        
    def test_groupTeachers(self):
        userM = UserManagement("CygnusCloud","cygnuscloud2012","WebServerDBTest",2)
        l1 = userM.getTeachers(1)
        l2 = ["Teacher1"]
        self.assertEquals(l1, l2, "Not same Teachers") 
        
    def test_deleteUser(self):
        userM = UserManagement("CygnusCloud","cygnuscloud2012","WebServerDBTest",1)
        userM.deleteUser(7)
        self.assertFalse(userM.isUserExists(7), "User not deleted")
        
    def test_createUser(self):
        userM = UserManagement("CygnusCloud","cygnuscloud2012","WebServerDBTest",1)
        userId = userM.createUser("UserTest","testPass",2)
        self.assertTrue(userM.isUserExists(str(userId)), "User not created")
        
    
    def test_deleteVM(self):
        userM = UserManagement("CygnusCloud","cygnuscloud2012","WebServerDBTest",1)
        userM.deleteVM("VMName3",2)
        self.assertFalse(userM.isVMExists("VMName3"), "VM not deleted")

    def test_deleteAllVM(self):
        userM = UserManagement("CygnusCloud","cygnuscloud2012","WebServerDBTest",1)
        userM.deleteAllVM(2)
        l1 = userM.getVMNames(2)
        l2 = []
        self.assertEquals(l1, l2, "Not All VM deleted")
        
    def test_createType(self):
        userM = UserManagement("CygnusCloud","cygnuscloud2012","WebServerDBTest",1)
        typeId = userM.createType("TypeTest")
        self.assertTrue(userM.isTypeExists(typeId), "type not created")
 
    def test_deleteType(self):
        userM = UserManagement("CygnusCloud","cygnuscloud2012","WebServerDBTest",1)
        userM.deleteType(4)
        self.assertFalse(userM.isTypeExists(4), "type not deleted") 
        
    def test_groupIds(self):
        userM = UserManagement("CygnusCloud","cygnuscloud2012","WebServerDBTest",1)
        l1 = userM.getGroupId("VMName1")
        l2 = [1]
        self.assertEquals(l1, l2, "Not Same groups")     
        
    def test_userIds(self):
        userM = UserManagement("CygnusCloud","cygnuscloud2012","WebServerDBTest",1)
        l1 = userM.getUsersId(1)
        l2 = [2,3,5]
        self.assertEquals(l1, l2, "Not Same users")    
        
if __name__ == "__main__":
    #Cargamos el script de prueba
    dbUtils = DBConfigurator("")
    dbUtils.runSQLScript("WebServerDBTest", "./WebServerDBTest.sql")
    dbUtils.addUser("CygnusCloud","cygnuscloud2012", "WebServerDBTest")
    unittest.main()
