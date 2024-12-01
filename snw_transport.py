import os
from socket import *
import time
# signal.signal(signal.SIGALRM, handler_function)
clientDirectory = 'client_fl'
def snw_extract_command_and_file(string):
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

# full_path = os.path.join(clientDirectory, )
# Function to break data into 1000 byte chunks
def chunkData(directory, file):
    arrayData = []
    # Path to entire file
    file_path = os.path.join(directory,file)
    # Opening it to calculate the total length in bytes and closing it
    fileData = open(file_path, 'r')
    fileContent = fileData.read()
    sizeBytes = len(fileContent.encode('utf-8'))
    fileData.close()
    # Opening it to read the actual information and generate chunks
    fileData = open(file_path, 'r')
    # dataToSend = fileData.read()
    while True:
        dataChunk = fileData.read(1000)
        # arrayData.append(dataChunk)
        if not dataChunk:
            fileData.close()
            break
        arrayData.append(dataChunk)
    return [sizeBytes,arrayData]

# result = chunkData('file_1.txt')
# print(result[0])


#----------------Client uploads file using SNW-----------------------------------------------#
"""
def snw_put_command(serverIp, serverPortNumber, putCommand):# The method to send put command and file name to server
    serverName = serverIp
    serverPort = serverPortNumber
    # Creating a client socket
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    message = putCommand
    clientSocket.send(message.encode())
    serverResponse = clientSocket.recv(1024).decode()

    if serverResponse == 'File created successfully!':
        print('Server did it!')
        clientSocket.close()
    else:
        print('Server side error!\n')
        print(serverResponse)
"""

def snw_upload(serverIp, serverPortNumber, directory, file):
    serverName = serverIp
    # We will use a different port to send the actual data
    serverPort = serverPortNumber
    # Creating a client socket
    clientSocket = socket(SOCK_DGRAM)
    clientSocket.connect((serverName, serverPort))
    # Sending the actual message
    # message1 = fileToUpload
    fileByteSize , fileChunkArray = chunkData(directory, file)
    # print(fileByteSize)
    print(len(fileChunkArray[-1].encode('utf-8')))
    # String file size
    stringFileSize = 'LEN:' + str(fileByteSize)
    # Sending the file size to server
    clientSocket.sendto(stringFileSize.encode(), (serverName, serverPort))
    print('I have sent LEN!')
    # Iterating the message chunks
    for chunk in fileChunkArray:
        # Sending each chunk
        # start_time = time.time()
        clientSocket.sendto(chunk.encode(),(serverName, serverPort))
        # Waiting for ACK message
        serverResponse, serverAddress = clientSocket.recvfrom(2048)
        serverResponse = serverResponse.decode()
        # Checking if it's ACK
        if serverResponse == 'ACK':
            # We need to send the next chunk
            continue
        elif serverResponse == 'FIN': # We're done sending chunks
            print('File uploaded to server!')
            clientSocket.close()
        serverResponse, serverAddress = clientSocket.recvfrom(2048)
        serverResponse = serverResponse.decode()
        if serverResponse == 'File uploaded successfully':
            print('File uploaded to server!')
            # clientSocket.close()
        else:
            pass
