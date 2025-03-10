import serial   #pip install pyserial
from textwrap import wrap

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

class AccessLvl:
    pass

class Data:
    def __init__(self):
        value_type = 0
        value = bytearray()
        value_len = 0

    def get(self, ObjUID: int):
        version = 0
        if ObjUID == 0:
            if (self.value_len != 4) or (self.value_type==0) or (len(self.value) != 4):
                #TODO: 
                pass
            else:
                version = int.from_bytes(self.value, byteorder='big', signed=False)
        else:
            #TODO
            pass
        return version

    def set(self, ObjUID, val: bytearray):
        pass
        
class Counter:
    def __init__(self, adr: int, port: serial.Serial):
        self.adr = adr
        self.port = port
    
    def read_version(self):
        send_dat = sum([[self.adr], [0x01], [0]], [])
        crc = modbusCrc(send_dat)
        ba = crc.to_bytes(2, byteorder='little')
        send_packet = sum([send_dat, [ba[0]], [ba[1]]], [])        
        self.port.write(send_packet)
        resp = self.port.read(128)
        version_num = int.from_bytes(resp[4:9],byteorder='little', signed=False)
        version_str = ".".join(wrap(str(version_num), width=3))

        return version_num, version_str



