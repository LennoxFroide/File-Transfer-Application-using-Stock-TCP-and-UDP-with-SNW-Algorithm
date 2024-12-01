from socket import *
import os # This will help with keeping track of all the files in the client_fl
def tcp_extract_command_and_file(string):
    # We will split the string using the whitespace 
        actionArray = string.split(" ")
        # We should have an array of length 2
        if len(actionArray) <= 1 or len(actionArray) > 2: # Sanity check
            raise Exception("Error in taking in commands!")
        # Now we will iterate this array and get the command and file name
        elif len(actionArray) == 2:
            action, filename = actionArray[0].lower(), actionArray[1]
            return [action, filename]
        else:
            pass
#-------------------------Functions to send put and get commands using tcp--------------------------------------------#
def tcp_put_command(serverIp, serverPortNumber, putCommand, clientSocket):# The method to send put command and file name to server
    serverName = serverIp
    serverPort = serverPortNumber
    # Creating a client socket
    message = putCommand
    clientSocket.send(message.encode())
    serverResponse = clientSocket.recv(1024).decode()

    if serverResponse == 'File created successfully!':
        print('Server did it!')
        # clientSocket.close()
    else:
        print('Server side error!\n')
        print(serverResponse)

def tcp_get_command(clientDirectory, cacheIp, cachePortNumber, serverIp, serverPortNumber, getCommand):# The method to send put command and file name to server
    # Getting cache ip and port number
    cacheName = cacheIp
    cachePort = cachePortNumber
    serverName = serverIp
    serverPort = serverPortNumber
    # Creating a client socket
    clientSocket = socket(AF_INET, SOCK_STREAM)
    # We want to connect to the cache first
    clientSocket.connect((cacheName, cachePort))
    message = getCommand
    _, filename = tcp_extract_command_and_file(getCommand)
    clientSocket.send(message.encode())
    file_path = os.path.join(clientDirectory, filename)
    # Getting the file to write data to ready
    fileToWrite = open(file_path, 'w')
    # Prechecking where the file lives
    cacheDirectory = 'cache_fl'
    serverDirectory = 'server_fl'
    file_path_cache = os.path.join(cacheDirectory, filename)
    file_path_server = os.path.join(serverDirectory, filename)
    if os.path.isfile(file_path_cache):
        sourceMessage = 'File downloaded from cache!'
        pass
    elif os.path.isfile(file_path_server):
        sourceMessage = 'File downloaded from server!'
    else:
        sourceMessage = 'Error: File is neither in cache nor server!'

    while True:
        cacheResponse = clientSocket.recv(10240).decode()
        fileToWrite.write(cacheResponse)
        if not cacheResponse:
            fileToWrite.close()
            clientSocket.close()
            break
    return sourceMessage


#-----------------------------------Creating 2 ports 1 to receive get command and 1 to send get file from cache to server--------------#
def tcp_create_two_caches_get_command(cachePortNumber, cachePortTwo, cacheDirectory, serverIp, serverPortNumber):
    # Getting the port number to receive get command
    cachePortGetCommand = cachePortNumber
    # Getting the port number to connect to server
    cachePortConnectToServer = cachePortTwo
    serverPortSendGet = serverPortNumber
    serverSendGetName = serverIp
    # Creating a TCP socket
    cacheSocketGetCommand = socket(AF_INET, SOCK_STREAM)
    cacheSocketSendCommandToServer = socket(AF_INET, SOCK_STREAM)
    # Binding socket to port
    cacheSocketGetCommand.bind(('', cachePortGetCommand))
    # cacheSocketSendCommandToServer.bind(('', cachePortConnectToServer))
    # Turns it on
    cacheSocketGetCommand.listen(1)
    # cacheSocketSendCommandToServer.listen(1)
    # Indicating that the server is ready
    print("Cache is ready for the client!")
    # Will use this to initialize the 2nd port to receive uploads
    #counterUploadSocket = 0
    # To keep listening infinitely
    while True:
        clientSocket, address = cacheSocketGetCommand.accept()# Waiting for client to reach out
        # serverSocketReceiveGetResponse, address = cacheSocketSendCommandToServer.accept()
        # Getting the client's message
        message = clientSocket.recv(1024).decode()
        # Resolving it into command and filename
        command, filename = tcp_extract_command_and_file(message)
        # Evaluating the command
        if command == 'get':
            # toClient = 'File downloaded from cache!'
            # clientSocket.send(toClient.encode())
            # clientSocket.close()
            # continue
            # Getting the path to create file in
            file_path = os.path.join(cacheDirectory, filename)
            # Checking if file exists in the cache folder
            if os.path.isfile(file_path):
                # Making sure that the protocol is tcp
                # Reading the file and preparing to send it
                # Opening the file to read it
                readFile = open(file_path, 'r')
                # Reading the file
                fileToDownload = readFile.read()
                # Sending the message
                clientSocket.send(fileToDownload.encode())
                # Closing
                # clientSocket.close()
                clientSocket.close()
                continue
            else:
                # We need to connect to the server
                cacheSocketSendCommandToServer.connect((serverSendGetName, serverPortSendGet))
                # This is the intial get command from client being sent to server
                cacheSocketSendCommandToServer.send(message.encode())
                # Wait for response from server
                # serverSocketReceiveGetResponse, address = cacheSocketSendCommandToServer.accept()
                # We are accepting the file from the server
                f = open(file_path, "w")
                while True:
                    serverResponse = cacheSocketSendCommandToServer.recv(102400).decode()
                    print('Getting response from server!')
                    # We will create this file in the cache and write to it
                    # Getting the path to create file in
                    # file_path = os.path.join(cacheDirectory, filename)
                    # Creating file with name filename
                    # f = open(file_path, "w")
                    # Writing the data from the cache to this file
                    f.write(serverResponse)
                    # We're done getting the data
                    # if not serverResponse:
                    f.close()
                    # We open the file again to send data to client
                    fileToClient = open(file_path, 'r')
                    # Reading it
                    fileData = fileToClient.read()
                    # Sending data to client
                    clientSocket.send(fileData.encode())
                    clientSocket.close()
                    break


                """
                if serverResponse == 'File downloaded from server!':
                    # We need to send this to the client
                    clientSocket.send(serverResponse.encode())
                    serverSocketReceiveGetResponse.close()
                    clientSocket.close()
                    continue
                    # break
                else:
                    raise Exception('Error occured while downloading file from server!')

                pass
                """