#------------------------Servers to handle put command using snw---------------------------------------#
def snw_create_two_servers(serverPortNumber1, serverPortNumber2, serverDirectory, serverTransportProtocol):
    # Getting the port number
    serverPortCommand = serverPortNumber1
    serverPortData = serverPortNumber2
    # serverPortChunks = serverPortData + 10
    # Creating a TCP socket
    serverSocketCommand = socket(AF_INET, SOCK_STREAM)# Command is always TCP
    serverSocketData = socket(SOCK_DGRAM)
    # serverSocketChunks = socket(AF_INET, SOCK_DGRAM)
    # Binding socket to port
    serverSocketCommand.bind(('', serverPortCommand))
    serverSocketData.bind(('', serverPortData))
    # serverSocketChunks.bind(('', serverPortChunks))

    serverSocketCommand.listen(1)
    serverSocketData.listen(1)
    # serverSocketChunks.listen(1)
    # Getting the transport protocol
    transportProtocol = serverTransportProtocol
    # Indicating that the server is ready
    print("Server is ready for the client!")
    while True:
        clientSocket, address = serverSocketCommand.accept()# Waiting for client to reach out
        # Getting the client's message
        message = clientSocket.recv(1024).decode()
        # Resolving it into command and filename
        command, filename = snw_extract_command_and_file(message)
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
    while True:
        print('Getting length')
        clientDataSocket, address = serverSocketData.accept()
        if clientDataSocket:# Grabbing the size of the file
            fileSize, clientAddress = clientDataSocket.recvfrom(2048)# Waiting for client to reach out
            # Getting the client's message
            fileData = fileSize.decode()
            # Splitting the fileSize string
            lengthArray = fileData.split(':')
            # Grabbing the actual size
            integerSizeBytes = int(lengthArray[1])
            print(integerSizeBytes)
            break
            # runningChunkSize = 0
            # clientSocket.close()
    runningChunkSize = 0
    file_path = os.path.join(serverDirectory, filename)
    fileToWrite = open(file_path, 'a')
    while True:
        print('Getting data!')
        # Getting the client's message
        fileData = clientDataSocket.recv(1000)
        fileData = fileData.decode()
        print(len(fileData.encode('utf-8')))
        # Grabbing chunks
        runningChunkSize += 1000
        # Sending an ACK message back to client
        acknowledgement = 'ACK'
        clientDataSocket.send(acknowledgement.encode())
        
        fileToWrite.write(fileData)
        # Breaking from the data scoket
        if runningChunkSize >= integerSizeBytes:
            print("I'm done!")
            response = 'FIN!'
            clientDataSocket.send(response.encode())
            fileToWrite.close()
            clientDataSocket.close()
            # clientSocket.close()
            break
        elif not fileData:
            response = 'Packets were lost!'
            clientDataSocket.send.send(response.encode())
            break
        else:
            continue
        # If not file data and running chunk
    

        
# To go back to while loop
#----------------------Server to send file using snw socket--------------------------#
def snw_create_two_servers_get_command_send_file(serverPortNumber, serverUDPPort, serverDirectory):
    # Getting the port number to receive eget command from server
    serverPort = serverPortNumber + 100
    # Creating a TCP socket
    serverSocket = socket(AF_INET, SOCK_STREAM)# Get command always TCP
    serverSocket.bind(('', serverPort))
    serverSocket.listen(1)

    # Creatind SNW socket to send file to cache
    serverSocketData = socket(SOCK_DGRAM) # The snw socket to send file to cache
    serverSocketData.bind(('', serverUDPPort))
    serverSocketData.listen(1)
    # Indicating that the server is ready
    print("Server 2 is ready for the client!")
    # Will use this to initialize the 2nd port to receive uploads
    #counterUploadSocket = 0
    # To keep listening infinitely
    while True:
        cacheSendingGetRequest, address = serverSocket.accept()# Waiting for client to reach out
        # Getting the cache's message
        message = cacheSendingGetRequest.recv(1024).decode()
        # Resolving it into command and filename
        command, filename = snw_extract_command_and_file(message)
        # Evaluating the command
        print(command)
        if command == 'get':
            # We need to chunk this data
            fileByteSize , fileChunkArray = chunkData(serverDirectory, filename)
            # Sending data to client 
            #TODO: Implement SNW to send the file to the cache
            # message1 = fileToUpload
            # print(fileByteSize)
            print(len(fileChunkArray[-1].encode('utf-8')))
            # String file size
            stringFileSize = 'LEN:' + str(fileByteSize)
            cacheSendingGetRequest.send(stringFileSize.encode())
            print('I have sent LEN!')
            # break
        # Sending the file size to cache over UDP port
        # print('I have sent LEN!')
        while True:
            cacheFileRequest, address = serverSocketData.accept()
            # message = cacheSendingGetRequest.recv(1024).decode()
            if cacheFileRequest:
                break
        print('Cache is ready to receive file from server!')
        # Iterating the message chunks
        for chunk in fileChunkArray:
            # Sending each chunk
            cacheFileRequest.send(chunk.encode())# Should be sending to UDP socket but only have TCP
            # Waiting for ACK message
            cacheSendingGetRequestMessage, cacheAddress = cacheFileRequest.recvfrom(2048)
            cacheResponse = cacheSendingGetRequestMessage.decode()
            # Checking if it's ACK
            if cacheResponse == 'ACK':
                # We need to send the next chunk
                continue
        cacheSendingGetRequestMessage, cacheAddress = cacheFileRequest.recvfrom(2048)
        cacheResponse = cacheSendingGetRequestMessage.decode()
        if cacheResponse == 'FIN!': # We're done sending chunks
            print('File uploaded to server!')
            cacheFileRequest.close()
            continue


