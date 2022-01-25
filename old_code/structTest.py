import struct
import binascii

payload_len = 3
psecret = 6
step = 14
studentNum = 21

payload = 'hello world\0'
header = [payload_len, psecret, step, studentNum, payload.encode('utf-8')] 
s = struct.Struct('> L L H H 12s')
packed_data = s.pack(*header)

print('Original values:', header)
print('Format string  :', s.format)
print('Uses           :', s.size, 'bytes')
print('Packed Value   :', binascii.hexlify(packed_data))

s_fail = struct.Struct('> L L L H H 12s')

try:
    unpack_fail = s_fail.unpack(packed_data)
except:
    print("an error happend!")

unpacked_data = s.unpack(packed_data)
unpacked_payload_len, unpacked_psecret, unpacked_step, unpacked_studentNum, unpacked_payload, *rest = unpacked_data
print(unpacked_payload)
print(rest)
print('Unpacked Values: ', unpacked_data)

#unpacked_payload_len, unpacked_psecret, unpacked_step, unpacked_studentNum, unpacked_payload= s.unpack(packed_data)
#print(unpacked_payload.decode('utf-8'))