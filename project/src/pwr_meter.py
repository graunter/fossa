import re
import serial   #pip install pyserial
from textwrap import wrap
from enum import auto, Enum
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

# class StrData(Enum):
class ReqId(Enum):
    model = auto()
    fw_ver = auto()
    serial_num = auto()
    prod_date = auto()
    rtc = auto()
    cur_rate = auto()
    i_scale = auto()
    v_scale = auto()


#class PacDecData(Enum):
    Active_imp_e = auto()
    Active_imp_e_1  = auto()
    Active_imp_e_2 = auto()
    Active_imp_e_3 = auto()
    Active_imp_e_4 = auto()
    Active_imp_e_5 = auto()
    Active_imp_e_6 = auto()
    Active_imp_e_7 = auto()
    Active_imp_e_8 = auto()
    ReAct_imp_e = auto()
    ReAct_imp_e_1  = auto()
    ReAct_imp_e_2 = auto()
    ReAct_imp_e_3 = auto()
    ReAct_imp_e_4 = auto()
    ReAct_imp_e_5 = auto()
    ReAct_imp_e_6 = auto()
    ReAct_imp_e_7 = auto()
    ReAct_imp_e_8 = auto()
        
    Active_exp_e = auto()
    Active_exp_e_1  = auto()
    Active_exp_e_2 = auto()
    Active_exp_e_3 = auto()
    Active_exp_e_4 = auto()
    Active_exp_e_5 = auto()
    Active_exp_e_6 = auto()
    Active_exp_e_7 = auto()
    Active_exp_e_8 = auto()
    ReAct_exp_e = auto()
    ReAct_exp_e_1  = auto()
    ReAct_exp_e_2 = auto()
    ReAct_exp_e_3 = auto()
    ReAct_exp_e_4 = auto()
    ReAct_exp_e_5 = auto()
    ReAct_exp_e_6 = auto()
    ReAct_exp_e_7 = auto()
    ReAct_exp_e_8 = auto()

#class WordData(Enum):
    ActPwrA = auto()
    ActPwrB = auto()
    ActPwrC = auto()
    ActPwr = auto()
    ReActPwrA = auto()
    ReActPwrB = auto()
    ReActPwrC = auto()
    ReActPwr = auto()
    PwrA = auto()
    PwrB = auto()
    PwrC = auto()
    Pwr = auto()

#class CatenaData(Enum):
    UPhA = auto()
    UPhB = auto()
    UPhC = auto()
    IPhA = auto()
    IPhB = auto()
    IPhC = auto()

    AIE= auto()       