#-------------------------------Two cache ports to handle the get command in snw----------------------------------#
def snw_create_two_caches_get_command(cachePortNumber, cachePortTwo, cacheDirectory, serverIp, serverPortNumber, cacheSNWSocket):
    # Getting the port number to receive get command
    cachePortGetCommand = cachePortNumber # RECEIVES TCP FROM CLIENT
    # Getting the port number to connect to server
    # cachePortConnectToServer = cachePortTwo # cachePort + 10
    serverPortSendGet = serverPortNumber + 100 # Send TCP GET TO SERVER 
    serverPortRecvServer = serverPortNumber + 1001 # Server side port to send file to cache
    serverSendGetName = serverIp
    # Creating a TCP socket
    cacheSocketGetCommand = socket(AF_INET, SOCK_STREAM) # RECEIVES TCP FROM CLIENT
    cacheSocketGetCommand.bind(('', cachePortGetCommand))# TCP: Listens for get command from client
    cacheSocketGetCommand.listen(1)

    # Sends get command to server
    cacheSocketSendCommandToServer = socket(AF_INET, SOCK_STREAM) # Send TCP GET TO SERVER

    # Sends SNW Data to client
    cacheSNWSocket.bind(('', cachePortNumber + 100)) # Send SNW Data to client
    cacheSNWSocket.listen(1)

    # Receives SNW data from server
    cacheSocketReceiveFileFromServer = socket(SOCK_DGRAM)
    # Connecting it to the server
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
        command, filename = snw_extract_command_and_file(message)
        # Evaluating the command
        if command == 'get':
            # toClient = 'File downloaded from cache!'
            # Getting the path to create file in
            file_path = os.path.join(cacheDirectory, filename)
            # Checking if file exists in the cache folder
            if not os.path.isfile(file_path):
                # We need to connect to the server
                cacheSocketSendCommandToServer.connect((serverSendGetName, serverPortSendGet))# This just sends get command to server
                # This is the intial get command from client being sent to server
                cacheSocketSendCommandToServer.send(message.encode())
                # Wait for response from server
                # serverSocketReceiveGetResponse, address = cacheSocketSendCommandToServer.accept()
                # We are accepting the file from the server
                f = open(file_path, "w")
                # TODO: Implement SNW to receive the file from server
                # cacheSocketReceiveFileFromServer.connect((serverSendGetName, serverPortRecvServer))
                initializationMessage = 'Ready!'
                # cacheSocketReceiveFileFromServer.connect((serverSendGetName, serverPortRecvServer))
                # cacheSocketReceiveFileFromServer.send(initializationMessage.encode())
                while True:
                    print('Getting length')
                    # This receives snw message from server
                    # Grabbing the size of the file
                    fileSize = cacheSocketSendCommandToServer.recv(2048)# Waiting for client to reach out
                    # Getting the client's message
                    fileData = fileSize.decode()
                    # Splitting the fileSize string
                    lengthArray = fileData.split(':')
                    # Grabbing the actual size
                    integerSizeBytes = int(lengthArray[1])
                    print(integerSizeBytes)
                    break
                cacheSocketReceiveFileFromServer.connect((serverSendGetName, serverPortRecvServer))
                cacheSocketReceiveFileFromServer.send(initializationMessage.encode())
                runningChunkSize = 0
                file_path = os.path.join(cacheDirectory, filename)
                fileToWrite = open(file_path, 'a')
                while True:
                    print('Getting data!')
                    # Getting the client's message
                    fileData = cacheSocketReceiveFileFromServer.recv(1000)
                    fileData = fileData.decode()
                    print(len(fileData.encode('utf-8')))
                    # Grabbing chunks
                    runningChunkSize += 1000
                    # Sending an ACK message back to client
                    acknowledgement = 'ACK'
                    cacheSocketReceiveFileFromServer.send(acknowledgement.encode())
                    fileToWrite.write(fileData)
                    if runningChunkSize >= integerSizeBytes:
                        print("I'm done!")
                        response = 'FIN!'
                        cacheSocketReceiveFileFromServer.send(response.encode())
                        fileToWrite.close()
                        cacheSocketReceiveFileFromServer.close()
                        # clientSocket.close()
                        break
                    elif not fileData:
                        response = 'Packets were lost!'
                        cacheSocketReceiveFileFromServer.send(response.encode())
                        break
                    else:
                        continue
        # TODO: Implement snw to send file to client
        # message1 = fileToUpload
        while True:
            clientSocketSNW, address = cacheSNWSocket.accept()
            # Getting the client's message
            clientResponse = clientSocketSNW.recv(1024).decode()
            # clientResponse = clientMessage.decode()
            if clientResponse == 'Ready!':
                # Then we send the string lenght message
                # We have a connection to clients SNW socket
                # clientSocketSNW.send(stringFileSize.encode())
                print("we have a connection to client SNW socket!")
                break
        fileByteSize , fileChunkArray = chunkData(cacheDirectory, filename)
        # print(fileByteSize)
        print(len(fileChunkArray[-1].encode('utf-8')))
        # String file size
        stringFileSize = 'LEN:' + str(fileByteSize)
        # Sending the file size to server
        clientSocketSNW.send(stringFileSize.encode())
        print('I have sent LEN!')
        # Iterating the message chunks
        for chunk in fileChunkArray:
            # Sending each chunk
            clientSocketSNW.send(chunk.encode())
            # Waiting for ACK message
            clientSNWResponse= clientSocketSNW.recv(2048)
            clientResponse = clientSNWResponse.decode()
            # Checking if it's ACK
            if clientResponse == 'ACK':
                # We need to send the next chunk
                continue
            elif clientResponse == 'FIN': # We're done sending chunks
                print('File uploaded to server!')
                clientSocket.close()
            else:
                pass
        clientSNWResponse= clientSocketSNW.recv(2048)
        clientResponse = clientSNWResponse.decode()
        if clientResponse == 'FIN!': # We're done sending chunks
            print('File uploaded to server!')
            clientSocket.close()
                

