import argparse
import datetime
from datetime import datetime
import random
from threading import Thread
import time
import TermTk as ttk        # pip install pyTermTk
from collections import defaultdict
import sys
import glob
import serial               #pip install pyserial
from emeters.milur_const import *
import data_req as req
import emeters.milur_meter as mtr
from emeters.milur_meter_const import ReqId
from datetime import datetime



class SettingsFrame(ttk.TTkFrame):

    def __init__(self, *,
                 name:str=None,
                 **kwargs) -> None:
        
        self.device = None

        super().__init__(name="name", **kwargs)

        #---> Time
        self.rtc_dev = ttk.TTkLabel(text = 'NA')
        self.comp_time = ttk.TTkLabel(text = datetime.now().strftime('%S:%M:%H:%a:%d:%m:%Y') )
        self.time_diff = ttk.TTkLabel(text = 'NA')
        self.set_time_btn = ttk.TTkButton(text="Set current time", maxHeight=3)
        self.set_time_btn.clicked.connect(self.on_set_current_btn)
        self.adj_time_sec = ttk.TTkSpinBox(value=10, minimum=0, maximum=255, maxWidth = 25, maxHeight=3)
        self.adj_period_min = ttk.TTkSpinBox(value=1, minimum=0, maximum=255, maxWidth = 25, maxHeight=3)        
        self.soft_time_btn = ttk.TTkButton(text="Soft time correction", maxWidth = 25, maxHeight=3)
        self.soft_time_btn.clicked.connect(self.on_soft_correct_btn) 

        self.time_frame =  ttk.TTkFrame(visible=False)
        self.time_frame.setLayout(ttk.TTkGridLayout())

        self.time_frame.layout().addWidget(ttk.TTkLabel(text="Device time", maxWidth = 25, maxHeight=3), 0,0)          
        self.time_frame.layout().addWidget(self.rtc_dev, 0,1)
        self.time_frame.layout().addWidget(ttk.TTkLabel(text="Local time", maxWidth = 25, maxHeight=3), 1,0)         
        self.time_frame.layout().addWidget(self.comp_time, 1,1)    
        self.time_frame.layout().addWidget(ttk.TTkLabel(text="Time difference", maxWidth = 25, maxHeight=3), 2,0)          
        self.time_frame.layout().addWidget(self.time_diff, 2,1)    
        self.time_frame.layout().addWidget(self.set_time_btn, 3,1)  

        self.time_frame.layout().addWidget(ttk.TTkSpacer(maxHeight=3), 4,0)
        self.time_frame.layout().addWidget(ttk.TTkLabel(text="Soft time correction", maxWidth = 25, maxHeight=3), 5,0)        
         
        self.time_frame.layout().addWidget(ttk.TTkLabel(text="Adjust value in seconds", maxWidth = 25, maxHeight=3), 6,0)  
        self.time_frame.layout().addWidget(self.adj_time_sec, 6, 1)
        self.time_frame.layout().addWidget(ttk.TTkLabel(text="Duration in minutes", maxWidth = 25, maxHeight=3), 7,0)  
        self.time_frame.layout().addWidget(self.adj_period_min, 7, 1)
        self.time_frame.layout().addWidget(self.soft_time_btn, 8,1)         

        self.time_frame.layout().addWidget(ttk.TTkSpacer(), 10,3)
        self.time_frame.layout().addWidget(ttk.TTkSpacer(), 10,0)

        self.pause_visit_fl = True

        self.pull_visit_thrd = Thread(target=self.on_pull)
        self.pull_visit_thrd.daemon = True
        self.pull_visit_thrd.start()
        #---< Time

        #---> tax table
        self.head_tax_tbl = ['Time', 'Workday', 'Holiday', 'Saturday', 'Sunday'] 
        self.no_tax_tbl = [ ['--:--', '   -   ', '   -   ', '   -   ', '   -   '] ]

        tax_tableModel = ttk.TTkTableModelList(data=self.no_tax_tbl, header=self.head_tax_tbl)        

        self.tax_table = ttk.TTkTable(tableModel=tax_tableModel)
        self.tax_table.resizeRowsToContents()
        self.tax_table.resizeColumnsToContents()

        self.get_tax_btn = ttk.TTkButton(text='Read from device', border=True, maxHeight = 5 )
        self.get_tax_btn.clicked.connect(self.on_read_tax_btn)

        months_lst = ['JAN' , 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
        self.mlst = ttk.TTkComboBox(list=months_lst, text="Month", index=0)

        self.month_label = ttk.TTkLabel(text = f'{ self.mlst.currentText()}', maxHeight = 3)

        self.tax_frame = ttk.TTkFrame()
        self.tax_frame.setLayout(ttk.TTkVBoxLayout())
        self.tax_frame.layout().addWidget(self.mlst)
        self.tax_frame.layout().addWidget(self.get_tax_btn)
        self.tax_frame.layout().addWidget(self.month_label)
        self.tax_frame.layout().addWidget(self.tax_table)
        #---< tax table

        #---> holidays     
        self.hol_frame = ttk.TTkFrame()
        self.hol_frame.setLayout(ttk.TTkVBoxLayout())


        self.head_hol_tbl = ['Day', 'Month', ] 
        self.no_hol_tbl = [ ['--------' for _ in range( len(self.head_hol_tbl) ) ] ]

        hol_tableModel = ttk.TTkTableModelList(data=self.no_hol_tbl, header=self.head_hol_tbl)        

        self.hol_table = ttk.TTkTable(tableModel=hol_tableModel)
        self.hol_table.resizeRowsToContents()
        self.hol_table.resizeColumnsToContents()

        self.get_hol_btn = ttk.TTkButton(text='Read from device', border=True, maxHeight = 5 )
        self.get_hol_btn.clicked.connect(self.on_read_hol_btn)

        self.hol_frame = ttk.TTkFrame(border=True, visible=False)
        self.hol_frame.setLayout(ttk.TTkVBoxLayout())    
        self.hol_frame.layout().addWidget(self.get_hol_btn)
        self.hol_frame.layout().addWidget(self.hol_table)

        #---< holidays

        #---> PWI records

        self.rec_frame = ttk.TTkFrame()
        self.rec_frame.setLayout(ttk.TTkVBoxLayout())

        self.clear_hh_table_btn = ttk.TTkButton(text='Clear hours pwi', border=True, maxHeight = 5 )
        self.clear_hh_table_btn.clicked.connect(self.on_clear_hh_tbl_btn)        

        self.rec_frame.layout().addWidget(self.clear_hh_table_btn)

        #---< PWI records

        tbl_tab = ttk.TTkTabWidget(border=False, visible=True)
        tbl_tab.addTab(self.time_frame, " Device time ")        
        tbl_tab.addTab(self.tax_frame, " tax table ")
        tbl_tab.addTab(self.hol_frame, " holidays ")
        tbl_tab.addTab(self.rec_frame, " Init ")


        self.setLayout(ttk.TTkVBoxLayout())
        self.layout().addWidget(tbl_tab)        


    def on_pull(self):

        while True:   
            if not self.pause_visit_fl:
                try:
                    # for item in g_view_items:
                    #     item.upd_from_dev()
                    if self.time_frame.isVisible() and self.isVisible():
                        if self.device:
                            remote_rtc = self.device.rd_str(ReqId.rtc)
                            self.rtc_dev.setText(remote_rtc)

                        format_string = '%S:%M:%H:%a:%d:%b:%Y'

                        try:
                            comp_time = datetime.now()
                            self.comp_time.setText(comp_time.strftime(format_string))

                            remote_rtc_dtime = datetime.strptime(remote_rtc, format_string)
                            time_diff = comp_time - remote_rtc_dtime
                            self.time_diff.setText(str(time_diff))

                        except Exception as e:
                            pass

                except serial.SerialException as e:
                    #todo
                    pass

            time.sleep(0.1)   


    def on_read_hol_btn(self):
        
        try:
            hol_tbl = self.device.rd_holidays_tbl()
        except Exception as e:
            err_box = ttk.TTkMessageBox( title="Err",  text=f'{str(e)}' )
            ttk.TTkHelper.overlay(None, err_box, 50, 20, True)

        
        tableModel = ttk.TTkTableModelList(data=hol_tbl, header=self.head_hol_tbl)
        self.hol_table.setModel(tableModel)
        self.hol_table.resizeRowsToContents()
        # self.hol_table.resizeColumnsToContents()

    def on_soft_correct_btn(self):
        try:
            self.pause_visit_fl = True
            time.sleep(1)
   
            self.device.wr_soft_time(self.adj_time_sec.value(), self.adj_period_min.value())
            self.pause_visit_fl = False            
        except Exception as e:
            # TODO: unexpected error sometime happened
            err_box = ttk.TTkMessageBox( title="Err",  text=f'{str(e)}' )
            ttk.TTkHelper.overlay(None, err_box, 50, 20, True)
            self.pause_visit_fl = False          

    def on_set_current_btn(self):

        try:


            self.pause_visit_fl = True
            time.sleep(1)
            dt = datetime.now()     
            # just for testing
            # dt = dt.replace(second = 1, minute = 2, hour = 3)       
            self.device.wr_rtc(dt)
            self.pause_visit_fl = False            
        except Exception as e:
            # TODO: unexpected error sometime happened
            err_box = ttk.TTkMessageBox( title="Err",  text=f'{str(e)}' )
            ttk.TTkHelper.overlay(None, err_box, 50, 20, True)
            self.pause_visit_fl = False  
            

    def on_read_tax_btn(self):
       
        month = self.mlst.currentIndex()
        
        tax_tbl = self.no_tax_tbl
        try:
            tax_tbl = self.device.rd_tax_tbl(month)
        except Exception as e:
            err_box = ttk.TTkMessageBox( title="Err",  text=f'{str(e)}' )
            ttk.TTkHelper.overlay(None, err_box, 50, 20, True)

        tax_tableModel = ttk.TTkTableModelList(data=tax_tbl, header=self.head_tax_tbl)
        self.tax_table.setModel(tax_tableModel)
        self.tax_table.resizeRowsToContents()
        # self.tax_table.resizeColumnsToContents()

        self.month_label.setText(f'{ self.mlst.currentText()}')

    def set_device(self, dev: mtr.MilurMeter):
        self.device = dev
        self.pause_visit_fl = False 

    def on_upd(self):
        self.on_read_tax_btn()



    def on_clear_hh_tbl_btn(self):

        try:
            self.device.clr_pwi_record()

        except Exception as e:
            err_box = ttk.TTkMessageBox( title="Err",  text=f'{str(e)}' )
            ttk.TTkHelper.overlay(None, err_box, 50, 20, True)
            return




def main():

    root = ttk.TTk(title="test vew")

    root.setLayout(ttk.TTkGridLayout())

    root.layout().addWidget(SettingsFrame())
    
    root.mainloop()


if __name__ == "__main__":
    main()        