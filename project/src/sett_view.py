import argparse
import random
from threading import Thread
import time
import TermTk as ttk        # pip install pyTermTk
from collections import defaultdict
import sys
import glob
import serial               #pip install pyserial
from milur_const import *
import data_req as req
import milur_meter as mtr
from milur_meter import ReqId



class SettingsFrame(ttk.TTkFrame):

    def __init__(self, *,
                 name:str=None,
                 **kwargs) -> None:
        
        self.device = None

        super().__init__(name="name", **kwargs)


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

        tbl_tab = ttk.TTkTabWidget(border=False, visible=True)
        tbl_tab.addTab(self.tax_frame, " tax table ")
        tbl_tab.addTab(self.hol_frame, " holidays ")


        self.setLayout(ttk.TTkVBoxLayout())
        self.layout().addWidget(tbl_tab)        

    def on_read_hol_btn(self):
        
        try:
            hol_tbl = self.device.rd_holidays_tbl()
        except Exception as e:
            err_box = ttk.TTkMessageBox( title="Err",  text=f'{str(e)}' )
            ttk.TTkHelper.overlay(None, err_box, 50, 20, True)

        
        tableModel = ttk.TTkTableModelList(data=hol_tbl, header=self.head_hol_tbl)
        self.hol_table.setModel(tableModel)
        self.hol_table.resizeRowsToContents()
        self.hol_table.resizeColumnsToContents()

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
        self.tax_table.resizeColumnsToContents()

        self.month_label.setText(f'{ self.mlst.currentText()}')

    def set_device(self, dev: mtr.PwrMeter):
        self.device = dev

    def on_upd(self):
        self.on_read_tax_btn()



def main():

    root = ttk.TTk(title="test vew")

    root.setLayout(ttk.TTkGridLayout())

    root.layout().addWidget(SettingsFrame())
    
    root.mainloop()


if __name__ == "__main__":
    main()        