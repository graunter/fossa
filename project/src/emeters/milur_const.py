

class Inc:
    _idx_counter = 0

    def __new__(cls):
        cur_val = Inc._idx_counter
        Inc._idx_counter += 1
        return cur_val
    
    def set_to(val: int):
        Inc._idx_counter = val


TEST_ADR = 0x15


GET_ID_CMD	=	1
SET_ID_CMD	=	2
nop_ID_CMD	=	3
nop_ID_CMD	=	4
LISTINIT_ID_CMD	=	5
GETLISTNE_ID_CMD	=	6
nop_ID_CMD	=	7
AOPEN_ID_CMD	=	8
ARELEASE_ID_CMD	=	9
SETRTC_ID_CMD	=	10
GET_EVTLIST_ID_CMD	=	11
GET_ENTALIST_ID_CMD	=	12
getPWIRecord_ID_CMD	=	13
PWILIST_SEARCH_ID_CMD	=	14
GETCURINDEX_ID_CMD	=	15
LIST_SEARCH_ID_CMD	=	16
GET_COLLECTION_ID_CMD	=	17
nop_ID_CMD	=	18
nop_ID_CMD	=	19
SET_IDM_SERVICE_ID_CMD	=	20
UPDATE_FIRMWARE_ID_CMD	=	21
SET_RTC_G3PLC_ID_CMD	=	22
GET_METERINFO_G3PLC_ID_CMD	=	23
nop_ID_CMD	=	24
nop_ID_CMD	=	25
nop_ID_CMD	=	26
nop_ID_CMD	=	27
nop_ID_CMD	=	28
nop_ID_CMD	=	29
SET_SOFT_RTC_CORRECTION_ID_CMD	=	30
SET_ROUND_RTC_TO_MINUTE_ID_CMD	=	31
SET_ROUND_RTC_TO_QUARTERHOUR_ID_CMD	=	32

Inc.set_to(9)

FREQ_ID_DATA = Inc()                   # Частота сети
RATE_ID_DATA = Inc()             # Текущий тариф
INDICATION_ID_DATA = Inc()       # Параметры индикации
_ = Inc()
CTRL_FN_ID_DATA = Inc()        # Идентификатор управляющей процедуры
RTC_ID_DATA = Inc()            # Часы реального времени
HOLIDAYS_ID_DATA = Inc()       # Список праздничных дней
PWI_ID_DATA = Inc()            # Срезы мощности
EVENTS_ID_DATA = Inc()         # Буфер событий
ERR_LST_ID_DATA = Inc()        # Список событий (errors)
MAX_RATES_ID_DATA = Inc()      # Максимальное число тарифов
                            # none
MODEL_ID_DATA = 32          # Модель счетчика
FW_ID_DATA = 33             # Версия встроенного программного обеспечения
RTC_CALIBR_ID_DATA = 34     # Калибровка часов реального времени
TIME_AUTO_SW_ID_DATA = 35   # Управление автоматическим переходом на летнее/зимнее время

                            # scipped
DAYS_PWR_ID_DATA = 66       # Энергия в суточных интервалах                            
MONTHS_PWR_ID_DATA = 67     # Энергия в месячных интервалах
SN_ID_DATA = 68             # Серийный номер счетчика

Inc.set_to(100)

UA_ID_DATA = Inc()            # Напряжение. Фаза А
UB_ID_DATA = Inc()            # Напряжение. Фаза В
UC_ID_DATA = Inc()
IA_ID_DATA = Inc()            # Ток. Фаза А
IB_ID_DATA = Inc()
IC_ID_DATA = Inc()
APA_ID_DATA = Inc()           # Активная мощность. Фаза А
APB_ID_DATA = Inc()
APC_ID_DATA = Inc()
AP_ALL_ID_DATA = Inc()            # Активная мощность. Сумма
RPA_ID_DATA = Inc()           # Реактивная мощность. Фаза А
RPB_ID_DATA = Inc()
RPC_ID_DATA = Inc()
RP_ALL_ID_DATA = Inc()            # Реактивная мощность. Сумма
PA_ID_DATA = Inc()            # Полная мощность. Фаза А
PB_ID_DATA = Inc()
PC_ID_DATA = Inc()
P_ID_DATA = Inc()             # Полная мощность. Сумма

AP_ID_DATA = Inc()           # Активная импортируемая энергия суммарная
AP_T1_ID_DATA = Inc()        # Активная импортируемая энергия по тарифу 1
AP_T2_ID_DATA = Inc()        # Активная импортируемая энергия по тарифу 2
AP_T3_ID_DATA = Inc()        # Активная импортируемая энергия по тарифу 3
AP_T4_ID_DATA = Inc()        # Активная импортируемая энергия по тарифу 4
AP_T5_ID_DATA = Inc()        # Активная импортируемая энергия по тарифу 5
AP_T6_ID_DATA = Inc()        # Активная импортируемая энергия по тарифу 6
AP_T7_ID_DATA = Inc()        # Активная импортируемая энергия по тарифу 7
AP_T8_ID_DATA = Inc()        # Активная импортируемая энергия по тарифу 8

