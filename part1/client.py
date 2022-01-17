# gotta get the socket api
import socket
# import utility functions; call with utils.helper.get_packet_header()
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils.helper

# Set host name and port used by server
HOST = 'localhost'
PORT = 9999
# HOST = 'attu2.cs.washington.edu'
# PORT = 12235

def old_client():
    """
    Old echoClient code.
    """
    # Creates a socket, c for client
    c = socket.socket()

    # We connect to an address, in this case the address is (ip address, port)? not sure
    # for local
    c.connect((HOST, PORT))

    utils.helper.get_packet_header(0,0,0,0)

    print(c.recv(1024).decode())
    while True:
        echo = input("Enter anything and it will be echo'd back from server: ")
        c.send(bytes(echo, 'utf-8'))
        print(c.recv(1024).decode())

def run_client():
    """
    Runs the client and its stages.
    """
    old_client()

if __name__ == '__main__':
    run_client()
