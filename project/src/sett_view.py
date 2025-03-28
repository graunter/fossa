import argparse
import random
from threading import Thread
import time
import TermTk as ttk        # pip install pyTermTk
from collections import defaultdict
import sys
import glob
import serial               #pip install pyserial
from my_const import *
import data_req as req
import pwr_meter as mtr
from pwr_meter import ReqId



class SettingsFrame(ttk.TTkFrame):

    def __init__(self, *,
                 name:str=None,
                 **kwargs) -> None:
        
        self.device = None

        super().__init__(name="name", **kwargs)


        self.head_tax_tbl = ['Time', 'Workday', 'Holiday', 'Saturday', 'Sunday'] 
        no_tax_tbl = [ ['--:--', '   -   ', '   -   ', '   -   ', '   -   '] ]

        tax_tableModel = ttk.TTkTableModelList(data=no_tax_tbl, header=self.head_tax_tbl)        

        self.tax_table = ttk.TTkTable(tableModel=tax_tableModel)
        self.tax_table.resizeRowsToContents()
        self.tax_table.resizeColumnsToContents()

        self.get_tax_btn = ttk.TTkButton(text='Read from device', border=True, maxHeight = 5 )
        self.get_tax_btn.clicked.connect(self.on_read_tax_btn)

        months_lst = ['JAN' , 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
        self.mlst = ttk.TTkComboBox(list=months_lst, text="Month", index=0)

        self.setLayout(ttk.TTkVBoxLayout())
        self.layout().addWidget(self.mlst)
        self.layout().addWidget(self.get_tax_btn)
        self.layout().addWidget(self.tax_table)

    def on_read_tax_btn(self):

        if not self.device:
            wrn_box = ttk.TTkMessageBox(
                title="Warning",
                text="No device is present"
            )
            ttk.TTkHelper.overlay(None, wrn_box, 50, 20, True)
            return 
        
        month = self.mlst.currentIndex()
        
        tax_tbl = self.device.rd_tax_tbl(month)
        tax_tableModel = ttk.TTkTableModelList(data=tax_tbl, header=self.head_tax_tbl)
        self.tax_table.setModel(tax_tableModel)


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