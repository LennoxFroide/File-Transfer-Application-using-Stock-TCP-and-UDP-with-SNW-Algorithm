# Getting the two modules to help us pick the transport protocols
import tcp_transport as tcpModule
import snw_transport as snwModule
import os
from multiprocessing import Process # Will use this to initialize multiple server ports at once
import threading
from socket import *

class Server:
    """This class sets up the server."""

    def __init__(self, portNumber, transportProtocol):
        # Getting the "computer where the server class insstance will be established"
        self.portNumber = portNumber
        self.transportProtocol = transportProtocol
        self.path = 'server_fl'

def build_server_put_ports(serverPortNumber, secondServerPortNumber, serverPath, serverTransportProtocol, counter = None):
    if counter != None:
        tcpModule.tcp_create_two_servers(serverPortNumber, secondServerPortNumber, serverPath, serverTransportProtocol)
    else:
        pass
def build_server_get_ports(serverPortNumber, serverPath, counter = None):
    if counter != None:
        tcpModule.tcp_create_two_servers_get_command_send_file(serverPortNumber, serverPath)
    else:
        pass
# tcpModule.tcp_create_two_servers(myServer.portNumber, myServer.portNumber + 1000, myServer.path)
# tcpModule.tcp_create_two_servers_get_command_send_file(myServer.portNumber, myServer.path)


# We need this main method to get inputs from the user from the command line
if __name__ == "__main__":
    # This module will help us to get inputs from user
    import argparse
    
    # This flag will set up the user client first before doing anything else
    # clientSet = False
    
    # To help us access the argumentparser function
    parser = argparse.ArgumentParser()
    
    # Indicating the arguments required to set up client
    parser.add_argument("serverportnumber", type=int)
    parser.add_argument("transportprotocol", type=str)
    
    # Grabbing the string of input arguments for the client
    args = parser.parse_args()
    print(args)
    # Now we can set the values for the client class
    myServer = Server(args.serverportnumber,args.transportprotocol)
    print(myServer.portNumber, myServer.transportProtocol)
    # Only for the put command
    # Running these processes in parallel
    
    if myServer.transportProtocol == 'tcp':
        # tcpModule.tcp_create_two_servers(myServer.portNumber, myServer.portNumber + 1000, myServer.path, myServer.transportProtocol)
        #tcpModule.tcp_create_two_servers_get_command_send_file(myServer.portNumber, myServer.path)
        x = threading.Thread(target= tcpModule.tcp_create_two_servers, args=(myServer.portNumber, myServer.portNumber + 1000, myServer.path, myServer.transportProtocol))
        y = threading.Thread(target= tcpModule.tcp_create_two_servers_get_command_send_file, args=(myServer.portNumber, myServer.path))
        x.start()
        y.start()
        x.join()
        y.join()
    elif myServer.transportProtocol == 'snw':
        x = threading.Thread(target = snwModule.snw_create_two_servers, args=(myServer.portNumber, myServer.portNumber + 1000, myServer.path, myServer.transportProtocol))
        y = threading.Thread(target = snwModule.snw_create_two_servers_get_command_send_file, args=(myServer.portNumber, myServer.portNumber + 1001, myServer.path))
        x.start()
        y.start()
        x.join()
        y.join()
        # pass

    
    

