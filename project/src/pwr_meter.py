import re
import serial   #pip install pyserial
from textwrap import wrap
from enum import Enum
import my_const as mconst
from collections import namedtuple


def calc_crc_16_ibm(msg:str) -> int:
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


def create_packet_from_dat(send_dat: list) -> list:
    crc = calc_crc_16_ibm(send_dat)
    ba = crc.to_bytes(2, byteorder='little')
    send_packet = sum([send_dat, [ba[0]], [ba[1]]], [])
    return send_packet


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

class StrData(Enum):
    model = 1
    fw_ver = 2

        
class PwrMeter:
    def __init__(self, adr: int, port: serial.Serial):
        self.adr = adr
        self.port = port
        self.err_cnt = 0

    def link(self, port: serial.Serial):
        self.port = port

    def disconnect(self):
        self.port = None        

    def check_resp_on_adr(adr: int, port: serial.Serial) -> bool:
        send_dat = sum([[adr], [mconst.AOPEN_ID_CMD], [mconst.ACCESS_LVL_USER], list(mconst.ACCESS_PWD_USER)], [])
        send_packet = create_packet_from_dat(send_dat)

        try:
            if not port.is_open:
                port.open()
            port.write(send_packet)
            received = port.read(128)
        except:
            return False

        is_present = True if received != b'' else False

        return is_present


    def rd_str(self, item: StrData):

        # TODO: may be exeption will be better?
        if not self.port:
            return 0, "0"
        
        if not self.port.is_open:
            return 0, "0"    
        
        Msg = namedtuple("Msg", "id, len")

        trans_tbl = { 
              StrData.model: Msg(mconst.MODEL_ID_DATA, 16)  
            , StrData.fw_ver: Msg(mconst.FW_ID_DATA, 4)
        }

        if item not in trans_tbl.keys():
            # TODO:
            pass
        
        send_dat = sum([[self.adr], [mconst.GET_ID_CMD], [trans_tbl[item].id] ], [])
        send_packet = create_packet_from_dat(send_dat)
        self.port.write(send_packet)
        #TODO: read len should d be calculated
        resp = self.port.read(128)

        txt = "NA"

        if resp != b'':
            data_start_pos = 4
            data_end_pos = data_start_pos + trans_tbl[item].len
            txt = resp[data_start_pos:data_end_pos].decode("ansi").rstrip('\0')
            # re.sub('\W+', '', txt)
        else:
            self.err_cnt += 1


        return txt
        




