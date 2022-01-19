# gotta get the socket api
import socket
# import utility functions; call with utils.get_packet_header()
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils.helper
import random

# Set max number of clients that can be served
MAX_CONNECTIONS = 10

# Set host name and port used by server
HOST = 'localhost'
PORT = 9999
# (?) for attu
# HOST = 'attu2.cs.washington.edu'
# PORT = 12235

# Student ID
SID = 160


def stage_a(resp):
    # recieve client packet
    # verifying ????
    payload_len = resp[payload_len]
    p_secret = resp[p_secret]
    payload = resp[payload]

    # using random
    num = random.randint(5) #(????)
    len = random.randint(5)
    udp_port = random.randint(5)
    secretA = random.randint(5)

    # send a response

    ## do the server sending stuff lol

    #stage a


def stage_b():
    # transmit nump UDP packets on port udp_port (from stage a)


#     #stage b

# def stage_c():
#     #stage c

# def stage_d():
#     #stage d

def old_server():
    """
    Old echoServer code.
    """
    # Creates a socket, s for server
    # AF_INET is just what we use,
    # SOCK_DGRAM = UDP, SOCK_STREAM = TCP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print('Socket Created!')

    # binds the socket to the address (ip address, port)? still not sure
    # for localhost
    s.bind(('localhost', 9999))

    # for attu. is gethostname necessary?
    # https://docs.python.org/2/howto/sockets.html
    # Might need to keep it as gethostname(), tried doing specific didnt work,
    # In here it explains also why we should use gethostname()
    
    # print(socket.gethostname())
    # s.bind((socket.gethostname(), 12235))


    # doesn't need to specify a number, the argument is "backlog" meaning
    # the number of unaccepted connections that the system will
    # allow before refusing new connections, basically how many can be connected?
    s.listen(MAX_CONNECTIONS)
    print('waiting for connections')

    c, addr = s.accept()
    print("Connected with ", addr)
    c.send(bytes("You've connected to the server!", 'utf-8'))

    while True:
        echo = c.recv(1024).decode()
        print("Client sent: ", echo)
        c.send(bytes(echo, 'utf-8'))




def run_server():
    """
    Runs the server.
    """
    old_server()

if __name__ == '__main__':
    run_server()



