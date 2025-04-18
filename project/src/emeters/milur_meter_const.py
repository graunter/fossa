from enum import auto, Enum

class AccessLvl:
    pass

# TODO: data model according to power meter user manual
# class Data:
#     def __init__(self):
#         value_type = 0
#         value = bytearray()
#         value_len = 0

#     def get(self, ObjUID: int):
#         version = 0
#         if ObjUID == 0:
#             if (self.value_len != 4) or (self.value_type==0) or (len(self.value) != 4):
#                 #TODO: 
#                 pass
#             else:
#                 version = int.from_bytes(self.value, byteorder='big', signed=False)
#         else:
#             #TODO
#             pass
#         return version

#     def set(self, ObjUID, val: bytearray):
#         pass

#  Str Data
class ReqId(Enum):
    model = auto()
    fw_ver = auto()
    serial_num = auto()
    prod_date = auto()
    rtc = auto()
    cur_rate = auto()
    i_scale = auto()
    v_scale = auto()


# PacDecData
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

#Word Data
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

#Caten Data
    UPhA = auto()
    UPhB = auto()
    UPhC = auto()
    IPhA = auto()
    IPhB = auto()
    IPhC = auto()

    AIE= auto()       

# parcer types
class DType(Enum):
    StrData = auto() 
    PacDecData = auto() 
    DigitData = auto() 
    RtcData = auto()
    VScaleData = auto()
    IScaleDate = auto()
