import argparse
import random
from threading import Thread
import time
import TermTk as ttk        # pip install pyTermTk
from collections import defaultdict
from my_const import *
import data_req as req
import pwr_meter as mtr
from pwr_meter import ReqId



class RecordsFrame(ttk.TTkFrame):

    def __init__(self, *,
                 name:str=None,
                 **kwargs) -> None:
        
        self.device = None

        super().__init__(name="name", **kwargs)

        self.head_ENTARecord_tbl = ['Time', 
            'Sum in A PWR','Sum in A PWR 1','Sum in A PWR 2','Sum in A PWR 3','Sum in A PWR 4','Sum in A PWR 5','Sum in A PWR 6','Sum in A PWR 7','Sum in A PWR 8',
            'Sum out A PWR', 'Sum out A PWR 1','Sum out A PWR 2','Sum out A PWR 3','Sum out A PWR 4','Sum out A PWR 5','Sum out A PWR 6','Sum out A PWR 7','Sum out A PWR 8',
            'Sum in R PWR','Sum in R PWR 1','Sum in R PWR 2','Sum in R PWR 3','Sum in R PWR 4','Sum in R PWR 5','Sum in R PWR 6','Sum in R PWR 7','Sum in R PWR 8',
            'Sum out R PWR', 'Sum out R PWR 1','Sum out R PWR 2','Sum out R PWR 3','Sum out R PWR 4','Sum out R PWR 5','Sum out R PWR 6','Sum out R PWR 7','Sum out R PWR 8',            
        ] 

        #--->
        self.get_hh_rec_btn = ttk.TTkButton(text='Read total counts', border=True, maxHeight = 5 )
        self.get_hh_rec_btn.clicked.connect(self.on_read_hh_cnt_btn)

        btns_hh_frame = ttk.TTkFrame()
        btns_hh_frame.setLayout( ttk.TTkHBoxLayout() )

        len_lst = ['Last' , '10', '100', '1000', 'All']
        self.mlst = ttk.TTkComboBox(list=len_lst, text="Month", index=0)

        self.get_hh_table_btn = ttk.TTkButton(text='Read records', border=True, maxHeight = 5 )
        self.get_hh_table_btn.clicked.connect(self.on_read_hh_tbl_btn)        

        btns_hh_frame.layout().addWidget(self.get_hh_rec_btn)
        btns_hh_frame.layout().addWidget(self.mlst)
        btns_hh_frame.layout().addWidget(self.get_hh_table_btn)
        #---<


        self.head_tax_tbl = ['Time', 'Active in Pwr', 'Active out Pwr', 'Done'] 
        no_tax_tbl = [ ['-----------------------' for _ in range( len(self.head_tax_tbl) ) ] ]

        tax_tableModel = ttk.TTkTableModelList(data=no_tax_tbl, header=self.head_tax_tbl)        

        self.tax_table = ttk.TTkTable(tableModel=tax_tableModel)
        self.tax_table.resizeRowsToContents()
        self.tax_table.resizeColumnsToContents()



        self.half_hours_frame = ttk.TTkFrame(border=True, visible=False)

        self.half_hours_frame.setLayout(ttk.TTkVBoxLayout())
        self.half_hours_frame.layout().addWidget(btns_hh_frame)        
        self.half_hours_frame.layout().addWidget(self.tax_table) 



        #---> months
        self.months_frame = ttk.TTkFrame(border=True, visible=False)

        self.get_m_rec_btn = ttk.TTkButton(text='Read total counts', border=True, maxHeight = 5 )
        self.get_m_rec_btn.clicked.connect(self.on_read_m_cnt_btn)

        self.get_m_table_btn = ttk.TTkButton(text='Read records', border=True, maxHeight = 5 )
        self.get_m_table_btn.clicked.connect(self.on_read_m_tbl_btn)

        self.head_m_tax_tbl = self.head_ENTARecord_tbl

        no_tax_m_tbl = [ ['--------' for _ in range( len(self.head_m_tax_tbl) ) ] ]

        tax_m_tableModel = ttk.TTkTableModelList(data=no_tax_m_tbl, header=self.head_m_tax_tbl)        

        self.tax_m_table = ttk.TTkTable(tableModel=tax_m_tableModel)
        self.tax_m_table.resizeRowsToContents()
        self.tax_m_table.resizeColumnsToContents()

        self.months_frame.setLayout(ttk.TTkVBoxLayout())
        self.months_frame.layout().addWidget(self.get_m_rec_btn)
        self.months_frame.layout().addWidget(self.get_m_table_btn)
        self.months_frame.layout().addWidget(self.tax_m_table)

        #---<

        #---> days
        self.days_frame = ttk.TTkFrame(border=True, visible=False)

        self.get_d_rec_btn = ttk.TTkButton(text='Read total counts', border=True, maxHeight = 5 )
        self.get_d_rec_btn.clicked.connect(self.on_read_d_cnt_btn)

        self.get_d_table_btn = ttk.TTkButton(text='Read records', border=True, maxHeight = 5 )
        self.get_d_table_btn.clicked.connect(self.on_read_d_tbl_btn)

        self.head_d_tax_tbl = self.head_ENTARecord_tbl

        no_tax_d_tbl = [ ['--------' for _ in range( len(self.head_d_tax_tbl) ) ] ]

        tax_d_tableModel = ttk.TTkTableModelList(data=no_tax_d_tbl, header=self.head_d_tax_tbl)        

        self.tax_d_table = ttk.TTkTable(tableModel=tax_d_tableModel)
        self.tax_d_table.resizeRowsToContents()
        self.tax_d_table.resizeColumnsToContents()

        self.days_frame.setLayout(ttk.TTkVBoxLayout())
        self.days_frame.layout().addWidget(self.get_d_rec_btn)
        self.days_frame.layout().addWidget(self.get_d_table_btn)
        self.days_frame.layout().addWidget(self.tax_d_table)

        #---<


        tbl_tab = ttk.TTkTabWidget(border=False, visible=True)
        tbl_tab.addTab(self.half_hours_frame, " Hours ")
        tbl_tab.addTab(self.days_frame, " Days ")
        tbl_tab.addTab(self.months_frame, " Months ")  


        self.setLayout(ttk.TTkHBoxLayout())
        self.layout().addWidget(tbl_tab)

    def on_read_d_tbl_btn(self):
        try:

            cur_idx = self.device.rd_d_tax_current()
            total_cnt = self.device.rd_d_tax_total()
        
            #cur_idx += 1
            rd_idx = cur_idx
            pwi_tbl = []
            for i in range(total_cnt):
                pwi_rec = self.device.rd_d_record(rd_idx)
                pwi_tbl.append(pwi_rec)
                rd_idx -=1
                if rd_idx < 0:
                    rd_idx = 122

            tax_tableModel = ttk.TTkTableModelList(data=pwi_tbl, header=self.head_d_tax_tbl) 
            self.tax_d_table.setModel(tax_tableModel) 
            self.tax_d_table.resizeRowsToContents()
            self.tax_d_table.resizeColumnsToContents()            

        except Exception as e:
            err_box = ttk.TTkMessageBox( title="Err",  text=f'{str(e)}' )
            ttk.TTkHelper.overlay(None, err_box, 50, 20, True)
            return        

    def on_read_d_cnt_btn(self):
        cur_idx = self.device.rd_d_tax_current()
        total_cnt = self.device.rd_d_tax_total()
    
        wrn_box = ttk.TTkMessageBox(
            title="Info",
            text=f'total = {str(total_cnt)}, current is {str(cur_idx)}'
        )
        ttk.TTkHelper.overlay(None, wrn_box, 50, 20, True)

    def on_read_m_cnt_btn(self):

        cur_idx = self.device.rd_m_tax_current()
        total_cnt = self.device.rd_m_tax_total()


        wrn_box = ttk.TTkMessageBox(
            title="Info",
            text=f'total = {str(total_cnt)}, current is {str(cur_idx)}'
        )
        ttk.TTkHelper.overlay(None, wrn_box, 50, 20, True)


    def on_read_m_tbl_btn(self):
        try:
            cur_idx = self.device.rd_m_tax_current()
            total_cnt = self.device.rd_m_tax_total()

            #cur_idx += 1
            rd_idx = cur_idx
            pwi_tbl = []
            for i in range(total_cnt):
                pwi_rec = self.device.rd_m_record(rd_idx)
                pwi_tbl.append(pwi_rec)
                rd_idx -=1
                if rd_idx < 0:
                    rd_idx = 11

            tax_tableModel = ttk.TTkTableModelList(data=pwi_tbl, header=self.head_m_tax_tbl) 
            self.tax_m_table.setModel(tax_tableModel) 
            self.tax_m_table.resizeRowsToContents()
            self.tax_m_table.resizeColumnsToContents()            

        except Exception as e:
            err_box = ttk.TTkMessageBox( title="Err",  text=f'{str(e)}' )
            ttk.TTkHelper.overlay(None, err_box, 50, 20, True)
            return
        


    def on_read_hh_tbl_btn(self):

        try:
            cur_idx = self.device.rd_total_tax_current()

            match self.mlst.currentIndex():
                case 0:  # Last
                    total_cnt = 1
                    # pwi_rec = self.device.rd_pwi_record(cur_idx)
                    # tax_tableModel = ttk.TTkTableModelList(data=[pwi_rec], header=self.head_tax_tbl) 
                    # self.tax_table.setModel(tax_tableModel)
                    # return
                case 4:
                    total_cnt = self.device.rd_total_tax_count()                
                case 1 | 2 | 3:
                    total_cnt = 10 ** self.mlst.currentIndex()
                    total_tbl_cnt = self.device.rd_total_tax_count()

                    total_cnt = min(total_cnt, total_tbl_cnt)

            cur_idx += 1
            rd_idx = cur_idx
            pwi_tbl = []
            for i in range(total_cnt):
                pwi_rec = self.device.rd_pwi_record(rd_idx)
                pwi_tbl.append(pwi_rec)
                rd_idx -=1
                if rd_idx < 0:
                    rd_idx = 5903

            tax_tableModel = ttk.TTkTableModelList(data=pwi_tbl, header=self.head_tax_tbl) 
            self.tax_table.setModel(tax_tableModel) 
            self.tax_table.resizeRowsToContents()
            self.tax_table.resizeColumnsToContents()

        except Exception as e:
            err_box = ttk.TTkMessageBox( title="Err",  text=f'{str(e)}' )
            ttk.TTkHelper.overlay(None, err_box, 50, 20, True)
            return


    def on_read_hh_cnt_btn(self):

        if not self.device:
            wrn_box = ttk.TTkMessageBox(
                title="Warning",
                text="No device is present"
            )
            ttk.TTkHelper.overlay(None, wrn_box, 50, 20, True)
            return 
        
        total_cnt = self.device.rd_total_tax_count()
        cur_idx = self.device.rd_total_tax_current()

        wrn_box = ttk.TTkMessageBox(
            title="Info",
            text=f'total = {str(total_cnt)}, current is {str(cur_idx)}'
        )
        ttk.TTkHelper.overlay(None, wrn_box, 50, 20, True)
        

    def set_device(self, dev: mtr.PwrMeter):
        self.device = dev

    def on_upd(self):
        self.on_read_hh_cnt_btn()



def main():

    root = ttk.TTk(title="test vew")
    root.setLayout(ttk.TTkGridLayout())
    root.layout().addWidget(RecordsFrame())
    root.mainloop()


if __name__ == "__main__":
    main()        