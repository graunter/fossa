
import time
import serial   #pip install pyserial
import emeters.milur_const as mconst
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
    def __init__(self, msg, tx=[], rx=[]):
        super().__init__(msg)
        self.tx = tx
        self.rx = rx
        
class DummyPortHandler():

    def __init__(self, port: serial.Serial):
        self.port = port

    def __enter__(self):
        return self
    
    def __exit__(self, exception_type, exception_value, exception_traceback):
        #Exception handling here
        pass

    def write(self, data): return self.port.write(data)
    def read(self, data): return self.port.read(data)    
    def reset_input_buffer(self): return self.port.reset_input_buffer() 
    def flush(self): return self.port.flush() 


class MilurMeter:

    def __init__(self, adr: int):
        self.adr = adr
        self.err_cnt = 0


    def link(self, *args):
        self.ph = DummyPortHandler(*args)

    def disconnect(self):
        self.ph = None     


    # TODO: this check is not protected by semaphore
    @staticmethod
    def check_resp_on_adr(adr: int, port: serial.Serial, sem: threading.Semaphore = None) -> bool:
        send_dat = sum([[adr], [mconst.AOPEN_ID_CMD], [mconst.ACCESS_LVL_USER], list(mconst.ACCESS_PWD_USER)], [])
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

                last_send_dat = sum([[adr], [mconst.ARELEASE_ID_CMD], [0]], [])
                last_send_packet = create_packet_from_dat(last_send_dat)
                port.write(last_send_packet)
                last_received = port.read(128)
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

        with self.ph as ph:
            ph.write(send_packet)
            #TODO: read len should be calculated
            # adr id_cmd crc1 crc2
            resp = ph.read(10)
            
            if len(resp) != 4:
            #     raise ProtocolException("Too short response for login")
                pass
            

    def logout(self) -> bool:
        send_dat = [self.adr] + [mconst.ARELEASE_ID_CMD]

        # TODO: There is no clear secription for 'releare' respose
        # may be standard error processing over exeption will be enought
        self.run_request(send_dat, True)



    def raise_with_dbg_data(self, msg, tx=None, rx=None):
        raise ProtocolException(
            f'{msg}'
            , f'TX: [{str(tx)}], '
            , f'RX: [{str(rx)}]' 
        )         

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

    MIN_RESP_LEN = 6   

    POS_ADR = 0     
    POS_CODE = 1
    POS_ERR = 2
    POS_LEN = 3
    POS_DAT = 4

    def run_request(self, pdu: list, no_resp_fl=False) -> bytes:
        send_packet = create_packet_from_dat(pdu)  
        tx_cmd_id = pdu[1]

        with self.ph as ph:
            ph.reset_input_buffer()
            ph.write(send_packet)
            ph.flush()
            #TODO: read len should be calculated
            # adr id_cmd _id_obj len crc1 crc2

            long_time_commands = { 
                mconst.SETRTC_ID_CMD:0.1 
                , mconst.GET_ENTALIST_ID_CMD:0.05
                , mconst.GET_COLLECTION_ID_CMD:0.1
            }

            # if (tx_cmd_id := pdu[1]) in long_time_commands.keys():
            #     time.sleep(long_time_commands[tx_cmd_id])

            # TODO: Should we read with no_response flag? 
            # check this part of SM 
            resp = ph.read(self.MIN_RESP_LEN)

            if no_resp_fl and not resp:
                return
            
            if len(resp) < self.MIN_RESP_LEN and tx_cmd_id  in long_time_commands.keys():
                time.sleep(long_time_commands[tx_cmd_id])
                add_resp = ph.read(self.MIN_RESP_LEN)
                resp = resp + add_resp

            if resp == b'':
                self.raise_with_dbg_data('No response from device', send_packet) 

            if len(resp) < self.MIN_RESP_LEN:
                self.raise_with_dbg_data('Too short response', send_packet, resp) 

            if (rx_adp:=resp[self.POS_ADR]) != (tx_adr:=pdu[self.POS_ADR]):
                self.raise_with_dbg_data('Wrong reply address', send_packet, resp) 

            
            in_data = []
            
            resp_with_len = [
                mconst.GET_ID_CMD
                , mconst.LISTINIT_ID_CMD
                , mconst.GETLISTNE_ID_CMD
                , mconst.GETCURINDEX_ID_CMD
                , mconst.getPWIRecord_ID_CMD
                , mconst.GET_ENTALIST_ID_CMD]

            if tx_cmd_id in resp_with_len:
                if (resp_code:=resp[self.POS_CODE]) == (0x80 + tx_cmd_id):
                    if (err_code:=resp[self.POS_ERR]) in self.RespErrCode.keys():
                        txt = self.RespErrCode[err_code]
                    else:
                        txt = ""
                    
                    self.raise_with_dbg_data(f'Response Err {txt}', send_packet, resp)                          
                
                if resp_code != tx_cmd_id:
                    self.raise_with_dbg_data('Wrong reply code', send_packet, resp)   
 
                resp_next = ph.read(next_read_size := resp[self.POS_LEN])   

                if len(resp_next) != next_read_size:
                    self.raise_with_dbg_data('Respons is not complete', send_packet, resp+resp_next)
                
                #TODO: set timeout to 3.5 chars and read no symbols
                # resp_extra = self.port.read(3)
                # if resp_extra:
                #     raise ProtocolException(f'Extra data on line: {str(resp_extra)}')

                resp = resp + resp_next

                crc = calc_crc_16_ibm(resp[0:-2])
                ba = crc.to_bytes(2, byteorder='little')
        
                if (ba[0] != resp[-2]) or (ba[1] != resp[-1]):
                    # TODO: may be not eq?
                    # if resp_code == mconst.GET_COLLECTION_ID_CMD:
                    self.raise_with_dbg_data('Crc mismatch', send_packet, resp+resp)
                else:
                    in_data = resp[self.POS_DAT:len(resp)-2]

            elif tx_cmd_id == mconst.GET_COLLECTION_ID_CMD:
                if (resp_code:=resp[self.POS_CODE]) == (0x80 + tx_cmd_id):
                    if (err_code:=resp[self.POS_ERR]) in self.RespErrCode.keys():
                        txt = self.RespErrCode[err_code]
                    else:
                        txt = "Response Err"
                    
                    self.raise_with_dbg_data(f'Response Err in GET_COLLECTION_ID_CMD #{txt}', send_packet, resp)      
 
                if resp_code != tx_cmd_id:
                    self.raise_with_dbg_data('Wrong reply code', send_packet, resp)  
                
                # WARNING - this diff with common processing is important!
                next_read_size = resp[self.POS_LEN] + 1
                resp_next = ph.read(next_read_size)   

                if next_read_size < len(resp_next):
                    self.raise_with_dbg_data(f'Short response Err in GET_COLLECTION_ID_CMD ', send_packet, resp+resp_next) 

                #TODO: set timeout to 3.5 chars and read no sumbols
                # resp_extra = self.port.read(3)
                # if resp_extra:
                #     raise ProtocolException(f'Extra data on line: {str(resp_extra)}')  
                
                resp = resp + resp_next

                crc = calc_crc_16_ibm(resp[0:-2])
                ba = crc.to_bytes(2, byteorder='little')
        
                if (ba[0] != resp[-2]) or (ba[1] != resp[-1]):
                    #TODO: the overall packet seem good
                    # in_data = resp[data_start_pos:len(resp)-1]
                    pass
                else:
                    in_data = resp[self.POS_DAT:len(resp)-2]

                              
            elif tx_cmd_id == mconst.SETRTC_ID_CMD:
                if (resp_code:=resp[self.POS_CODE]) == (0x80 + tx_cmd_id):
                    if (err_code:=resp[self.POS_ERR]) in self.RespErrCode.keys():
                        txt = self.RespErrCode[err_code]
                    else:
                        txt = ""
                    
                    self.raise_with_dbg_data(f'Response Err in SETRTC_ID_CMD #{txt}', send_packet, resp)  
                
            else:
                # TODO: the command processed by anyway but todo with this response?
                # self.raise_with_dbg_data(f'The response for {tx_cmd_id} command is not supported', send_packet, resp) 
                in_data = []

        return in_data

    def wr_soft_time(self, diff_sec, period):

        cmd = mconst.SET_SOFT_RTC_CORRECTION_ID_CMD
        send_dat = [self.adr, cmd, diff_sec, period]  
        in_dat = self.run_request(send_dat)

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

    def rd_all_electricity(self) -> list:
        cmd = mconst.GET_COLLECTION_ID_CMD
        obj_id = 2
        send_dat = [self.adr, cmd, obj_id, 1, 0]        
        
        in_dat = self.run_request(send_dat)
       
        if len(in_dat)==0:
            pass    # for breakpoint

        try:
            dlen = 4
            records = []
            dat = in_dat
            for cnt in range(12):
                records.append( digit := int.from_bytes(dat[cnt*dlen:(cnt+1)*dlen], byteorder='little', signed=True)/1000 )

            pwr_lst  = [str(item) for item in records]
        except Exception as e:
            raise ProtocolException(
                f'Can"t parse power records'
                , f'TX: [{str(send_dat)}], '
                , f'RX: [{str(dat)}]' 
        )  

        try:
            dat = dat[(cnt+1)*dlen:]
            dlen = 3
            records = []
            for cnt in range(3):
                records.append( digit := int.from_bytes(dat[cnt*dlen:(cnt+1)*dlen], byteorder='little', signed=True)/1000) 

            v_lst = [str(item) for item in records]
        except Exception as e:
            raise ProtocolException(
                f'Can"t parse voltage records'
                , f'TX: [{str(send_dat)}], '
                , f'RX: [{str(dat)}]' 
        )  

        try:
            dat = dat[(cnt+1)*dlen:]
            dlen = 3
            records = []
            for cnt in range(3):
                records.append( digit := int.from_bytes(dat[cnt*dlen:(cnt+1)*dlen], byteorder='little', signed=True)/1000) 

            i_lst = [str(item) for item in records]
        except Exception as e:
            raise ProtocolException(
                f'Can"t parse current records'
                , f'TX: [{str(send_dat)}], '
                , f'RX: [{str(dat)}]' 
        )              



        try:
            last_dat = dat[(cnt+1)*dlen:]
            freq = 0
            tax = 0
            time = 0
            freq = str(int.from_bytes(last_dat[0:2], byteorder='little', signed=False)/1000)
            tax = str(int.from_bytes(last_dat[2:3], byteorder='little', signed=False))
            time, _ = self.decode_rtc_to_liststr(last_dat[3:3+7])
        except Exception as e:
            raise ProtocolException(
                f'Can"t parse misc records: {str(freq)}, {str(tax)}, {str(time)} from {str(last_dat)}'
                , f'TX: [{str(send_dat)}], '
                , f'RX: [{str(last_dat)}]' 
        )    

        return pwr_lst + v_lst + i_lst + [freq, tax] + [':'.join( time )]


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
        for cnt in range(8): #12 records total
            value, _ = self.decode_word_to_str(dat[cnt*dlen:(cnt+1)*dlen], 1000)
            records.append( value )

        for cnt in range(8, 12): 
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
            

    def clr_pwi_record(self):
        cmd = mconst.LISTINIT_ID_CMD
        obj_id = mconst.PWI_ID_DATA
        send_dat = [self.adr, cmd, obj_id]
        in_dat = self.run_request(send_dat, True)
        time.sleep(2)   

    def rd_pwi_record(self, idx: int):
        # TODO: move to list init Fn
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
        # date_lst, rest = self.decode_time_to_liststr(in_dat)
 
        dt, rest = self.decode_time_to_datetime(in_dat)
        # date_txt = ':'.join( date_lst )

        P_sum_in = self.decode_PacDec_to_str(rest[0:3], 2)
        P_sum_out = self.decode_PacDec_to_str(rest[4:7], 2)
        # TODO: according to protocol must be presented in this response
        # Q_sum_in = rest[8:11].hex().removesuffix('F')
        # Q_sum_out = rest[12:15].hex().removesuffix('F')

        # end_fl = rest[16]
        end_fl = rest[8]

        # hour_record = [date_txt, str(P_sum_in), str(P_sum_out), str(Q_sum_in), str(Q_sum_out), str(end_fl)]
        hour_record = [dt, P_sum_in, P_sum_out, str(end_fl)]
        
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
    
    def rd_pf(self):
        req_id = mconst.PF

        in_dat_full = self.run_request([self.adr, mconst.GET_ID_CMD, req_id])

        if len(in_dat_full) < 16:
            self.raise_with_dbg_data('PF - too short response', "", in_dat_full) 

        pf_tbl = []
        line_size = 4
        for idx_cnt in range(4):        
            in_dat = in_dat_full[line_size*idx_cnt : line_size*(idx_cnt+1)]

            pf_tbl.append(str(in_dat))

        return pf_tbl


    def decode_rtc_to_datetime(self, in_dat: bytes) -> datetime:
        seconds = in_dat[0]
        minutes = in_dat[1]
        hours = in_dat[2]
        dow = ['ERR', 'Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        doweek_idx = in_dat[3]
        if 0 < doweek_idx < len(dow):
            doweek = doweek_idx-1
        else:
            raise IndexError("emetrs: day-of-week value out of range") 
        
        days = in_dat[4]
        months_lst = ['ERR', 'Jan' , 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        months_idx = in_dat[5]

        if 0 < months_idx < len(months_lst):
            months = months_idx
        else:
            raise IndexError("emetrs: months value out of range")       
              
        years = 2000 + in_dat[6]

        dt = datetime(second=seconds, minute=minutes, hour=hours, day=days, month=months, year=years)

        return dt, in_dat[7:]
        
    def rd_rtc(self) -> datetime:
        in_dat = self.run_request([self.adr, mconst.GET_ID_CMD, mconst.RTC_ID_DATA])
        dt = self.decode_rtc_to_datetime(in_dat)
        return dt



    def decode_month_name_to_digit(self, month: str):
        months_lst = ['JAN' , 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
        try:
            idx = 1 + months_lst.index(month)
            return idx
        except Exception as e: 
            raise ProtocolException(f'Wrong month name: {str(e)}')

    
    def decode_rtc_to_liststr(self, in_dat: bytes):
        seconds = str(in_dat[0]).zfill(2)
        minutes = str(in_dat[1]).zfill(2)
        hours = str(in_dat[2]).zfill(2)
        dow = ['ERR', 'Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        doweek_idx = in_dat[3]
        doweek = str(dow[doweek_idx]) if doweek_idx < len(dow) else 'Err'
        days = str(in_dat[4]).zfill(2)
        months_lst = ['ERR', 'Jan' , 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        months_idx = in_dat[5]
        months = str(months_idx).zfill(2) if months_idx < len(months_lst) else 'Err'                
        years = str(2000 + in_dat[6])
        return [seconds, minutes, hours, doweek, days, months, years], in_dat[7:]


    def decode_time_to_liststr(self, in_dat: bytes):
        minutes = str(in_dat[0]).zfill(2)
        hours = str(in_dat[1]).zfill(2)
        days = str(in_dat[2]).zfill(2)
        months_lst = ['ERR', 'JAN' , 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
        months_idx = in_dat[3]
        months = str(months_idx).zfill(2) if months_idx < len(months_lst) else 'Err'                
        years = str(2000 + in_dat[4])
 
        # this is an example of empty output - just for reference
        #date_txt = ':'.join( [minutes, hours, days, months, years] )
        return [minutes, hours, days, months, years], in_dat[5:]


    def decode_time_to_datetime(self, in_dat: bytes) -> datetime:
        minutes = in_dat[0]
        hours = in_dat[1]
        days = in_dat[2]
        months = in_dat[3]     
        years = 2000 + in_dat[4]

        dt = datetime(minute=minutes, hour=hours, day=days, month=months, year=years)

        return dt, in_dat[5:]
    

    def decode_timesec_to_liststr(self, in_dat: bytes):
        seconds = str(in_dat[0]).zfill(2)
        minutes = str(in_dat[1]).zfill(2)
        hours = str(in_dat[2]).zfill(2)
        days = str(in_dat[3]).zfill(2)
        months_lst = ['ERR', 'JAN' , 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
        months_idx = in_dat[4]
        months = str(months_idx).zfill(2) if months_idx < len(months_lst) else 'Err'                
        years = str(2000 + in_dat[5])
        return [seconds, minutes, hours, days, months, years], in_dat[6:]


    def decode_PacDec_to_str(self, in_dat: bytes, scale = 0):
        in_digit = in_dat.hex().removesuffix('F')
        if set(in_digit) =={'0'}:
            return '0'
        in_digit = in_digit[::-1]
        if scale !=0:
            in_real = in_digit[0:len(in_digit)-scale:] + '.' + in_digit[len(in_digit)-scale:]
        else:
            in_real = in_digit
        
        txt = str(in_real.lstrip('0'))    
        return txt       

    def decode_word_to_str(self, in_dat: bytes, scale = 1) -> {str, bytes}:
        dat = in_dat[0:4]
        digit = int.from_bytes(in_dat, byteorder='little', signed=True)
        txt = str(digit/scale)    
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
        

    Msg = namedtuple("Msg", "name label unite dtype id len scale", defaults=('-', '', '', None, None, None, 1))

    trans_str_tbl = { 
          ReqId.model: Msg("Model name", 'model', '',               DType.StrData, mconst.MODEL_ID_DATA, 14)  
        , ReqId.fw_ver: Msg("Firmware version", 'fw-version', '',   DType.StrData, mconst.FW_ID_DATA, 4)
        , ReqId.serial_num: Msg("Serial number", 'sn',              DType.StrData, mconst.SN_ID_DATA, 15)
        , ReqId.prod_date: Msg("Production date", 'manufactured', "ss.mm.hh.dow.dd.mm.yyyy", DType.RtcData, mconst.PROD_DATE_ID_DATA, 7)
        , ReqId.cur_rate: Msg("Rate", 'tarrif', '',                 DType.DigitData, mconst.RATE_ID_DATA, 1)
        , ReqId.freq: Msg("Frequency", "Frequency", "Hz",           DType.UDigitData, mconst.FREQ_ID_DATA, 2, 1000)
        , ReqId.v_scale: Msg("Voltage scale", "k_voltage",          DType.VScaleData, mconst.SCALE_ID_DATA, 4)
        , ReqId.i_scale: Msg("Current scale", "k-current", '',      DType.IScaleDate, mconst.SCALE_ID_DATA, 4)                        
        
        , ReqId.rtc: Msg("RTC", "time", "ss.mm.hh.dow.dd.mm.yyyy",  DType.RtcData, mconst.RTC_ID_DATA, 7)
        , ReqId.calc_day: Msg("Calc day", "calc-day", "DoM",        DType.DigitData, mconst.CALC_DAY_ID_DATA, 1)

        , ReqId.UPhA: Msg("A Phase voltage", "Urms L1", "V",        DType.DigitData, mconst.UA_ID_DATA, 3, 1000)
        , ReqId.IPhA: Msg("A Phase current", "Irms L1", "A",        DType.DigitData, mconst.IA_ID_DATA, 3, 1000)
 
        , ReqId.UPhB: Msg("B Phase voltage", "Urms L1", "V",        DType.DigitData, mconst.UB_ID_DATA, 3, 1000)
        , ReqId.IPhB: Msg("B Phase current", "Irms L2", "A",        DType.DigitData, mconst.IB_ID_DATA, 3, 1000)
 
        , ReqId.UPhC: Msg("A Phase voltage", "Urms L3", "V",        DType.DigitData, mconst.UC_ID_DATA, 3, 1000)
        , ReqId.IPhC: Msg("A Phase current", "Irms L3", "A",        DType.DigitData, mconst.IC_ID_DATA, 3, 1000)

        , ReqId.PwrA: Msg("A Total power", "S L1", "VA",            DType.DigitData, mconst.PA_ID_DATA, 4, 1000) 
        , ReqId.PwrB: Msg("B Total power", "S L2", "VA",            DType.DigitData, mconst.PB_ID_DATA, 4, 1000) 
        , ReqId.PwrC: Msg("C Total power", "S L3", "VA",            DType.DigitData, mconst.PC_ID_DATA, 4, 1000)     
        , ReqId.Pwr: Msg("Total power", "Total S", "VA",            DType.DigitData, mconst.P_ID_DATA, 4, 1000)                            

        , ReqId.ActPwrA: Msg("Active power", "P L1", "W",           DType.DigitData, mconst.APA_ID_DATA, 4, 1000)     
        , ReqId.ActPwrB: Msg("B Active power", "P L2", "W",         DType.DigitData, mconst.APB_ID_DATA, 4, 1000)  
        , ReqId.ActPwrC: Msg("C Active power", "P L3", "W",         DType.DigitData, mconst.APC_ID_DATA, 4, 1000)             
        , ReqId.ActPwr: Msg("Total Active power", "Total P", "W",   DType.DigitData, mconst.AP_ID_DATA, 4, 1000)   

        , ReqId.ReActPwrA: Msg("A ReActive power", "Q L1", "var",     DType.DigitData, mconst.RPA_ID_DATA, 4, 1000)     
        , ReqId.ReActPwrB: Msg("B ReActive power", "Q L2", "var",     DType.DigitData, mconst.RPB_ID_DATA, 4, 1000)  
        , ReqId.ReActPwrC: Msg("C ReActive power", "Q L3", "var",     DType.DigitData, mconst.RPC_ID_DATA, 4, 1000)             
        , ReqId.ReActPwr: Msg("Total ReActive power", "Total Q", "var", DType.DigitData, mconst.RP_ID_DATA, 4, 1000)   

        , ReqId.Active_imp_e: Msg("Active in energy sum", "AP", "W*h", DType.PacDecData, mconst.AIE_ID_DATA, 4, 0)  
        , ReqId.Active_imp_e_1: Msg("Active in energy sum", "AP-t1", "W*h", DType.PacDecData, mconst.AIE_T1_ID_DATA, 4, 0)  
        , ReqId.Active_imp_e_2: Msg("Active in energy sum", "AP-t2", "W*h", DType.PacDecData, mconst.AIE_T2_ID_DATA, 4, 0)  
        , ReqId.Active_imp_e_3: Msg("Active in energy sum", "AP-t3", "W*h", DType.PacDecData, mconst.AIE_T3_ID_DATA, 4, 0)  
        , ReqId.Active_imp_e_4: Msg("Active in energy sum", "AP-t4", "W*h", DType.PacDecData, mconst.AIE_T4_ID_DATA, 4, 0)  
        , ReqId.Active_imp_e_5: Msg("Active in energy sum", "AP-t5", "W*h", DType.PacDecData, mconst.AIE_T5_ID_DATA, 4, 0)  
        , ReqId.Active_imp_e_6: Msg("Active in energy sum", "AP-t6", "W*h", DType.PacDecData, mconst.AIE_T6_ID_DATA, 4, 0)  
        , ReqId.Active_imp_e_7: Msg("Active in energy sum", "AP-t7", "W*h", DType.PacDecData, mconst.AIE_T7_ID_DATA, 4, 0)  
        , ReqId.Active_imp_e_8: Msg("Active in energy sum", "AP-t8", "W*h", DType.PacDecData, mconst.AIE_T8_ID_DATA, 4, 0)        

        , ReqId.ReAct_imp_e: Msg("ReActive in energy sum", "RP", "W*h", DType.PacDecData, mconst.RIE_ID_DATA, 4, 0)                    
        , ReqId.ReAct_imp_e_1: Msg("ReActive in energy sum", "RP-t1", "W*h", DType.PacDecData, mconst.RIE_T1_ID_DATA, 4, 0)          
        , ReqId.ReAct_imp_e_2: Msg("ReActive in energy sum", "RP-t2", "W*h", DType.PacDecData, mconst.RIE_T2_ID_DATA, 4, 0)  
        , ReqId.ReAct_imp_e_3: Msg("ReActive in energy sum", "RP-t3", "W*h", DType.PacDecData, mconst.RIE_T3_ID_DATA, 4, 0)  
        , ReqId.ReAct_imp_e_4: Msg("ReActive in energy sum", "RP-t4", "W*h", DType.PacDecData, mconst.RIE_T4_ID_DATA, 4, 0)   
        , ReqId.ReAct_imp_e_5: Msg("ReActive in energy sum", "RP-t5", "W*h", DType.PacDecData, mconst.RIE_T5_ID_DATA, 4, 0)          
        , ReqId.ReAct_imp_e_6: Msg("ReActive in energy sum", "RP-t6", "W*h", DType.PacDecData, mconst.RIE_T6_ID_DATA, 4, 0)  
        , ReqId.ReAct_imp_e_7: Msg("ReActive in energy sum", "RP-t7", "W*h", DType.PacDecData, mconst.RIE_T7_ID_DATA, 4, 0)  
        , ReqId.ReAct_imp_e_8: Msg("ReActive in energy sum", "RP-t8", "W*h", DType.PacDecData, mconst.RIE_T8_ID_DATA, 4, 0)                                 
    }


