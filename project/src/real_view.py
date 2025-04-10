import TermTk as ttk        # pip install pyTermTk
from collections import defaultdict
from milur_const import *
import data_req as req
import milur_meter as mtr
from milur_meter import ReqId



class RealFrame(ttk.TTkFrame):

    def __init__(self, *,
                 name:str=None,
                 **kwargs) -> None:
        
        self.device = None

        super().__init__(name="name", **kwargs)

        # g_view_frame = ttk.TTkFrame(border=True, title="View", visible=False)

        line_cnt = 0
        name_column = 0
        data_column = 1
        units_column = 2

        self.g_view_items = [
            req.DataRequest(label="RTC", req=lambda dev: dev.rd_str(ReqId.rtc))
            , req.DataRequest(label="Rate", req=lambda dev: dev.rd_str(ReqId.cur_rate))
            , req.DataRequest(label="A Phase voltage", unit="V", req=lambda dev: dev.rd_str(ReqId.UPhA))
            , req.DataRequest(label="A Phase current", unit="A", req=lambda dev: dev.rd_str(ReqId.IPhA))
            , req.DataRequest(label="A Phase active power", unit="W", req=lambda dev: dev.rd_str(ReqId.ActPwrA))

            , req.DataRequest(label="B Phase voltage", unit="V", req=lambda dev: dev.rd_str(ReqId.UPhB))
            , req.DataRequest(label="B Phase current", unit="A", req=lambda dev: dev.rd_str(ReqId.IPhB))
            , req.DataRequest(label="B Phase active power", unit="W", req=lambda dev: dev.rd_str(ReqId.ActPwrB))

            , req.DataRequest(label="C Phase voltage", unit="V", req=lambda dev: dev.rd_str(ReqId.UPhC))
            , req.DataRequest(label="C Phase current", unit="A", req=lambda dev: dev.rd_str(ReqId.IPhC))
            , req.DataRequest(label="C Phase active power", unit="W", req=lambda dev: dev.rd_str(ReqId.ActPwrC))

            
            , req.DataRequest(label="Active power summary", unit="W", req=lambda dev: dev.rd_str(ReqId.ActPwr))
            , req.DataRequest(label="Active in energy sum", unit="kW*h", req=lambda dev: dev.rd_str(ReqId.Active_imp_e))  

        ]

        self.setLayout(ttk.TTkVBoxLayout())

        for item in self.g_view_items:
            self.layout().addWidget(item)

        self.layout().addWidget(ttk.TTkSpacer())


    def set_device(self, dev: mtr.PwrMeter):
        self.device = dev

        for item in self.g_view_items:
            item.set_device(dev)
            item.upd_from_dev()

    def on_upd(self):
        # self.on_read_hh_cnt_btn()        
        for item in self.g_view_items:
            item.upd_from_dev()