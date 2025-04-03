import re
import serial   #pip install pyserial
from textwrap import wrap
from enum import auto, Enum
import my_const as mconst
from collections import namedtuple
import threading
import time


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

        self.sem = threading.Semaphore()


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

    def run_request(self, pdu: list, no_resp_fl=False) -> bytes:
        send_packet = create_packet_from_dat(pdu)  

        self.sem.acquire()
        self.port.write(send_packet)
        #TODO: read len should be calculated
        resp = self.port.read(128)
        self.sem.release()             

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

        if no_resp_fl and not resp:
            return
        elif resp == b'':
            raise serial.SerialException("No response from device")
        else:
            if len(resp) < 3:
                raise serial.SerialException("Too short response")
            
            if (RespCode:=resp[1]) == (0x80 + pdu[1]):
                if (ErrCode:=resp[2]) in RespErrCode.keys():
                    txt = RespErrCode[ErrCode]
                else:
                    txt = "Response Err"
                
                raise serial.SerialException(f'{txt}')

            data_start_pos = 4
            data_end_pos = data_start_pos + 2

            in_data = resp[data_start_pos:len(resp)-2]
            return in_data
    
    
    def rd_pwi_record(self, idx: int):
        # cmd = mconst.LISTINIT_ID_CMD
        # obj_id = mconst.PWI_ID_DATA
        # send_dat = [self.adr, cmd, obj_id]
        # in_dat = self.run_request(send_dat, True)

        # time.sleep(2)   

        cmd = mconst.getPWIRecord_ID_CMD
        obj_id = mconst.PWI_ID_DATA

        b0 = idx & 0xFF
        b1 = (idx >> 8) & 0xFF

        send_dat = [self.adr, cmd, obj_id, b0, b1]

        in_dat = self.run_request(send_dat)

        
        # date_lst, rest = self.decode_rtc_to_liststr(in_dat)
        minutes = str(in_dat[0]).zfill(2)
        hours = str(in_dat[1]).zfill(2)
        days = str(in_dat[2]).zfill(2)
        months_lst = ['ERR', 'JAN' , 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
        months_idx = in_dat[3]
        months = str(months_lst[months_idx]) if months_idx < len(months_lst) else 'Err'                
        years = str(2000 + in_dat[4])
 
        date_txt = ':'.join( [minutes, hours, days, months, years] )

        rest = in_dat[5:]

        P_sum_in = rest[0:3].hex().removesuffix('F')
        P_sum_out = rest[4:7].hex().removesuffix('F')
        # Q_sum_in = rest[8:11].hex().removesuffix('F')
        # Q_sum_out = rest[12:15].hex().removesuffix('F')

        # end_fl = rest[16]
        end_fl = rest[8]

        # hour_record = [date_txt, str(P_sum_in), str(P_sum_out), str(Q_sum_in), str(Q_sum_out), str(end_fl)]
        hour_record = [date_txt, str(P_sum_in), str(P_sum_out), str(end_fl)]
        
        return hour_record
            


    def rd_total_tax_count(self) ->int:
        cmd = mconst.GETLISTNE_ID_CMD
        obj_id = mconst.PWI_ID_DATA

        send_dat = [self.adr, cmd, obj_id]

        in_dat = self.run_request(send_dat)

        in_digit = int.from_bytes(in_dat, byteorder='little', signed=True)
        
        return in_digit

    def rd_total_tax_current(self) ->int:
        cmd = mconst.GETCURINDEX_ID_CMD
        obj_id = mconst.PWI_ID_DATA

        send_dat = [self.adr, cmd, obj_id]

        in_dat = self.run_request(send_dat)

        in_digit = int.from_bytes(in_dat, byteorder='little', signed=True)
        
        return in_digit



    def rd_tax_tbl(self, month_num: int):

        # TODO: may be exeption will be better?
        if (not self.port) or (not self.port.is_open):
            return [ ["Port is not avaliable"], ['--:--', '   -   ', '   -   ', '   -   ', '   -   '] ]
        

        if month_num+1 not in range(13):
            return ["Wrong month number"]

        req_id = mconst.TAX_RATE_JAN_ID_DATA + month_num

        send_dat = sum([[self.adr], [mconst.GET_ID_CMD], [req_id] ], [])
        send_packet = create_packet_from_dat(send_dat)

        self.sem.acquire()
        self.port.write(send_packet)
        #TODO: read len should be calculated
        resp = self.port.read(128)
        self.sem.release()


        taxt_tbl = []

        if resp != b'':
            txt = ""
            if len(resp) < 70:
                return ["Err len in resp"]
            
            # if (RespCode:=resp[1]) == (0x80 + mconst.GET_ID_CMD):
            #     if ErrCode:=resp[2] in RespErrCode.keys():
            #         txt = RespErrCode[ErrCode]
            #     else:
            #         txt = "Response Err"
                
            #     return txt

            data_start_pos = 4
            data_end_pos = data_start_pos + 64
            line_size = 4

            in_dat_full = resp[data_start_pos:data_end_pos]

            for idx_cnt in range(16):

                in_dat = in_dat_full[line_size*idx_cnt : line_size*(idx_cnt+1)]

                hours   =  '-' if 0xFF == in_dat[0] else str(in_dat[0]).zfill(2)
                minutes =  '-' if 0xFF == in_dat[1] else str(in_dat[1]).zfill(2)

                lo_nible = 0x0F & in_dat[2]
                work_day = '-' if 0x0F == lo_nible else lo_nible + 1
                  
                hi_nible = (0xF0 & in_dat[2]) >> 4
                holl_day = '-' if 0x0F == hi_nible else hi_nible + 1

                lo_nible = 0x0F & in_dat[2]
                sat_day = '-' if 0x0F == lo_nible else lo_nible + 1
                  
                hi_nible = (0xF0 & in_dat[2]) >> 4
                san_day = '-' if 0x0F == hi_nible else hi_nible + 1


                this_line = [ f'{hours}:{minutes}', str(work_day) , str(holl_day), str(sat_day), str(san_day) ]

                taxt_tbl.append(this_line)
        else:
            taxt_tbl = [[] for x in range(5)]

        return taxt_tbl
    
    def decode_rtc_to_liststr(self, in_dat: bytes):
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
        return [seconds, minutes, hours, doweek, days, months, years], in_dat[7:]

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

        self.sem.acquire()
        self.port.write(send_packet)
        #TODO: read len should be calculated
        resp = self.port.read(128)
        self.sem.release()

        txt = "NA"



        if resp != b'':
            txt = ""
            if len(resp) < 5:
                return "Err len in resp" 
            
            if (RespCode:=resp[1]) == (0x80 + mconst.GET_ID_CMD):
                if (ErrCode:=resp[2]) in RespErrCode.keys():
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
                time_list, _ = self.decode_rtc_to_liststr(in_dat)
                txt = ':'.join(time_list)
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
        



