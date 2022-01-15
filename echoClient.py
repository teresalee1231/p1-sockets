# gotta get the socket api
import socket

# Creates a socket, c for client
c = socket.socket()

# We connect to an address, in this case the address is (ip address, port)? not sure
c.connect(('localhost', 9999))
print(c.recv(1024).decode())
while True:
    echo = input("Enter anything and it will be echo'd back from server: ")
    c.send(bytes(echo, 'utf-8'))
    print(c.recv(1024).decode())