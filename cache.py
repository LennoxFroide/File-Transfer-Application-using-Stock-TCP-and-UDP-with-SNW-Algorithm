import tcp_transport as tcpModule
import snw_transport as snwModule
from socket import *

# This set up the cache 
class Cache:
    """This class establishes the cache."""

    def __init__(self, cacheportnumber, serverip, serverport, transportprotocol):
        # Setting the port that cache will run on
        self.cachePortNumber = cacheportnumber
        # Saving the server's ip
        self.serverIp = serverip
        # Saving the server's port number
        self.serverPort =serverport
        # Setting the transport protocol that the cache will use
        self.transportProtocol = transportprotocol
        # The directory to cache
        self.path= 'cache_fl'



# We need this main method to get inputs from the user from the command line
if __name__ == "__main__":
    # This module will help us to get inputs from user
    import argparse
    
    # To help us access the argumentparser function
    parser = argparse.ArgumentParser()
    
    # Indicating the arguments required to set up client
    parser.add_argument("cacheportnumber", type=int)
    parser.add_argument("serverip", type=str)
    parser.add_argument("serverportnumber", type=int)
    parser.add_argument("transportprotocol", type=str)
    
    # Grabbing the string of input arguments for the client
    args = parser.parse_args()
    print(args)
    # Now we can set the values for the client class
    myCache = Cache(args.cacheportnumber, args.serverip, args.serverportnumber, args.transportprotocol)

    # By default the server will be a receiver
    if myCache.transportProtocol == 'tcp':
        # We establish a tcp welcoming door        # Receives client's get command  # Send get to server
        tcpModule.tcp_create_two_caches_get_command(myCache.cachePortNumber, myCache.cachePortNumber + 10, myCache.path, myCache.serverIp, myCache.serverPort + 100)
    elif myCache.transportProtocol == 'snw':
        # UDP Socket to receive files from server 
        cacheSocketSNW = socket(SOCK_DGRAM)
        snwModule.snw_create_two_caches_get_command(myCache.cachePortNumber, myCache.cachePortNumber + 10, myCache.path, myCache.serverIp, myCache.serverPort, cacheSocketSNW)
    else:
        pass
