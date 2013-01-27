# Cut-n-paste these commands when necessary
# Create two shut down dummy servers
DELETE FROM VMServer;
DELETE FROM VMServerStatus;
INSERT INTO VMServer(serverId, serverName, serverStatus, serverIP, serverPort) VALUES
	(1, 'Server1', 2, '127.0.0.1', '10200'),
	(2, 'Server2', 2, '192.168.0.4', '10201');

#Create some dummy images
DELETE FROM Image;
INSERT INTO Image(imageId, name, description) VALUES 
	(1, 'Debian', 'Debian Squeeze AMD64'), 
	(2, 'Windows', 'Windows 7 Professional x64');
	
#"Deploy" them on a server
# DELETE FROM ImageOnServer	
INSERT INTO ImageOnServer VALUES(1, 1), (2, 2);