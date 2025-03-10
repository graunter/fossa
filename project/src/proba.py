import serial   #pip install pyserial
import struct
from binascii import hexlify

def modbusCrc(msg:str) -> int:
    crc = 0xFFFF
    for n in range(len(msg)):
        crc ^= msg[n]
        for i in range(8):
            if crc & 1:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc

ser = serial.Serial(port='COM11', baudrate=9600, bytesize=8, parity='N', 
stopbits=1, timeout=0.1, rtscts=False, dsrdtr=False)

adr = range(22, 25)
prj_ver_code = 0x00
open_srv_code = 0x08
freq_code = 0x09
fw_ver_code = 33

access_lvl_user = 0
access_adm_user = 1
access_dev_user = 2

access_pwd_user = [255]*6

cmd_crc = [0, 0]




#command_to_send = "AT+RET\r\n"
#command_to_send = [adr, service_code, access_lvl, access_pwd, cmd_crc]

for test_adr in adr:
    send_dat = sum([[test_adr], [open_srv_code], [access_lvl_user], list(access_pwd_user)], [])
    crc = modbusCrc(send_dat)
    ba = crc.to_bytes(2, byteorder='little')
    send_packet = sum([send_dat, [ba[0]], [ba[1]]], [])
    ser.write(send_packet)
    
    received = ser.read(128)
    if received != b'':
        print(f'\n {test_adr}, {hex(test_adr)}: AOPEN \n')
        print(f'>> {[hex(one) for one in send_packet]}')
        print(f'<< {[hex(one) for one in received]}')

        send_dat = sum([[test_adr], [0x01], [freq_code], list(cmd_crc)], [])
        crc = modbusCrc(send_dat)
        ba = crc.to_bytes(2, byteorder='little')
        send_packet = sum([send_dat, [ba[0]], [ba[1]]], [])        
        ser.write(send_packet)
        resp = ser.read(128)

        print(f'\n {test_adr}, {hex(test_adr)}: frequency')
        print(f'>> {[hex(one) for one in send_packet]}')
        print(f'<< {[hex(one) for one in resp]}')
        freq = int.from_bytes(resp[4:6],byteorder='little', signed=False)
        print(f'{freq/1000}')

        send_dat = sum([[test_adr], [0x01], [fw_ver_code]], [])
        crc = modbusCrc(send_dat)
        ba = crc.to_bytes(2, byteorder='little')
        send_packet = sum([send_dat, [ba[0]], [ba[1]]], [])        
        ser.write(send_packet)
        resp = ser.read(128)

        print(f'\n {test_adr}, {hex(test_adr)}: firmware version')
        print(f'>> {[hex(one) for one in send_packet]}')
        print(f'<< {[hex(one) for one in resp]}')
        ver = resp[4:(4+4)].decode("utf-8")
        print(f'{ver}')
    else:
        print(f'\r{test_adr}: none', end='')