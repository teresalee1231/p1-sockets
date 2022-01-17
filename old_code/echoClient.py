# gotta get the socket api
import socket

# Creates a socket, c for client
c = socket.socket()

# We connect to an address, in this case the address is (ip address, port)? not sure
# for local
# c.connect(('localhost', 9999))

# for attu
c.connect(('attu2.cs.washington.edu', 12235))

print(c.recv(1024).decode())
while True:
    echo = input("Enter anything and it will be echo'd back from server: ")
    c.send(bytes(echo, 'utf-8'))
    print(c.recv(1024).decode())