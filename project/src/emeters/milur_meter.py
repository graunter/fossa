
import time
import serial   #pip install pyserial
import milur_const as mconst
from  emeters.milur_meter_const import *
from collections import namedtuple
import threading
from datetime import datetime


def calc_crc_16_ibm(msg) -> int:
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
    send_packet = send_dat + [ba[0]] + [ba[1]]
    return send_packet



class ProtocolException(Exception):
    pass
        
class PwrMeter:

    def __init__(self, adr: int, port: serial.Serial, sem: threading.Semaphore):
        self.adr = adr
        self.port = port
        self.err_cnt = 0
        self.sem = sem


    def link(self, port: serial.Serial, sem: threading.Semaphore):
        self.port = port
        self.sem = sem

    def disconnect(self):
        self.port = None    


    # TODO: this check is not protected by semaphore
    @staticmethod
    def check_resp_on_adr(adr: int, port: serial.Serial, sem: threading.Semaphore = None) -> bool:
        send_dat = sum([[adr], [mconst.AOPEN_ID_CMD], [mconst.ACCESS_ADM_USER], list(mconst.ACCESS_PWD_USER)], [])
        send_packet = create_packet_from_dat(send_dat)

        #TODO: fast stub
        if not sem:
            sem = threading.Semaphore()

        try:
            with sem:
                if not port.is_open:
                    port.open()
                port.write(send_packet)
                received = port.read(128)
        except:
            return False

        is_present = True if received != b'' else False

        return is_present
    
    # TODO: an interface obj for lvl is required
    def login(self, lvl: int, pwd: list):
        if len(pwd) > mconst.PWD_LEN:
            raise ProtocolException("Very long password")
        else:
            pwd = pwd[:mconst.PWD_LEN] + [0 for _ in range(mconst.PWD_LEN - len(pwd))]

        send_dat = [self.adr] + [mconst.AOPEN_ID_CMD] + [lvl] + pwd


        # TODO: There is no clear secription for 'open' respose
        # may be standard error processing over exeption will be enought
        send_packet = create_packet_from_dat(send_dat) 

        with self.sem:
            self.port.write(send_packet)
            #TODO: read len should be calculated
            # adr id_cmd crc1 crc2
            resp = self.port.read(10)
            
            if len(resp) != 4:
            #     raise ProtocolException("Too short response for login")
                pass
            




    def logout(self) -> bool:
        send_dat = [self.adr] + [mconst.ARELEASE_ID_CMD]

        # TODO: There is no clear secription for 'releare' respose
        # may be standard error processing over exeption will be enought
        self.run_request(send_dat, True)


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
        
    def run_request(self, pdu: list, no_resp_fl=False) -> bytes:
        send_packet = create_packet_from_dat(pdu)  

        with self.sem:
            self.port.reset_input_buffer()
            self.port.write(send_packet)
            self.port.flush()
            #TODO: read len should be calculated
            # adr id_cmd _id_obj len crc1 crc2

            long_time_commands = { mconst.SETRTC_ID_CMD:0.1 }
            if (tx_cmd_id := pdu[1]) in long_time_commands.keys():
                time.sleep(long_time_commands[tx_cmd_id])

            resp = self.port.read(6)

            if no_resp_fl and not resp:
                return
            
            if resp == b'':
                raise ProtocolException("No response from device")

            if resp[0] != pdu[0]:
                raise ProtocolException('Wrong reply adress') 

            
            
            if len(resp) < 3:
                raise ProtocolException("Too short response")
            
            in_data = []
            
            resp_with_len = [
                mconst.GET_ID_CMD
                , mconst.LISTINIT_ID_CMD
                , mconst.GETLISTNE_ID_CMD
                , mconst.GETCURINDEX_ID_CMD
                , mconst.getPWIRecord_ID_CMD
                , mconst.GET_ENTALIST_ID_CMD]

            if tx_cmd_id in resp_with_len:
                if (resp_code:=resp[1]) == (0x80 + tx_cmd_id):
                    if (ErrCode:=resp[2]) in self.RespErrCode.keys():
                        txt = self.RespErrCode[ErrCode]
                    else:
                        txt = "Response Err"
                    
                    raise ProtocolException(f'{txt}')
                
                if resp_code != tx_cmd_id:
                    raise ProtocolException('Wrong reply code')  
 
                next_read_size = resp[3]

                resp_next = self.port.read(next_read_size)   

                if len(resp_next) != next_read_size:
                    raise ProtocolException('Respons is not complete')  
                
                #TODO: set timeout to 3.5 chars and read no sumbols
                # resp_extra = self.port.read(3)
                # if resp_extra:
                #     raise ProtocolException(f'Extra data on line: {str(resp_extra)}')

                resp = resp + resp_next

                crc = calc_crc_16_ibm(resp[0:-2])
                ba = crc.to_bytes(2, byteorder='little')
        
                data_start_pos = 4

                if (ba[0] != resp[-2]) or (ba[1] != resp[-1]):
                    if resp[1] == mconst.GET_COLLECTION_ID_CMD:
                        raise ProtocolException("Crc mismatch")
                else:
                    in_data = resp[data_start_pos:len(resp)-2]

            elif tx_cmd_id == mconst.GET_COLLECTION_ID_CMD:
                if (resp_code:=resp[1]) == (0x80 + tx_cmd_id):
                    if (ErrCode:=resp[2]) in self.RespErrCode.keys():
                        txt = self.RespErrCode[ErrCode]
                    else:
                        txt = "Response Err"
                    
                    raise ProtocolException(f'{txt}')
 
                if resp_code != tx_cmd_id:
                    raise ProtocolException('Wrong reply code')  
                
                next_read_size = resp[3] + 1
                resp_next = self.port.read(next_read_size)   

                #TODO: set timeout to 3.5 chars and read no sumbols
                # resp_extra = self.port.read(3)
                # if resp_extra:
                #     raise ProtocolException(f'Extra data on line: {str(resp_extra)}')  
                
                resp = resp + resp_next

                crc = calc_crc_16_ibm(resp[0:-2])
                ba = crc.to_bytes(2, byteorder='little')
        
                data_start_pos = 4

                if (ba[0] != resp[-2]) or (ba[1] != resp[-1]):
                    #TODO: the overall packet seem good
                    # in_data = resp[data_start_pos:len(resp)-1]
                    pass
                else:
                    in_data = resp[data_start_pos:len(resp)-2]

                              
            elif pdu[1] == mconst.SETRTC_ID_CMD:
                if (resp_code:=resp[1]) == (0x80 + tx_cmd_id):
                    if (ErrCode:=resp[2]) in self.RespErrCode.keys():
                        txt = self.RespErrCode[ErrCode]
                    else:
                        txt = "Response Err"
                
                    raise ProtocolException(f'{txt}')
                
            else:
                in_data = []


        return in_data
    
    def wr_rtc(self, dt: datetime):
        cmd = mconst.SETRTC_ID_CMD
        obj_id = 14
        Seconds = dt.second
        Minutes = dt.minute
        Hours = dt.hour
        DayInWeek = dt.weekday()+2
        if DayInWeek>7:
            DayInWeek = DayInWeek - 7
        Day = dt.day
        Month = dt.month
        Year = dt.year-2000

        send_dat = [self.adr, cmd, obj_id, Seconds, Minutes, Hours, DayInWeek, Day, Month, Year]  
        in_dat = self.run_request(send_dat)


    def rd_split(self) -> list:

        cmd = mconst.GET_COLLECTION_ID_CMD
        obj_id = 13
        send_dat = [self.adr, cmd, obj_id, 1, 0]        
        in_dat = self.run_request(send_dat)

        dlen = 4
        records = []
        dat = in_dat
        for cnt in range(18):
            records.append( self.decode_PacDec_to_str(dat[cnt*dlen:(cnt+1)*dlen], 3) )

        energy_lst  = [str(item) for item in records]

        dat = in_dat[(cnt+1)*dlen:]

        dlen = 3
        records = []
        for cnt in range(6):
            records.append( digit := int.from_bytes(dat[cnt*dlen:(cnt+1)*dlen], byteorder='little', signed=True)/1000) 

        vA, vB, vC, iA, iB, iC = [str(item) for item in records]

        dat = in_dat[(cnt+1)*dlen:]

        dlen = 4
        records = []        
        for cnt in range(9):
            records.append( self.decode_PacDec_to_str(dat[cnt*dlen:(cnt+1)*dlen], 3) )

        pwr_lst = [str(item) for item in records]

        
        dat = dat[(cnt+1)*dlen:]

        freq = str(int.from_bytes(dat[0:2], byteorder='little', signed=False)/1000)
        tax = str(int.from_bytes(dat[2:3], byteorder='little', signed=False))
        time, _ = self.decode_rtc_to_liststr(dat[3:3+7])
        model = self.decode_str_to_str(dat[10:10+20])
        fw_ver = self.decode_str_to_str(dat[30:30+4])
        v_bat = self.decode_word_to_str(dat[34:34+2], 1000)
        crc = self.decode_word_to_str(dat[36:36+2])
        load = str(int.from_bytes(dat[38:38+1], byteorder='little', signed=False))
        idm = str(int.from_bytes(dat[39:39+1], byteorder='little', signed=False))


        dat = dat[40:]

        dlen = 2
        records = []        
        for cnt in range(8):
            records.append( self.decode_word_to_str(dat[cnt*dlen:(cnt+1)*dlen]) )

        pwr_fact_lst = [str(item) for item in records]
  
        dat = dat[(cnt+1)*dlen:]

        dlen = 2
        records = []        
        for cnt in range(3):
            records.append( self.decode_word_to_str(dat[cnt*dlen:(cnt+1)*dlen]) )

        ph_angle_lst =  [str(item) for item in records]

        dat = dat[(cnt+1)*dlen:]

        lcd =  self.decode_str_to_str(dat[0:3])
        phase = str(int.from_bytes(dat[3:4], byteorder='little', signed=False))


        load = str(int.from_bytes(dat[38:38+1], byteorder='little', signed=False))

        return energy_lst + [vA, vB, vC, iA, iB, iC] + pwr_lst + [freq, tax, time, model, fw_ver, v_bat, crc, load, id ] + pwr_fact_lst + ph_angle_lst + [lcd, phase]


    def rd_momentum(self) -> list:
        cmd = mconst.GET_COLLECTION_ID_CMD
        obj_id = 2
        send_dat = [self.adr, cmd, obj_id, 1, 0]        
        in_dat = self.run_request(send_dat)

        dlen = 4
        records = []
        dat = in_dat
        for cnt in range(12):
            records.append( self.decode_PacDec_to_str(dat[cnt*dlen:(cnt+1)*dlen], 3) )

        pA, pB, pC, pSum, qA, qB, qC, qSum, tA, tB, tC, tSum = [str(item) for item in records]

        dat = in_dat[(cnt+1)*dlen:]

        dlen = 3
        records = []
        for cnt in range(6):
            records.append( digit := int.from_bytes(dat[cnt*dlen:(cnt+1)*dlen], byteorder='little', signed=True)/1000) 

        vA, vB, vC, iA, iB, iC = [str(item) for item in records]


        dat = dat[(cnt+1)*dlen:]

        freq = str(int.from_bytes(dat[0:2], byteorder='little', signed=False)/1000)
        tax = str(int.from_bytes(dat[2:3], byteorder='little', signed=False))
        time, _ = self.decode_rtc_to_liststr(dat[3:3+7])

        return [pA, pB, pC, pSum, qA, qB, qC, qSum, tA, tB, tC, tSum, vA, vB, vC, iA, iB, iC, freq, tax] + [':'.join( time )]

    
    def rd_d_tax_current(self) ->int:
        cmd = mconst.GETCURINDEX_ID_CMD
        obj_id = mconst.DAYS_PWR_ID_DATA
        send_dat = [self.adr, cmd, obj_id]
        in_dat = self.run_request(send_dat)
        in_digit = int.from_bytes(in_dat, byteorder='little', signed=True)  
        return in_digit
    
    def rd_d_tax_total(self) ->int:
        cmd = mconst.GETLISTNE_ID_CMD
        obj_id = mconst.DAYS_PWR_ID_DATA
        send_dat = [self.adr, cmd, obj_id]
        in_dat = self.run_request(send_dat)
        in_digit = int.from_bytes(in_dat, byteorder='little', signed=True)
        return in_digit
    
    def rd_d_record(self, idx: int):

        cmd = mconst.GET_ENTALIST_ID_CMD
        obj_id = mconst.DAYS_PWR_ID_DATA

        b0 = idx & 0xFF
        b1 = (idx >> 8) & 0xFF

        send_dat = [self.adr, cmd, obj_id, b0, b1]

        in_dat = self.run_request(send_dat)

        date_lst, rest = self.decode_timesec_to_liststr(in_dat)
 
        date_txt = ':'.join( date_lst )

        scale = 1
        pwr_lst = []
        for i in range(8*4 + 4):
            real = self.decode_PacDec_to_str(rest[0:4], 2)
            pwr_lst.append(real)
            rest = rest[4:]

        if len(rest) != 0: 
            raise serial.SerialException(f'too long input message')

        hour_record = [date_txt] + pwr_lst
        
        return hour_record
    

    def rd_m_tax_current(self) ->int:
        cmd = mconst.GETCURINDEX_ID_CMD
        obj_id = mconst.MONTHS_PWR_ID_DATA
        send_dat = [self.adr, cmd, obj_id]
        in_dat = self.run_request(send_dat)
        in_digit = int.from_bytes(in_dat, byteorder='little', signed=True)
        return in_digit
    

    def rd_m_tax_total(self) ->int:
        cmd = mconst.GETLISTNE_ID_CMD
        obj_id = mconst.MONTHS_PWR_ID_DATA
        send_dat = [self.adr, cmd, obj_id]
        in_dat = self.run_request(send_dat)
        in_digit = int.from_bytes(in_dat, byteorder='little', signed=True)
        return in_digit

    def rd_m_record(self, idx: int):
        obj_id = mconst.MONTHS_PWR_ID_DATA
        cmd = mconst.GET_ENTALIST_ID_CMD

        b0 = idx & 0xFF
        b1 = (idx >> 8) & 0xFF

        send_dat = [self.adr, cmd, obj_id, b0, b1]
        in_dat = self.run_request(send_dat)

        date_lst, rest = self.decode_timesec_to_liststr(in_dat)
        date_txt = ':'.join( date_lst )
       
        scale = 2
        pwr_lst = []
        for i in range(8*4 + 4):
            real = self.decode_PacDec_to_str(rest[0:4], scale)
            pwr_lst.append(real)
            rest = rest[4:]

        mounth_record = [date_txt] + pwr_lst
        
        return mounth_record
            

    def rd_pwi_record(self, idx: int):
        # TODO: move ti list init Fn
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
        date_lst, rest = self.decode_time_to_liststr(in_dat)
 
        date_txt = ':'.join( date_lst )

        P_sum_in = rest[0:3].hex().removesuffix('F')
        P_sum_out = rest[4:7].hex().removesuffix('F')
        # TODO: according to protocol must be presented in this response
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

    def rd_holidays_tbl(self):
        cmd = mconst.GET_ID_CMD
        obj_id = mconst.HOLIDAYS_ID_DATA
        send_dat = [self.adr, cmd, obj_id]
        in_dat = self.run_request(send_dat)

        holidays = []
        rec_len = 2
        for idx in range(20):
            day = int.from_bytes(in_dat[rec_len*idx:rec_len*idx+1], byteorder='little', signed=False)
            month = int.from_bytes(in_dat[rec_len*idx+1:rec_len*idx+2], byteorder='little', signed=False)

            if day != 0xFF and month != 0xFF:
                holidays.append([str(day), str(month)])
            else:
                break
        
        if not holidays:
            holidays.append(["", ""])

        return holidays


    def rd_tax_tbl(self, month_num: int):

        if month_num not in range(12):
            raise IndexError("Wrong month number")
        
        req_id = mconst.TAX_RATE_JAN_ID_DATA + month_num

        in_dat_full = self.run_request([self.adr, mconst.GET_ID_CMD, req_id])
 
        taxt_tbl = []
        line_size = 4
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

            # this is an example of empty output - just for reference
            # taxt_tbl = [[] for x in range(5)]

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


    def decode_time_to_liststr(self, in_dat: bytes):
        minutes = str(in_dat[0]).zfill(2)
        hours = str(in_dat[1]).zfill(2)
        days = str(in_dat[2]).zfill(2)
        months_lst = ['ERR', 'JAN' , 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
        months_idx = in_dat[3]
        months = str(months_lst[months_idx]) if months_idx < len(months_lst) else 'Err'                
        years = str(2000 + in_dat[4])
 
        # this is an example of empty output - just for reference
        #date_txt = ':'.join( [minutes, hours, days, months, years] )
        return [minutes, hours, days, months, years], in_dat[5:]

    def decode_timesec_to_liststr(self, in_dat: bytes):
        seconds = str(in_dat[0]).zfill(2)
        minutes = str(in_dat[1]).zfill(2)
        hours = str(in_dat[2]).zfill(2)
        days = str(in_dat[3]).zfill(2)
        months_lst = ['ERR', 'JAN' , 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
        months_idx = in_dat[4]
        months = str(months_lst[months_idx]) if months_idx < len(months_lst) else 'Err'                
        years = str(2000 + in_dat[5])
        return [seconds, minutes, hours, days, months, years], in_dat[6:]


    def decode_PacDec_to_str(self, in_dat: bytes, scale = 1):
        in_digit = in_dat.hex().removesuffix('F')
        if set(in_digit) =={'0'}:
            return '0'
        in_digit = in_digit[::-1]
        if scale !=1:
            in_real = in_digit[0:len(in_digit)-scale:] + '.' + in_digit[len(in_digit)-scale:]
        else:
            in_real = in_digit
        
        txt = str(in_real.lstrip('0'))    
        return txt       

    def decode_word_to_str(self, in_dat: bytes, scale = 1) -> {str, bytes}:
        dat = in_dat[0:4]
        digit = int.from_bytes(in_dat, byteorder='little', signed=False)
        txt = str(digit)    
        return txt, in_dat[4:]

    def decode_str_to_str(self, in_dat: bytes) -> str:
        i = in_dat.find(b'\x00')
        if i == -1:
            re_in_dat = in_dat
        else:
            re_in_dat = in_dat[:i]
        in_str = re_in_dat.decode("utf-8")
        txt = in_str.rstrip('\0')
        return txt

    def rd_str(self, item: ReqId):
        

        if item not in self.trans_str_tbl.keys():
            # TODO:
            raise ValueError('Request from GUI is not supported!')

        this_msg = self.trans_str_tbl[item]

        in_dat = self.run_request([self.adr, mconst.GET_ID_CMD, this_msg.id])

        txt = "NA"

        if this_msg.dtype == DType.StrData:
            txt = self.decode_str_to_str(in_dat)
        elif this_msg.dtype == DType.DigitData:
            in_digit = int.from_bytes(in_dat, byteorder='little', signed=True)
            in_real = in_digit / this_msg.scale if this_msg.scale != 1 else in_digit
            txt = str(in_real)
        elif this_msg.dtype == DType.UDigitData:
            in_digit = int.from_bytes(in_dat, byteorder='little', signed=False)
            in_real = in_digit / this_msg.scale if this_msg.scale != 1 else in_digit
            txt = str(in_real)            
        elif this_msg.dtype == DType.PacDecData:
            txt = self.decode_PacDec_to_str(in_dat, this_msg.scale)  
        elif this_msg.dtype == DType.RtcData:
            time_list, _ = self.decode_rtc_to_liststr(in_dat)
            txt = ':'.join(time_list)
        elif this_msg.dtype == DType.VScaleData:
            in_digit = in_dat[0:1]
            digit = int.from_bytes(in_digit, byteorder='little', signed=False)
            txt = str(digit)
        elif this_msg.dtype == DType.IScaleData:
            in_digit = in_dat[2:3]
            digit = int.from_bytes(in_digit, byteorder='little', signed=False)
            txt = str(digit)              
        else:
            txt = "Data type is not supported"

        return txt
        

    Msg = namedtuple("Msg", "dtype id len scale", defaults=(None, None, None, 1))

    trans_str_tbl = { 
          ReqId.model: Msg(DType.StrData, mconst.MODEL_ID_DATA, 14)  
        , ReqId.fw_ver: Msg(DType.StrData, mconst.FW_ID_DATA, 4)
        , ReqId.serial_num: Msg(DType.StrData, mconst.SN_ID_DATA, 15)
        , ReqId.prod_date: Msg(DType.RtcData, mconst.PROD_DATE_ID_DATA, 7)
        , ReqId.cur_rate: Msg(DType.DigitData, mconst.RATE_ID_DATA, 1)
        , ReqId.freq: Msg(DType.UDigitData, mconst.FREQ_ID_DATA, 2, 1000)
        , ReqId.v_scale: Msg(DType.VScaleData, mconst.SCALE_ID_DATA, 4)
        , ReqId.i_scale: Msg(DType.IScaleDate, mconst.SCALE_ID_DATA, 4)                        
        
        , ReqId.rtc: Msg(DType.RtcData, mconst.RTC_ID_DATA, 7)
        , ReqId.calc_day: Msg(DType.DigitData, mconst.CALC_DAY_ID_DATA, 1)

        , ReqId.UPhA: Msg(DType.DigitData, mconst.UA_ID_DATA, 3, 1000)
        , ReqId.IPhA: Msg(DType.DigitData, mconst.IA_ID_DATA, 3, 1000)
        , ReqId.PwrA: Msg(DType.DigitData, mconst.PA_ID_DATA, 4, 1000)  


        , ReqId.UPhB: Msg(DType.DigitData, mconst.UB_ID_DATA, 3, 1000)
        , ReqId.IPhB: Msg(DType.DigitData, mconst.IB_ID_DATA, 3, 1000)
        , ReqId.PwrB: Msg(DType.DigitData, mconst.PB_ID_DATA, 4, 1000)  

        , ReqId.UPhC: Msg(DType.DigitData, mconst.UC_ID_DATA, 3, 1000)
        , ReqId.IPhC: Msg(DType.DigitData, mconst.IC_ID_DATA, 3, 1000)
        , ReqId.PwrC: Msg(DType.DigitData, mconst.PC_ID_DATA, 4, 1000)                        

        , ReqId.ActPwrA: Msg(DType.DigitData, mconst.APA_ID_DATA, 4, 1000)     
        , ReqId.ActPwrB: Msg(DType.DigitData, mconst.APB_ID_DATA, 4, 1000)  
        , ReqId.ActPwrC: Msg(DType.DigitData, mconst.APC_ID_DATA, 4, 1000)             

        , ReqId.ActPwr: Msg(DType.DigitData, mconst.AP_ID_DATA, 4, 1000)      
        
        , ReqId.ReActPwr: Msg(DType.DigitData, mconst.RP_ID_DATA, 4, 1000)   

        , ReqId.Active_imp_e: Msg(DType.PacDecData, mconst.AIE_ID_DATA, 4, 2)                      
    }


