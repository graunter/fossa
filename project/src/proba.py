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

dev_port = '/dev/ttyUSB0'
dev_port = 'COM15'

ser = serial.Serial(port=dev_port, baudrate=9600, bytesize=8, parity='N', 
stopbits=1, timeout=0.1, rtscts=False, dsrdtr=False)

adr = range(10, 25)
prj_ver_code = 0x00
open_srv_code = 0x08
freq_code = 0x09
fw_ver_code = 33
rtc_code = 14

access_lvl_user = 0
access_adm_user = 1
access_dev_user = 2

access_pwd_user = [255]*6

cmd_crc = [0, 0]


def decode_rtc(resp: list):
    data_start_pos = 4
    data_end_pos = data_start_pos + 7

    in_dat = resp[data_start_pos:data_end_pos]    

    seconds = str(in_dat[0]).zfill(2)
    minutes = str(in_dat[1]).zfill(2)
    hours = str(in_dat[2]).zfill(2)
    dow = ['ERR', 'SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']
    doweek_idx = in_dat[3]
    doweek = str(dow[doweek_idx]) if doweek_idx < len(dow) else 'Err'
    days = str(in_dat[4]).zfill(2)
    months_lst = ['ERR', 'JAN' , 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    months_idx = in_dat[5]
    months = str(months_lst[months_idx]) if months_idx < len(months_lst) else 'Err'                
    years = str(2000 + in_dat[6])
    txt = ':'.join([seconds, minutes, hours, doweek, days, months, years])
    return txt


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


        # test for RTC
        for _ in range(1):
            send_dat = sum([[test_adr], [0x01], [rtc_code]], [])
            crc = modbusCrc(send_dat)
            ba = crc.to_bytes(2, byteorder='little')
            send_packet = sum([send_dat, [ba[0]], [ba[1]]], [])        
            ser.write(send_packet)
            resp = ser.read(128)

            print(f'\n {test_adr}, {hex(test_adr)}: RTC')
            print(f'>> {[hex(one) for one in send_packet]}')
            print(f'<< {[hex(one) for one in resp]}')
            print(f'dec: {list(resp)}')
            txt = decode_rtc(resp)
            print(f'{txt}')


    else:
        print(f'\r{test_adr}: none', end='')