# -*- coding: UTF8 -*-
import MySQLdb
import os
import unittest



from database.MainServerDB.ImagesInServerManager import ImageServerManager
from database.MainServerDB.ServerVMManager import ServerVMManager
from database.DBUtils.DBUtils import DBUtils

class DBMainServerTests(unittest.TestCase):
    '''
        Clase encargada de realizar los test unitarios asociados 
    '''
    def test_maxVMNumber(self):
        #Instanciamos la clase
        serverVM = ServerVMManager("CygnusCloud","cygnuscloud2012","DBMainServerTest")
        m1 = serverVM.getMaxVMNumber(1)
        m2 = 5
        self.assertEquals(m1, m2, "Not same number of VM")
        
    def test_freeVMNumber(self):
        #Instanciamos la clase
        serverVM = ServerVMManager("CygnusCloud","cygnuscloud2012","DBMainServerTest")
        m1 = serverVM.getFreeVMNumber(3)
        m2 = 1
        self.assertEquals(m1, m2, "Not same number of free VM")
        
    def test_servers(self):
        #Instanciamos la clase
        serverVM = ServerVMManager("CygnusCloud","cygnuscloud2012","DBMainServerTest")
        l1 = serverVM.getServers()
        l2 = [1,2,3]
        self.assertEquals(l1, l2, "Not same servers")
        
    def test_changeMaxVM(self):
        #Instanciamos la clase
        serverVM = ServerVMManager("CygnusCloud","cygnuscloud2012","DBMainServerTest")
        serverVM.setMaxVM(2,7)
        m1 = serverVM.getMaxVMNumber(2)
        m2 = 7
        self.assertEquals(m1, m2, "Not change VM number")
        
    def test_subscribeServer(self):
        #Instanciamos la clase
        serverVM = ServerVMManager("CygnusCloud","cygnuscloud2012","DBMainServerTest")
        id = serverVM.subscribeServer("portTest","IPTest",23)
        self.assertTrue(serverVM.isServerExists(id), "Not server created")
        
    def test_unsubscribeServer(self):
        #Instanciamos la clase
        serverVM = ServerVMManager("CygnusCloud","cygnuscloud2012","DBMainServerTest")
        serverVM.unsubscribeServer(4)
        self.assertFalse(serverVM.isServerExists(4), "Not server created")

    def test_getImageServers(self):
        #Instanciamos la clase
        serverVM = ServerVMManager("CygnusCloud","cygnuscloud2012","DBMainServerTest")
        l1 = serverVM.getImageServers(1)
        l2 = [1,3]
        self.assertEquals(l1, l2, "Not same servers")

    def test_getServerImages(self):
        #Instanciamos la clase
        imageS = ImageServerManager("CygnusCloud","cygnuscloud2012",1,"DBMainServerTest")
        l1 = imageS.getServerImages()
        l2 = [1,3]
        self.assertEquals(l1, l2, "Not same servers")
        
    def test_getImageName(self):
        #Instanciamos la clase
        imageS = ImageServerManager("CygnusCloud","cygnuscloud2012",1,"DBMainServerTest")
        n1 = imageS.getImageName(2)
        n2 = "VMName2"
        self.assertEquals(n1, n2, "Not same VM Names")
        
    def test_getImageDescription(self):
        #Instanciamos la clase
        imageS = ImageServerManager("CygnusCloud","cygnuscloud2012",1,"DBMainServerTest")
        d1 = imageS.getImageDescription(2)
        d2 = "A Virtual machine Image 2"
        self.assertEquals(d1, d2, "Not same VM descriptions")


    def test_createNewImage(self):
        #Instanciamos la clase
        imageS = ImageServerManager("CygnusCloud","cygnuscloud2012",1,"DBMainServerTest")
        id1 = imageS.createNewImage("VMNameTest","A Virtual machine Image Test")
        self.assertTrue(imageS.isImageExists(id1), "Not same VM descriptions")
        
    def test_changeDescription(self):
        #Instanciamos la clase
        imageS = ImageServerManager("CygnusCloud","cygnuscloud2012",1,"DBMainServerTest")
        imageS.setDescription(3, "A modified test Virtual machine Image 3")
        d1 = imageS.getImageDescription(3)
        d2 = "A modified test Virtual machine Image 3"
        self.assertEquals(d1, d2, "Not VM description changed")




if __name__ == "__main__":
    #Cargamos el script de prueba
    dbUtils = DBUtils(os.getcwd() + "/DBMainServerTest.sql")
    dbUtils.initMySqlUser("CygnusCloud","cygnuscloud2012")
    dbUtils.loadScript("CygnusCloud","cygnuscloud2012")     
    unittest.main()