# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: imageRepositoryDB.py    
    Version: 2.0
    Description: image repository database connector
    
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

from ccutils.databases.connector import BasicDBConnector
from re import sub
from os import path

from imageRepository.database.image_status_t import IMAGE_STATUS_T


class ImageRepositoryDBConnector(BasicDBConnector):
    """
    Image repository database connector
    """
    
    
    def __init__(self, sqlUser, sqlPassword, databaseName):
        """
        Establishes the connection with the database
        Args:
            sqlUser: the MySQL user to use
            sqlPassword: the MySQL user's password
            databaseName: the database's name
        """
        BasicDBConnector.__init__(self, sqlUser, sqlPassword, databaseName)
    
    def getImageData(self, imageID):
        """
        Returns the data associated with an image
        Args:
            imageID: an image ID
        Returns:
            a dictionary with the image's data. If the image does not exist,
            None will be returned.
        """
        sqlQuery = "SELECT * FROM Image WHERE imageID = {0}".format(imageID)
        row = self._executeQuery(sqlQuery, False)
        if (row == None) :
            return None
        (imageID, compressedFilePath, imageStatus) = row[0]
        result = dict()
        result["compressedFilePath"] = str(compressedFilePath)
        result["imageStatus"] = imageStatus
        return result
    
    def addImage(self):   
        """
        Registers an image in the database
        Args:
            None
        Returns:
            The new image's ID.
        """     
        update = "INSERT INTO Image(compressedFilePath, imageStatus) VALUES (NULL, {0});".format(IMAGE_STATUS_T.NOT_RECEIVED)
        self._executeUpdate(update)
        query = "SELECT imageID FROM Image;"
        results = self._executeQuery(query, False)
        imageID = int(results[len(results) - 1])
        update = "UPDATE Image SET compressedFilePath = '{1}' WHERE imageID = {0};".format(imageID, "undefined" + str(imageID))
        self._executeUpdate(update)
        return imageID
    
    def cancelImageEdition(self, imageID):
        """
        Unlocks an image
        Args:
            imageID: an image ID
        Returns:
            Nothing
        """
        query = "SELECT compressedFilePath FROM Image WHERE imageID = {0};".format(imageID)
        result = self._executeQuery(query, True)
        if (result == None) :
            # The image is not locked => we've nothing to do
            return
        if ("undefined" in result) :
            self.deleteImage(imageID)
        else :
            self.changeImageStatus(imageID, IMAGE_STATUS_T.READY)
    
    def deleteImage(self, imageID):
        """
        Deletes an image from the database
        Args:
            imageID: an image ID
        Returns:
            Nothing
        """
        update = "DELETE FROM Image WHERE imageID = {0};".format(imageID)
        self._executeUpdate(update)
    
    def addBaseImage(self, compressedFilePath):
        """
        Registers a base image in the database
        Args:
            compressedFilePath: a .zip file path
        Returns:
            the new image's ID
        """
        update = "INSERT INTO Image(compressedFilePath, imageStatus) VALUES ('{0}', {1});".format("undefined", IMAGE_STATUS_T.READY)
        self._executeUpdate(update)
        
    def changeImageStatus(self, imageID, newStatus):
        """
        Changes an image's state
        Args:
            imageID: an image ID
            newStatus: the new image ID
        Returns:
            Nothing
        """
        update = "UPDATE Image SET imageStatus = {1} WHERE imageID = {0};".format(imageID, newStatus)
        self._executeUpdate(update)
        
    def handleFinishedUploadTransfer(self, fileName):
        """
        Updates an uploaded image's status
        Args:
            fileName: a .zip file path
        Returns:
            Nothing
        """
        imageID = sub("[^0-9]", "", path.basename(fileName))
        update = "UPDATE Image SET imageStatus = {1}, compressedFilePath = '{2}' WHERE imageID = {0};".format(imageID, IMAGE_STATUS_T.READY, fileName)
        self._executeUpdate(update)    
        
    def handlePartialDownloadTransfer(self, fileName):
        """
        Updates a partially downloaded image's status
        Args:
            fileName: a .zip file path
        Returns:
            Nothing
        """
        imageID = sub("[^0-9]", "", path.basename(fileName))
        self.changeImageStatus(imageID, IMAGE_STATUS_T.READY)