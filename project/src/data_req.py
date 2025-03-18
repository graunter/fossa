import TermTk as ttk
import pwr_meter as mtr

class DataRequest(ttk.TTkFrame):
     
    def __init__(self, *
            , label: ttk.TTkString = "Param name"
            , data: ttk.TTkString = "NA"
            , unit: ttk.TTkString = ""
            , request = None
            , **kwargs) -> None:
        
        super().__init__(
            border=False
            , visible=True
            , layout = ttk.TTkGridLayout()
            # , minWidth = 60
            ,  **kwargs)

        self.label_txt = label
        self.data_txt = data
        self.unit_txt = unit
        self.device = None
        
        start_column = 0
        name_column = start_column
        data_column = name_column +1
        units_column = data_column +1

        def_name_w = 20
        def_data_w = 20
        def_unit_w = 20

        def_name_size = 20
        def_data_size = 20
        def_unit_size = 30

        line_cnt = 0


        self.layout().addWidget(ttk.TTkLabel(text=self.label_txt, size=(def_name_size,1), maxWidth = def_name_w), line_cnt, name_column)
        self.data_item = ttk.TTkLineEdit(text=self.data_txt, size=(def_data_size,1), maxWidth = def_data_w)
        self.data_item.setEnabled(False)
        self.layout().addWidget(self.data_item, line_cnt, data_column)
        self.layout().addWidget(ttk.TTkLabel(text=self.unit_txt, size=(def_unit_size,1), maxWidth = def_unit_w), line_cnt, units_column)    

    def set_device(self, dev: mtr.PwrMeter):
        self.device = dev

    def upd_from_dev(self):
        txt = self.device.rd_str(mtr.StrData.model)
        self.data_item.setText(txt)
        