#--------------------------------------The method to send GET command-----------------------------------------#
def snw_get_command(clientDirectory, cacheIp, cachePortNumber, serverIp, serverPortNumber, getCommand, clientSocketSNW):# The method to send put command and file name to server
    # Getting cache ip and port number
    cacheName = cacheIp
    cachePort = cachePortNumber
    serverName = serverIp
    serverPort = serverPortNumber
    # Creating a client socket
    clientSocket = socket(AF_INET, SOCK_STREAM)
    # Client socket to receive SNW file
    # clientGetSnwPort = 20001
    # We want to connect to the cache first
    clientSocket.connect((cacheName, cachePort))
    message = getCommand
    _, filename = snw_extract_command_and_file(getCommand)
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
    # We will receive the data through this socket # We need to use the extra cache port
    # clientSocketSNW.bind(('', clientGetSnwPort))
    # clientSocketSNW.connect((cacheName, cachePort + 100))
    initializationMessage = 'Ready!'
    clientSocketSNW.send(initializationMessage.encode())

    #clientSocketSNW.listen(1)
    # Getting the message
    while True:
        print('Getting length')
        fileSize, cacheAddress = clientSocketSNW.recvfrom(2048)
        if fileSize:# Grabbing the size of the file
            # fileSize, cacheAddress = cacheDataSocket.recvfrom(2048)# Waiting for cache to send LEN message
            # Getting the client's message
            fileData = fileSize.decode()
            # Splitting the fileSize string
            lengthArray = fileData.split(':')
            # Grabbing the actual size
            integerSizeBytes = int(lengthArray[1])
            print(integerSizeBytes)
            break
            # runningChunkSize = 0
            # clientSocket.close()
    runningChunkSize = 0
    file_path = os.path.join(clientDirectory, filename)
    fileToWrite = open(file_path, 'a')
    while True:
        print('Getting data!')
        # Getting the client's message
        fileDataCache, cacheAddress = clientSocketSNW.recvfrom(2048)
        fileData = fileDataCache.decode()
        print(len(fileData.encode('utf-8')))
        # Grabbing chunks
        runningChunkSize += 1000
        # Sending an ACK message back to client
        acknowledgement = 'ACK'
        clientSocketSNW.sendto(acknowledgement.encode(), (cacheName, cachePort+100))
    
        fileToWrite.write(fileData)
        # clientSocket.close()
        # Breaking from the data scoket
        if runningChunkSize >= integerSizeBytes:
            response = 'FIN!'
            clientSocketSNW.send(response.encode())
            fileToWrite.close()
            # clientSocket.close()
            break
        elif not fileData:
            response = 'Packets were lost!'
            clientSocketSNW.send(response.encode())
            break
        else:
            continue