def tcp_create_two_servers_get_command_send_file(serverPortNumber, serverDirectory):
    # Getting the port number
    serverPort = serverPortNumber + 100
    # Creating a TCP socket
    serverSocket = socket(AF_INET, SOCK_STREAM)
    # Binding socket to port
    serverSocket.bind(('', serverPort))
    serverSocket.listen(1)
    # Indicating that the server is ready
    print("Server 2 is ready for the client!")
    # Will use this to initialize the 2nd port to receive uploads
    #counterUploadSocket = 0
    # To keep listening infinitely
    while True:
        cacheSendingGetRequest, address = serverSocket.accept()# Waiting for client to reach out
        # Getting the client's message
        message = cacheSendingGetRequest.recv(1024).decode()
        # Resolving it into command and filename
        command, filename = tcp_extract_command_and_file(message)
        # Evaluating the command
        print(command)
        if command == 'get':
            # Getting the path of file
            file_path = os.path.join(serverDirectory, filename)
            # We open the file again to send data to client
            fileToCache = open(file_path, 'r')
            # Reading it
            fileData = fileToCache.read()
            # Sending data to client
            cacheSendingGetRequest.send(fileData.encode())
            cacheSendingGetRequest.close()
            continue
            # response = 'File downloaded from server!'
            # cacheSendingGetRequest.send(response.encode())
            # cacheSendingGetRequest.close()
            # continue
        else:
            pass
#-------------------------------Creating 2 ports 1 for put command and 1 for put file----------------------------------------#
def tcp_create_two_servers(serverPortNumber1, serverPortNumber2, serverDirectory, serverTransportProtocol):
    # Getting the port number
    serverPortCommand = serverPortNumber1
    serverPortData = serverPortNumber2
    # serverPortGetCommand = serverPortNumber3
    # Creating a TCP socket
    serverSocketCommand = socket(AF_INET, SOCK_STREAM)
    serverSocketData = socket(AF_INET, SOCK_STREAM )
    # serverPortGetCommandSocket = socket(AF_INET, SOCK_STREAM)
    # Binding socket to port
    serverSocketCommand.bind(('', serverPortCommand))
    serverSocketData.bind(('', serverPortData))
    # serverPortGetCommandSocket.bind(('', serverPortGetCommand))

    serverSocketCommand.listen(1)
    serverSocketData.listen(1)
    # serverPortGetCommandSocket.listen(1)
    # Getting the transport protocol
    transportProtocol = serverTransportProtocol
    # Indicating that the server is ready
    print("Server is ready for the client!")
    while True:
        clientSocket, address = serverSocketCommand.accept()# Waiting for client to reach out
        # Getting the client's message
        # clientSocket.setblocking(0)
        message = clientSocket.recv(1024).decode()
        print(message)
        # Resolving it into command and filename
        command, filename = tcp_extract_command_and_file(message)
        # Evaluating the command
        if command == 'put':
            # Getting the path to create file in
            file_path = os.path.join(serverDirectory, filename)
            # Creating file with name filename
            f = open(file_path, "w")
            print('File created successfully!')
            # Sending response back to client
            response = 'File created successfully!'
            clientSocket.send(response.encode())
            break
            # clientSocket.close()
            # Getting the message
    file_path = os.path.join(serverDirectory, filename)
    fileToWrite = open(file_path, 'w')
    # clientSocket.settimeout(100)
    while True:
        # clientSocket, address = serverSocketData.accept()# Waiting for client to reach out
            # Getting the client's message
            print('Working...')
            fileData = clientSocket.recv(102400).decode()
            print(len(fileData.encode('utf-8')))
            # We can write this data
            # Getting the path to create file in
            # file = open(file_path, 'w')
            # Getting the path to create file in
            # file_path = os.path.join(serverDirectory, filename)
            # fileToWrite = open(file_path, 'w')
            fileToWrite.write(fileData)
            # response = 'File uploaded to server!'
            # clientSocket.send(response.encode())
            # fileToWrite.close()
            # clientSocket.close()
            # Breaking from the data scoket
            # or len(fileData.encode('utf-8')) < 1024
            # if not fileData:
                # print('No data')
            fileToWrite.close()
            response = 'File uploaded to server!'
            clientSocket.send(response.encode())    
            clientSocket.close()
            break
        # To go back to while loop
            continue
    # pass

