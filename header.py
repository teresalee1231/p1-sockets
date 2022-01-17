from pyexpat import ParserCreate
import struct
import binascii
import socket

# payload_len = 3
# psecret = 0
# client step alwauys 1
# step = 1
# student_num = 617
# checksum = 0

# udpheader = struct.pact(!)


class header:
  def __init__(self, payload_len, psecret, step, student_num):
    self.payload_len = payload_len
    self.psecret = psecret
    self.step = step
    self.student_num = student_num

  def create_header(self):
    self.



