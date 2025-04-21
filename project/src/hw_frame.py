import TermTk as ttk        # pip install pyTermTk
from collections import defaultdict
from emeters.milur_const import *
import data_req as req
import emeters.milur_meter as mtr
from emeters.milur_meter_const import ReqId



class HardInfoFrame(ttk.TTkFrame):

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

        def_name_w = 30
        def_data_w = 20
        def_unit_w = 20

        def_name_size = 20
        def_data_size = 20
        def_unit_size = 30

        self.items = [
            
            req.DataRequest(label="Model name", req=lambda dev: dev.rd_str(ReqId.model))
            , req.DataRequest(label="Serial number", req=lambda dev: dev.rd_str(ReqId.serial_num))
            , req.DataRequest(label="Production date", unit="ss.mm.hh.dow.dd.mm.yyyy", req=lambda dev: dev.rd_str(ReqId.prod_date))
            , req.DataRequest(label="FW version", req=lambda dev: dev.rd_str(ReqId.fw_ver))
            , req.DataRequest(label="Current scale", req=lambda dev: dev.rd_str(ReqId.i_scale))
            , req.DataRequest(label="Voltage scale", req=lambda dev: dev.rd_str(ReqId.v_scale))        
        ]

        self.setLayout(ttk.TTkVBoxLayout())
        for item in self.items:
            self.layout().addWidget(item)

        self.layout().addWidget(ttk.TTkSpacer())


    def set_device(self, dev: mtr.PwrMeter):
        self.device = dev

        for i in self.items:
            i.set_device(dev)
            i.upd_from_dev()

    def on_upd(self):
        # self.on_read_hh_cnt_btn()        
        for item in self.items:
            item.upd_from_dev()