# TODO: Delete this
def tcp_create_server(serverPortNumber, serverDirectory):
    # Getting the port number
    serverPort = serverPortNumber
    # Creating a TCP socket
    serverSocket = socket(AF_INET, SOCK_STREAM)
    # Binding socket to port
    serverSocket.bind(('', serverPort))
    serverSocket.listen(1)
    # Indicating that the server is ready
    print("Server is ready for the client!")
    # Will use this to initialize the 2nd port to receive uploads
    #counterUploadSocket = 0
    # To keep listening infinitely
    while True:
        clientSocket, address = serverSocket.accept()# Waiting for client to reach out
        # Getting the client's message
        message = clientSocket.recv(1024).decode()
        # Resolving it into command and filename
        command, filename = tcp_extract_command_and_file(message)
        # Evaluating the command
        if command == 'put':
            # Getting the path to create file in
            file_path = os.path.join(serverDirectory, filename)
            # Creating file with name filename
            f = open(file_path, "w")
            print('File created successfully!')
            # Sending response back to client
            response = 'File created successfully!'
            clientSocket.send(response.encode())
            clientSocket.close()
        elif command == 'get':
            pass
        else:
            pass
#--------------------------------------Associated with upload from client to server---------------------------------------#
def tcp_upload(serverIp, serverPortNumber, fileToUpload, clientSocket, filename = None):
    serverName = serverIp
    # We will use a different port to send the actual data
    serverPort = serverPortNumber
    # Creating a client socket
    # clientSocket = socket(AF_INET, SOCK_STREAM)
    # clientSocket.connect((serverName, serverPort))
    # Sending the actual message
    message1 = fileToUpload
    print('Tcp upload!')
    clientSocket.send(message1.encode())
    # clientSocket.close()
    # We also need to tell the server where to write it
    # message2 = filename
    # clientSocket = socket(AF_INET, SOCK_STREAM)
    #clientSocket.connect((serverName, serverPort))
    # clientSocket.send(message2.encode())
    serverResponse = clientSocket.recv(1024).decode()
    if serverResponse == 'File uploaded successfully':
        print('File uploaded to server!')
        # clientSocket.close()
    else:
        pass

# TODO: Delete this
def tcp_receive_upload_to_server(serverPortNumber, serverDirectory):
    print('Has been called')
    # Getting the port number
    serverPort = serverPortNumber
    # Creating a TCP socket
    serverSocket = socket(AF_INET, SOCK_STREAM)
    # Binding socket to port
    serverSocket.bind(('', serverPort))
    serverSocket.listen(1)
    # Indicating that the server is ready
    # print("Server is ready for the client!")
    #file_path = os.path.join(serverDirectory, filename)
    #file = open(file_path, 'w')
    # file.write(message)
    # To keep listening infinitely
    # messageCounter = 0
    while True:
        print('Outer loop')
        number = 1
        while number <= 1:
            print("Inner Loop")
            clientSocket, address = serverSocket.accept()# Waiting for client to reach out
            # Getting the client's message
            # if messageCounter == 0:
            dataToWrite = clientSocket.recv(1024).decode()
            # messageCounter += 1
            # clientSocket.close()
            number += 1
        # elif messageCounter >= 1: # This should be the file name
        print('Here!')
        clientSocket, address = serverSocket.accept()
        filename = clientSocket.recv(1024).decode()
        file_path = os.path.join(serverDirectory, filename)
        file = open(file_path, 'w')
        file.write(dataToWrite)
        response = 'File uploaded to server!'
        clientSocket.send(response.encode())
        file.close()
        clientSocket.close()
        

    