RP_ID_DATA = Inc()           # Реактивная импортируемая энергия суммарная
RP_T1_ID_DATA = Inc()        # Реактивная импортируемая энергия по тарифу 1
RP_T2_ID_DATA = Inc()        # Реактивная импортируемая энергия по тарифу 2
RP_T3_ID_DATA = Inc()        # Реактивная импортируемая энергия по тарифу 3
RP_T4_ID_DATA = Inc()        # Реактивная импортируемая энергия по тарифу 4
RP_T5_ID_DATA = Inc()        # Реактивная импортируемая энергия по тарифу 5
RP_T6_ID_DATA = Inc()        # Реактивная импортируемая энергия по тарифу 6
RP_T7_ID_DATA = Inc()        # Реактивная импортируемая энергия по тарифу 7
RP_T8_ID_DATA = Inc()        # Реактивная импортируемая энергия по тарифу 8

_ = Inc()                   # Параметры калибровки

TAX_RATE_JAN_ID_DATA = Inc()     # Тарифное расписание на январь
TAX_RATE_FEB_ID_DATA = Inc()     # Тарифное расписание на февраль
TAX_RATE_MAR_ID_DATA = Inc()     # Тарифное расписание на март
TAX_RATE_APR_ID_DATA = Inc()     # Тарифное расписание на апрель
TAX_RATE_MAY_ID_DATA = Inc()     # Тарифное расписание на май
TAX_RATE_JUN_ID_DATA = Inc()     # Тарифное расписание на июнь
TAX_RATE_JUL_ID_DATA = Inc()     # Тарифное расписание на июль
TAX_RATE_AUG_ID_DATA = Inc()     # Тарифное расписание на август
TAX_RATE_SEP_ID_DATA = Inc()     # Тарифное расписание на сентябрь
TAX_RATE_OCT_ID_DATA = Inc()     # Тарифное расписание на октябрь
TAX_RATE_NOV_ID_DATA = Inc()     # Тарифное расписание на ноябрь
TAX_RATE_DEC_ID_DATA = Inc()     # Тарифное расписание на декабрь


AN_ID_DATA = Inc()           # Активная экспортируемая энергия суммарная
AN_T1_ID_DATA = Inc()        # Активная экспортируемая энергия по тарифу 1
AN_T2_ID_DATA = Inc()        # Активная экспортируемая энергия по тарифу 2
AN_T3_ID_DATA = Inc()        # Активная экспортируемая энергия по тарифу 3
AN_T4_ID_DATA = Inc()        # Активная экспортируемая энергия по тарифу 4
AN_T5_ID_DATA = Inc()        # Активная экспортируемая энергия по тарифу 5
AN_T6_ID_DATA = Inc()        # Активная экспортируемая энергия по тарифу 6
AN_T7_ID_DATA = Inc()        # Активная экспортируемая энергия по тарифу 7
AN_T8_ID_DATA = Inc()        # Активная экспортируемая энергия по тарифу 8


RN_ID_DATA = Inc()           # Реактивная экспортируемая энергия суммарная
RN_T1_ID_DATA = Inc()        # Реактивная экспортируемая энергия по тарифу 1
RN_T2_ID_DATA = Inc()        # Реактивная экспортируемая энергия по тарифу 2
RN_T3_ID_DATA = Inc()        # Реактивная экспортируемая энергия по тарифу 3
RN_T4_ID_DATA = Inc()        # Реактивная экспортируемая энергия по тарифу 4
RN_T5_ID_DATA = Inc()        # Реактивная экспортируемая энергия по тарифу 5
RN_T6_ID_DATA = Inc()        # Реактивная экспортируемая энергия по тарифу 6
RN_T7_ID_DATA = Inc()        # Реактивная экспортируемая энергия по тарифу 7
RN_T8_ID_DATA = Inc()        # Реактивная экспортируемая энергия по тарифу 8


PF = 173                        # Фактор мощности (cos(φ)

YEARS_REC_ID_DATA = 200            # Список Энергия на начало года

PROD_DATE_ID_DATA = 208     # Дата производства

CALC_DAY_ID_DATA = 212      # Дата расчетного периода
SCALE_ID_DATA = 216         # Коэффициент трансформации по току/напряжению





ACCESS_LVL_USER = 0
ACCESS_ADM_USER = 1
ACCESS_DEV_USER = 2

PWD_LEN = 6
ACCESS_PWD_USER = [255]*PWD_LEN
