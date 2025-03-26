

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

FREQ_ID_DATA = 9            # Частота сети
RATE_ID_DATA = 10           # Текущий тариф
INDICATION_ID_DATA = 11     # Параметры индикации
CTRL_FN_ID_DATA = 13        # Идентификатор управляющей процедуры
RTC_ID_DATA = 14            # Часы реального времени
HOLIDAYS_ID_DATA = 15       # Список праздничных дней
PWI_ID_DATA = 16            # Срезы мощности
EVENTS_ID_DATA = 17         # Буфер событий
ERR_LST_ID_DATA = 18        # Список событий (errors)
MAX_RATES_ID_DATA = 19      # Максимальное число тарифов
                            # none
MODEL_ID_DATA = 32          # Модель счетчика
FW_ID_DATA = 33             # Версия встроенного программного обеспечения
RTC_CALIBR_ID_DATA = 34     # Калибровка часов реального времени
TIME_AUTO_SW_ID_DATA = 35   # Управление автоматическим переходом на летнее/зимнее время

                            # scipped

SN_ID_DATA = 68             # Серийный номер счетчика

UA_ID_DATA = 100            # Напряжение. Фаза А
UB_ID_DATA = 101            # Напряжение. Фаза В
UC_ID_DATA = 102
IA_ID_DATA = 103            # Ток. Фаза А
IB_ID_DATA = 104
IC_ID_DATA = 105
APA_ID_DATA = 106           # Активная мощность. Фаза А
APB_ID_DATA = 107
APC_ID_DATA = 108
AP_ID_DATA = 109            # Активная мощность. Сумма
RPA_ID_DATA = 110           # Реактивная мощность. Фаза А
RPB_ID_DATA = 111
RPC_ID_DATA = 112
RP_ID_DATA = 113            # Реактивная мощность. Сумма
PA_ID_DATA = 114            # Полная мощность. Фаза А
PB_ID_DATA = 115
PC_ID_DATA = 116
P_ID_DATA = 117             # Полная мощность. Сумма

AIE_ID_DATA = 118           # Активная импортируемая энергия суммарная

PROD_DATE_ID_DATA = 208     # Дата производства

SCALE_ID_DATA = 216         # Коэффициент трансформации по току/напряжению





ACCESS_LVL_USER = 0
ACCESS_ADM_USER = 1
ACCESS_DEV_USER = 2

ACCESS_PWD_USER = [255]*6
