import TermTk as ttk
import emeters.milur_meter as mtr

class DataRequest(ttk.TTkFrame):
    
    def __init__(self
            , **kwargs) -> None:
        
        super().__init__(
            border=False
            , visible=True
            , layout = ttk.TTkGridLayout()
            # , minWidth = 60
            ,  **kwargs)

        self.device = None
        
        self.start_column = 0
        self.name_column = self.start_column
        self.data_column = self.name_column +1
        self.units_column = self.data_column +1

        self.def_name_w = 25
        self.def_data_w = 25
        self.def_unit_w = 20

        self.def_name_size = 25
        self.def_data_size = 25
        self.def_unit_size = 30


    def set_device(self, dev: mtr.MilurMeter):
        self.device = dev

    def upd_from_dev(self):
        pass

class DataSRequest(DataRequest):
   
    def __init__(self, *
            , label: ttk.TTkString = "Param name"
            , data: ttk.TTkString = "NA"
            , unit: ttk.TTkString = ""
            , req = None
            , **kwargs) -> None:     
        
        super().__init__( **kwargs )
 
        self.label_txt = label
        self.data_txt = data
        self.unit_txt = unit
        self.req = req
        
        line_cnt = 0


        self.layout().addWidget(ttk.TTkLabel(text=self.label_txt, size=(self.def_name_size,1), maxWidth = self.def_name_w), line_cnt, self.name_column)
        self.data_item = ttk.TTkLineEdit(text=self.data_txt, size=(self.def_data_size,1), maxWidth = self.def_data_w)
        self.data_item.setEnabled(False)
        self.layout().addWidget(self.data_item, line_cnt, self.data_column)
        self.layout().addWidget(ttk.TTkLabel(text=self.unit_txt, size=(self.def_unit_size,1), maxWidth = self.def_unit_w), line_cnt, self.units_column)    
        self.layout().addWidget(ttk.TTkSpacer())


    def upd_from_dev(self):
        if not self.device:
            self.data_item.setText("no device")
            return

        if self.req:
            try:
                txt = self.req(self.device)
            except Exception as e:
                txt = f'{str(e)}'
    
            self.data_item.setText(txt)


class DataQRequest(DataRequest):
   
    def __init__(self, *
            , score: ttk.TTkString = ""
            , label: list[ttk.TTkString] = ["1", "2", "3", "4"]
            , data: list[ttk.TTkString] = ["NA"]
            , unit: list[ttk.TTkString] = [""]
            , req = None
            , **kwargs) -> None:     
        
        super().__init__( **kwargs )
 
        self.label_txt = label
        self.data_txt = data
        self.unit_txt = unit
        self.req = req
        self.data_item = []
        
        line_cnt = 0

        self.setBorder(True)
        self.setTitle(score)
        self.setTitleAlign( ttk.TTkCore.TTkConstant.LEFT_ALIGN )

        for pos, lab in enumerate(label):
            self.layout().addWidget(
                ttk.TTkLabel(text=self.label_txt[pos], size=(self.def_name_size,1), maxWidth = self.def_name_w), line_cnt, self.name_column
            )

            txt = self.data_txt[pos] if pos < len(self.data_txt) else ""
                
            self.data_item.append( dat:= ttk.TTkLineEdit(text=txt, size=(self.def_data_size,1), maxWidth = self.def_data_w) )
            dat.setEnabled(False)
            self.layout().addWidget(dat, line_cnt, self.data_column)

            txt = self.unit_txt[pos] if pos < len(self.unit_txt) else ""
            self.layout().addWidget(
                ttk.TTkLabel(text=txt, size=(self.def_unit_size,1), maxWidth = self.def_unit_w), line_cnt, self.units_column
            )    

            self.layout().addWidget(ttk.TTkSpacer())

            line_cnt += 1


    def upd_from_dev(self):
        if not self.device:
            self.data_item.setText("no device")
            return

        if self.req:
            try:
                txt = self.req(self.device)
            except Exception as e:
                txt = f'{str(e)}'
    
            if len(self.data_item) >0:
                self.data_item[0].setText(txt)