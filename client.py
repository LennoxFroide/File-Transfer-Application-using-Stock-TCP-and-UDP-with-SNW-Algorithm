# This has to be a class taking in source, source id, destination, destination id
import sys # Will help with the functioinality of the quit() command
from socket import *
import os # This will help with keeping track of all the files in the client_fl
import server as serverModule

# Getting the two modules to help us pick the transport protocols
import tcp_transport as tcpModule
import snw_transport as snwModule

class Client:
    """This class sets up the client"""

    def __init__(self, serverIp, serverPort, cacheIp, cachePort, transportProtocol):
        # Saving the server ip/name
        self.serverIp = serverIp
        # Saving the server port number
        self.serverPort =serverPort
        # Saving the cache ip/name
        self.cacheIp = cacheIp
        # Saving the cache port number
        self.cachePort = cachePort
        # Saving the transport protocol to be used by client
        self.transportProtocol = transportProtocol
        # Getting the names of files in the client_fl directory
        # self.clientMap = self.updateClientMap({})
        # Path to client folder
        self.path = 'client_fl'
    

    #----------------------------------------Utility Methods---------------------------------------------------#
    def getCommandAndFile(self, string):
        # We will split the string using the whitespace 
        actionArray = string.split(" ")
        # We should have an array of length 2
        if len(actionArray) < 1 or len(actionArray) > 2: # Sanity check
            raise Exception("Error in taking in commands!")
        # Now we will iterate this array and get the command and file name
        elif len(actionArray) == 1:
            action, filename = actionArray[0].lower(), None
        else:
            action, filename = actionArray[0].lower(), actionArray[1]
        
        return [action, filename]
    
    def quit(self):
        """This method terminates the program"""
        sys.exit('Exiting program!')


import argparse
# We need this main method to get inputs from the user from the command line
if __name__ == "__main__":
    # This module will help us to get inputs from user
    while True:
    # import argparse
        
        # This flag will set up the user client first before doing anything else
        clientSet = False
        
        # To help us access the argumentparser function
        parser = argparse.ArgumentParser()
        
        # Indicating the arguments required to set up client
        parser.add_argument("serverip", type=str)
        parser.add_argument("serverportnumber", type=int)
        parser.add_argument("cacheip", type=str)
        parser.add_argument("cacheportnumber", type=int)
        parser.add_argument("transportprotocol", type=str)
        
        # Grabbing the string of input arguments for the client
        args = parser.parse_args()
        print(args)
        # Now we can set the values for the client class
        myClient = Client(args.serverip, args.serverportnumber, args.cacheip, args.cacheportnumber, args.transportprotocol)
        
        # Taking the command from the user
        userCommand = input("Enter command: ")

        commandFileArray = myClient.getCommandAndFile(userCommand) 
        command, filename = commandFileArray[0], commandFileArray[1]

        # To quit program
        if command == 'put':
            print('The command is %f \n', command)
            print('The file is %f \n', filename)
            clientSocket = socket(AF_INET, SOCK_STREAM)
            clientSocket.connect((myClient.serverIp, myClient.serverPort))
            tcpModule.tcp_put_command(myClient.serverIp, myClient.serverPort, userCommand, clientSocket)
            # Getting the full path to the file
            path_name = os.path.join(myClient.path,filename)
            # Opening the file to read it
            readFile = open(path_name, 'r')
            # Reading the file
            fileToUpload = readFile.read()
            # Now we can send the file but we first need to check the transport protocol
            if myClient.transportProtocol == 'tcp':
                # Building the get ports for server
                # Uploading the file using TCP
                print(filename)
                tcpModule.tcp_upload(myClient.serverIp, myClient.serverPort + 1000, fileToUpload, clientSocket, None)
            else:# We're are using stop-and-wait
                snwModule.snw_upload(myClient.serverIp, myClient.serverPort + 1000, myClient.path, filename)
        elif command == 'quit':
            myClient.quit()
        elif command == 'get':
            print('The command is %f \n', command)
            print('The file is %f \n', filename)
            if myClient.transportProtocol == 'tcp':
                fileLivesHere = tcpModule.tcp_get_command(myClient.path, myClient.cacheIp, myClient.cachePort, myClient.serverIp, myClient.serverPort, userCommand)
                print(fileLivesHere)
            else: # We have a UDP Connection
                # Creating a UDP port and sending it
                clientSocketSNW = socket(SOCK_DGRAM)
                clientSocketSNW.connect((myClient.cacheIp, myClient.cachePort + 100))
                # We will receive the file from the cache
                fileLivesHere = snwModule.snw_get_command(myClient.path, myClient.cacheIp, myClient.cachePort, myClient.serverIp, myClient.serverPort, userCommand, clientSocketSNW)
                continue
            
        else:
            pass

