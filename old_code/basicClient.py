# gotta get the socket api
import socket

# Creates a socket, c for client
c = socket.socket()

# We connect to an address, in this case the address is (ip address, port)? not sure
c.connect(('localhost', 9999))

# we're connected to the server, we can ask the user for some input and assign that to name
name = input("Enter your name: ")

# We send over the name, need to send it over as bytes, can't just do as a str, need
# to specify encoding scheme too
c.send(bytes(name, 'utf-8'))

# The client receives anything the server sent over (recv(buffer size)), need to decode after
print(c.recv(1024).decode())