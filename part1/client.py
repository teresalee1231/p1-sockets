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

# Step number is always 1
STEP = 1

# Student ID. TODO: move to utils as global var
SID = 160

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

def stage_a():
    """
    Returns tuple containing (num, len, udp_port, secretA) from step a2.
    Sends "hello world" UDP packet to attu2.cs.washington.edu on port 12235.
    Processes server UDP response.
    """

def stage_b(num, len, udp_port, secretA):
    """
    Returns tuple containing (tcp_port, secretB) from step b2.
    Args: values provided by server from stage_a
    Sends num UDP packets to server on port udp_port, resending if needed.
    Processes all server UDP ack packets for each packet.
    Processes server b2 packet.
    """

def stage_c(tcp_port, secretB):
    """
    Returns tuple containing (num2, len2, secretC, c) from step c2.
    Args: values provided by server from stage_b
    Opens TCP connection to server on port tcp_port.
    Processes server c2 packet.
    """

def stage_d(num2, len2, secretC, c):
    """
    Returns secretD.
    Args: values provided by server from stage_d
    Sends num2 packets to server (on port tcp_port?).
    Processes server d2 packet.
    """

def run_client():
    """
    Runs the client and its stages.
    """
    num, len, udp_port, secretA = stage_a
    tcp_port, secretB = stage_b(num, len, udp_port, secretA)
    num2, len2, secretC, c = stage_c(tcp_port, secretB)
    secretD = stage_d(num2, len2, secretC, c)

if __name__ == '__main__':
    run_client()
