import TermTk as ttk        # pip install pyTermTk
from collections import defaultdict
# from emeters.milur_const import *
import data_req as req
import emeters.milur_meter as mtr
from emeters.milur_meter_const import ReqId

class RealFrame(ttk.TTkFrame):

    def __init__(self, *,
                 name:str=None,
                 **kwargs) -> None:
        
        self.device = None

        super().__init__(name="name", **kwargs)

        # g_view_frame = ttk.TTkFrame(border=True, title="View", visible=False)


        #---> Common
        line_cnt = 0
        name_column = 0
        data_column = 1
        units_column = 2

        self.g_view_items = [
            req.DataSRequest(label="RTC", req=lambda dev: dev.rd_str(ReqId.rtc))
            , req.DataSRequest(label="Rate", req=lambda dev: dev.rd_str(ReqId.cur_rate))
            , req.DataSRequest(label="Frequency", req=lambda dev: dev.rd_str(ReqId.freq))
            , req.DataSRequest(label="A Phase voltage", unit="V", req=lambda dev: dev.rd_str(ReqId.UPhA))
            , req.DataSRequest(label="A Phase current", unit="A", req=lambda dev: dev.rd_str(ReqId.IPhA))
            , req.DataSRequest(label="A Phase active power", unit="W", req=lambda dev: dev.rd_str(ReqId.ActPwrA))

            , req.DataSRequest(label="B Phase voltage", unit="V", req=lambda dev: dev.rd_str(ReqId.UPhB))
            , req.DataSRequest(label="B Phase current", unit="A", req=lambda dev: dev.rd_str(ReqId.IPhB))
            , req.DataSRequest(label="B Phase active power", unit="W", req=lambda dev: dev.rd_str(ReqId.ActPwrB))

            , req.DataSRequest(label="C Phase voltage", unit="V", req=lambda dev: dev.rd_str(ReqId.UPhC))
            , req.DataSRequest(label="C Phase current", unit="A", req=lambda dev: dev.rd_str(ReqId.IPhC))
            , req.DataSRequest(label="C Phase active power", unit="W", req=lambda dev: dev.rd_str(ReqId.ActPwrC))

            , req.DataSRequest(label="Calc day", unit="date", req=lambda dev: dev.rd_str(ReqId.calc_day))            

            , req.DataSRequest(label="Active power summary (Total P)", unit="W", req=lambda dev: dev.rd_str(ReqId.ActPwr))
            , req.DataSRequest(label="Active power (P L1)", unit="W", req=lambda dev: dev.rd_str(ReqId.ActPwrA))
            # , req.DataSRequest(label="Active power (P L2)", unit="W", req=lambda dev: dev.rd_str(ReqId.ActPwrB))
            # , req.DataSRequest(label="Active power (P L3)", unit="W", req=lambda dev: dev.rd_str(ReqId.ActPwrC))            

            , req.DataSRequest(label="ReActive power summary (Q)", unit="var", req=lambda dev: dev.rd_str(ReqId.ReActPwr))  
            , req.DataSRequest(label="ReActive power (Q L1)", unit="var", req=lambda dev: dev.rd_str(ReqId.ReActPwrA))
            # , req.DataSRequest(label="ReActive power (Q L2)", unit="var", req=lambda dev: dev.rd_str(ReqId.ReActPwrB))
            # , req.DataSRequest(label="ReActive power (Q L3)", unit="var", req=lambda dev: dev.rd_str(ReqId.ReActPwrC)) 

            , req.DataSRequest(label="Full power summary (S)", unit="VA", req=lambda dev: dev.rd_str(ReqId.Pwr))  
            , req.DataSRequest(label="Full power (S L1)", unit="VA", req=lambda dev: dev.rd_str(ReqId.PwrA))
            # , req.DataSRequest(label="Full power (S L2)", unit="VA", req=lambda dev: dev.rd_str(ReqId.PwrB))
            # , req.DataSRequest(label="Full power (S L3)", unit="VA", req=lambda dev: dev.rd_str(ReqId.PwrC)) 



            , req.DataSRequest(label="Active in energy sum (AP)", unit="kW*h", req=lambda dev: dev.rd_str(ReqId.Active_imp_e))  
            , req.DataSRequest(label="Active in energy (AP t1)", unit="kW*h", req=lambda dev: dev.rd_str(ReqId.Active_imp_e_1))  
            # , req.DataSRequest(label="Active in energy (AP t1)", unit="kW*h", req=lambda dev: dev.rd_str(ReqId.Active_imp_e_2))  
            # , req.DataSRequest(label="Active in energy (AP t3)", unit="kW*h", req=lambda dev: dev.rd_str(ReqId.Active_imp_e_3))  
            # , req.DataSRequest(label="Active in energy (AP t4)", unit="kW*h", req=lambda dev: dev.rd_str(ReqId.Active_imp_e_4))                                      

            , req.DataSRequest(label="ReActive in energy sum (AR)", unit="kW*h", req=lambda dev: dev.rd_str(ReqId.ReAct_imp_e))  
            , req.DataSRequest(label="ReActive in energy (AR t1)", unit="kW*h", req=lambda dev: dev.rd_str(ReqId.ReAct_imp_e_1))  
            # , req.DataSRequest(label="ReActive in energy (AR t1)", unit="kW*h", req=lambda dev: dev.rd_str(ReqId.ReAct_imp_e_2))  
            # , req.DataSRequest(label="ReActive in energy (AR t3)", unit="kW*h", req=lambda dev: dev.rd_str(ReqId.ReAct_imp_e_3))  
            # , req.DataSRequest(label="ReActive in energy (AR t4)", unit="kW*h", req=lambda dev: dev.rd_str(ReqId.ReAct_imp_e_4))  

            , req.DataQRequest(
                score="Power Factor", 
                label=["PF", 'PF L1', 'PF L2', 'PF L3'], 
                unit=["none"], 
                req=lambda dev: dev.rd_pf()
            )

        ]

        self.line_frame = ttk.TTkFrame(border=True, visible=False)
        self.line_frame.setLayout(ttk.TTkVBoxLayout())

        for item in self.g_view_items:
            self.line_frame.layout().addWidget(item)

        self.line_frame.layout().addWidget(ttk.TTkSpacer())
        #---< Common

        #---> Groups

            #---> Power
            #---< Power

            #---> Momentum

        self.momentum_head = [
            'PA', 'PB', 'PC', 'PSum', 
            'QA', 'QB', 'QC', 'QSum', 
            'TA', 'TB', 'TC', 'TSum', 
            'VA', 'VB', 'VC', 
            'IA', 'IB', 'IC', 
            'F', 
            'Tax', 
            'RTC'
        ]
        self.no_tax_tbl = [ ['--------' for _ in range( len(self.momentum_head) ) ] ]
        momentum_tableModel = ttk.TTkTableModelList(data=self.no_tax_tbl, header=self.momentum_head)        
        self.moment_table = ttk.TTkTable(tableModel=momentum_tableModel)
        self.moment_table.resizeRowsToContents()
        self.moment_table.resizeColumnsToContents()
        
        self.momentum_frame = ttk.TTkFrame(border=True, visible=False)
        self.momentum_frame.setLayout(ttk.TTkVBoxLayout()) 
        self.momentum_frame.layout().addWidget(self.moment_table)
            #---< Momentum            

            #---> Split
        self.split_head = [
            'PASum', 'PA1' , 'PA2' , 'PA3' , 'PA4' , 'PA5' , 'PA6' , 'PA7' , 'PA8',
            'PRSum', 'PR1' , 'PR2' , 'PR3' , 'PR4' , 'PR5' , 'PR6' , 'PR7' , 'PR8',             
            'VA', 'VB', 'VC', 
            'IA', 'IB', 'IC', 
            'QA', 'QB', 'QC', 
            'PA', 'PB', 'PC', 
            'TA', 'TB', 'TC', 
            'F', 
            'Tax', 
            'RTC',
            'Model', 
            'FW Ver',
            'VBat',
            'M CRC',
            'Load',
            'idm',
            'PF A', 'PF B', 'PF C', 'PF S', 'PAng A', 'PAng B', 'PAng C', 'PAng S', 
            'Ph Ang AB', 'Ph Ang AC', 'Ph Ang BC'
            'LCD',
            'Phase'
        ]

        self.no_split_tbl = [ ['--------' for _ in range( len(self.split_head) ) ] ]
        split_tableModel = ttk.TTkTableModelList(data=self.no_split_tbl, header=self.split_head)        
        self.split_table = ttk.TTkTable(tableModel=split_tableModel)
        self.split_table.resizeRowsToContents()
        self.split_table.resizeColumnsToContents()
        
        self.split_frame = ttk.TTkFrame(border=True, visible=False)
        self.split_frame.setLayout(ttk.TTkVBoxLayout()) 
        self.split_frame.layout().addWidget(self.split_table)

            #---< Split 

        groups_tab = ttk.TTkTabWidget(border=False, visible=True)
        groups_tab.addTab(self.momentum_frame, " Momentum ")
        groups_tab.addTab(self.split_frame, " Split ")        

        self.group_frame = ttk.TTkFrame(border=True, visible=False)
        self.group_frame.setLayout(ttk.TTkVBoxLayout())
        self.group_frame.layout().addWidget(groups_tab)
        #---< Groups     

        tbl_tab = ttk.TTkTabWidget(border=False, visible=True)
        tbl_tab.addTab(self.line_frame, " Common ")
        tbl_tab.addTab(self.group_frame, " Groups ")
        # tbl_tab.addTab(self.months_frame, " Months ")  


        self.setLayout(ttk.TTkHBoxLayout())
        self.layout().addWidget(tbl_tab)


    def set_device(self, dev: mtr.MilurMeter):
        self.device = dev

        for item in self.g_view_items:
            item.set_device(dev)
            item.upd_from_dev()

    def upd_group(self):
        try:
            meas = self.device.rd_momentum()
        except Exception as e:
            txt = f'{str(e)}'
            meas = [ [txt] + ['--------' for _ in range( len(self.momentum_head )-1 ) ] ]

        momentum_tableModel = ttk.TTkTableModelList(data=[meas], header=self.momentum_head)  
        self.moment_table.setModel(momentum_tableModel)
        self.moment_table.resizeRowsToContents()
        self.moment_table.resizeColumnsToContents()

        try:
            meas = self.device.rd_split()
        except Exception as e:
            txt = f'{str(e)}'
            meas = [ [txt] + ['--------' for _ in range( len(self.split_head )-1 ) ] ]

        split_tableModel = ttk.TTkTableModelList(data=[meas], header=self.split_head)  
        self.split_table.setModel(split_tableModel)
        self.split_table.resizeRowsToContents()
        self.split_table.resizeColumnsToContents()

    def on_upd(self):
        # self.on_read_hh_cnt_btn()        
        for item in self.g_view_items:
            item.upd_from_dev()

        self.upd_group()

            

            
def main():

    root = ttk.TTk(title="test vew")
    root.setLayout(ttk.TTkGridLayout())
    root.layout().addWidget(RealFrame())
    root.mainloop()


if __name__ == "__main__":
    main()        