class DType(Enum):
    StrData = auto() 
    PacDecData = auto() 
    DigitData = auto() 
    RtcData = auto()
    VScaleData = auto()
    IScaleDate = auto()



        
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
        send_dat = sum([[adr], [mconst.AOPEN_ID_CMD], [mconst.ACCESS_ADM_USER], list(mconst.ACCESS_PWD_USER)], [])
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


    def rd_str(self, item: ReqId):

        # TODO: may be exeption will be better?
        if not self.port:
            return 0, "0"
        
        if not self.port.is_open:
            return 0, "0"    
        
        Msg = namedtuple("Msg", "dtype id len scale", defaults=(None, None, None, 1))

        trans_str_tbl = { 
              ReqId.model: Msg(DType.StrData, mconst.MODEL_ID_DATA, 14)  
            , ReqId.fw_ver: Msg(DType.StrData, mconst.FW_ID_DATA, 4)
            , ReqId.serial_num: Msg(DType.DigitData, mconst.SN_ID_DATA, 4)
            , ReqId.prod_date: Msg(DType.RtcData, mconst.PROD_DATE_ID_DATA, 7)
            , ReqId.cur_rate: Msg(DType.DigitData, mconst.RATE_ID_DATA, 1)
            , ReqId.v_scale: Msg(DType.VScaleData, mconst.SCALE_ID_DATA, 4)
            , ReqId.i_scale: Msg(DType.IScaleDate, mconst.SCALE_ID_DATA, 4)                        
            
            , ReqId.rtc: Msg(DType.RtcData, mconst.RTC_ID_DATA, 7)
            , ReqId.UPhA: Msg(DType.DigitData, mconst.UA_ID_DATA, 3, 1000)

            , ReqId.IPhA: Msg(DType.DigitData, mconst.IA_ID_DATA, 3, 1000)

            , ReqId.PwrA: Msg(DType.DigitData, mconst.PA_ID_DATA, 4, 1000)  

            , ReqId.ActPwrA: Msg(DType.DigitData, mconst.APA_ID_DATA, 4, 1000)      

            , ReqId.ActPwr: Msg(DType.DigitData, mconst.AP_ID_DATA, 4, 1000)      

            , ReqId.Active_imp_e: Msg(DType.PacDecData, mconst.AIE_ID_DATA, 4)   
             


                              

        }

        RespErrCode = {
            1: "ILLEGAL_FUNCTION"
            , 2: "ILLEGAL_DATA_ADDRESS"
            , 3: "ILLEGAL_DATA_VALUE"
            , 4: "SLAVE_DEVICE_FAILURE"
            , 5: "ACKNOWLEDGE"
            , 6: "SLAVE_DEVICE_BUSY"
            , 7: "MEMORY_ACCESS_ERROR"
            , 8: "SESSION_CLOSED"
            , 9: "ACCESS_DENIED"
            , 10: "ERROR_CRC"
            , 11: "FRAME_INCORRECT"
            , 12: "JUMPER_ABSENT"
            , 13: "PASSW_INCORRECT"
            , 14: "ACCESS_BLOCKED"
        }

        if item not in trans_str_tbl.keys():
            # TODO:
            raise ValueError('Request from GUI is not supported!')

        this_msg = trans_str_tbl[item]
        
        send_dat = sum([[self.adr], [mconst.GET_ID_CMD], [this_msg.id] ], [])
        send_packet = create_packet_from_dat(send_dat)
        self.port.write(send_packet)
        #TODO: read len should be calculated
        resp = self.port.read(128)

        txt = "NA"



        if resp != b'':
            txt = ""
            if len(resp) < 5:
                return "Err len in resp" 
            
            if (RespCode:=resp[1]) == (0x80 + mconst.GET_ID_CMD):
                if ErrCode:=resp[2] in RespErrCode.keys():
                    txt = RespErrCode[ErrCode]
                else:
                    txt = "Response Err"
                
                return txt

            data_start_pos = 4
            data_end_pos = data_start_pos + this_msg.len

            in_dat = resp[data_start_pos:data_end_pos]
            if this_msg.dtype == DType.StrData:
                i = in_dat.find(b'\x00')
                if i == -1:
                    re_in_dat = in_dat
                else:
                    re_in_dat = in_dat[:i]
                in_str = re_in_dat.decode("utf-8")
                txt = in_str.rstrip('\0')
            elif this_msg.dtype == DType.DigitData:
                digit = resp[data_start_pos:data_end_pos]
                in_digit = int.from_bytes(digit, byteorder='little', signed=True)
                in_real = in_digit / this_msg.scale if this_msg.scale != 1 else in_digit
                txt = str(in_real)
            elif this_msg.dtype == DType.PacDecData:
                digit = resp[data_start_pos:data_end_pos]
                in_digit = digit.hex().removesuffix('F')
                in_real = in_digit[-1:this_msg.scale:-1] + '.' + in_digit[this_msg.scale:0:-1]
                txt = str(in_real)   
            elif this_msg.dtype == DType.RtcData:
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
            elif this_msg.dtype == DType.VScaleData:
            #     in_digit = in_dat[0:1]
            #     digit = int.from_bytes(in_digit, byteorder='little', signed=False)
            #     txt = str(digit)
                txt = "Access denied"
            elif this_msg.dtype == DType.IScaleData:
            #     in_digit = in_dat[2:3]
            #     digit = int.from_bytes(in_digit, byteorder='little', signed=False)
            #     txt = str(digit)   
                txt = "Access denied"             
            else:
                txt = "Err"
        else:
            self.err_cnt += 1


        return txt
        




