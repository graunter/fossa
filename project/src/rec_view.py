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


        self.get_rec_btn = ttk.TTkButton(text='Read total counts from device', border=True, maxHeight = 5 )
        self.get_rec_btn.clicked.connect(self.on_read_cnt_btn)

        months_lst = ['JAN' , 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
        self.mlst = ttk.TTkComboBox(list=months_lst, text="Month", index=0)


        self.head_tax_tbl = ['Time', 'DoW', 'Month', 'Year', 'Active Pwr', 'Done'] 
        no_tax_tbl = [ ['--:--', '   -   ', '   -   ', '   -   ', '   -   ', '   -   '] ]

        tax_tableModel = ttk.TTkTableModelList(data=no_tax_tbl, header=self.head_tax_tbl)        

        self.tax_table = ttk.TTkTable(tableModel=tax_tableModel)
        self.tax_table.resizeRowsToContents()
        self.tax_table.resizeColumnsToContents()

        self.setLayout(ttk.TTkVBoxLayout())
        self.layout().addWidget(self.mlst)
        self.layout().addWidget(self.get_rec_btn)
        self.layout().addWidget(self.tax_table)        


    def on_read_cnt_btn(self):

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
        self.on_read_cnt_btn()



def main():

    root = ttk.TTk(title="test vew")
    root.setLayout(ttk.TTkGridLayout())
    root.layout().addWidget(RecordsFrame())
    root.mainloop()


if __name__ == "__main__":
    main()        