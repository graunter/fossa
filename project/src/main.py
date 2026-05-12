import argparse
from threading import Thread, Semaphore
import time
import TermTk as ttk        # pip install pyTermTk
from collections import defaultdict
import sys
import glob
import serial               #pip install pyserial
from emeters.milur_const import *
import data_req as req
from hw_frame import HardInfoFrame
from real_view import RealFrame
import emeters.milur_meter as mtr
# from emeters.milur_meter_const import ReqId
from emeters.milur_meter_const import ReqId
import sett_view as sview
import rec_view as rview
from proba import run_tester

view_frames = defaultdict(list)


g_current_frame = None
g_mb_open_btn: ttk.TTkButton
g_ser: serial.Serial
g_sema: Semaphore
g_mb_port_name: ttk.TTkLineEdit
g_pause_visit_fl = True
g_read_err_counter = 0
g_pull_visit_thrd = None
g_cnt_lst = []
g_info_frame: HardInfoFrame
g_mb_adr_ledit: ttk.TTkLineEdit
g_mb_detect_btn: ttk.TTkButton
g_sett_frame: sview.SettingsFrame
g_rec_frame: rview.RecordsFrame
r1: ttk.TTkRadioButton
r2: ttk.TTkRadioButton
r3: ttk.TTkRadioButton
pass1: ttk.TTkLineEdit
pass2: ttk.TTkLineEdit
pass3: ttk.TTkLineEdit

def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """

    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass

    return result


def switch_frame(next_frame: ttk.TTkFrame):
    global g_current_frame

    if g_current_frame != None:
        g_current_frame.setVisible(False)

    next_frame.setVisible(True)

    g_current_frame = next_frame




def create_btn_for_frame(init_state: bool, next_frame: ttk.TTkFrame) -> ttk.TTkButton:
    global g_current_frame

    text_for_btn = next_frame.title()
    new_btn = ttk.TTkButton(border=True, text=text_for_btn, minHeight=3)
    new_btn.setChecked(init_state)

    if init_state == True:
        g_current_frame = next_frame
        next_frame.setVisible(True)

    new_btn.clicked.connect(lambda: switch_frame(next_frame))

    return new_btn


def close_serial():
    global g_ser
    global g_pause_visit_fl
    global g_cnt_lst

    g_ser.close()
    g_mb_open_btn.setChecked(False)

    g_cnt_lst.clear()

    bg_color = ttk.TTkColor.BG_WHITE
    btn_text=ttk.TTkString(' Open ', bg_color)
    g_mb_open_btn.setText(btn_text)

    g_pause_visit_fl = True


def on_mb_open_btn():
    global g_mb_open_btn
    global g_ser
    global g_mb_port_name
    global g_pause_visit_fl
    global g_read_err_counter
    global g_pull_visit_thrd
    global g_cnt_lst
    global g_sema
    global r2
    global r3
    global pass1
    global pass2
    global pass3

    port_name = g_mb_port_name.text()

    try:
        if 'Open' in g_mb_open_btn.text().toAscii():
            g_ser = serial.Serial(
                port=str(port_name)
                , baudrate=9600
                , bytesize=8
                , parity='N'
                , stopbits=1
                , timeout=0.1
                , rtscts=False
                , dsrdtr=False
            )
            g_sema = Semaphore()
        else:
            close_serial()
            return
    except serial.SerialException as e:
        err_box = ttk.TTkMessageBox(
                title="Serial port error",
                text=format(e)
            )
        ttk.TTkHelper.overlay(None, err_box, 50, 20, True)
        return
    
    # mb_adr = int(g_mb_adr_ledit.text().toAscii())
    if not g_mb_adr_ledit.currentText():
        return
    else:
        mb_adr = int(g_mb_adr_ledit.currentText().toAscii())
        
    if mtr.MilurMeter.check_resp_on_adr(mb_adr, g_ser) == True:
        bg_color = ttk.TTkColor.BG_GREEN

        adapter = mtr.MilurMeter(mb_adr)#, g_ser, g_sema))
        #TODO: semaphore must be set here
        adapter.link(g_ser)#, g_sema)

        access_lvl = ACCESS_LVL_USER
        pass_string = pass1.text()


        if r1.checkState() is ttk.TTkK.Checked:
            access_lvl = ACCESS_LVL_USER
            pass_string = pass1.text()
        if r2.checkState() is ttk.TTkK.Checked:
            access_lvl = ACCESS_ADM_USER
            pass_string = pass2.text()
        elif r3.checkState() is ttk.TTkK.Checked:
            access_lvl = ACCESS_DEV_USER
            pass_string = pass3.text()

        pass_for_dev = [int(h, 16) for h in pass_string._text.split()]

        # if ACCESS_LVL_USER != access_lvl:
            # adapter.login(access_lvl, pass_for_dev)

        adapter.login(access_lvl, pass_for_dev)

        g_cnt_lst.append(adapter)

        g_info_frame.set_device(g_cnt_lst[0])
        g_info_frame.on_upd()

        g_view_frame.set_device(g_cnt_lst[0])

        g_sett_frame.set_device(g_cnt_lst[0])
        g_sett_frame.on_upd()

        g_rec_frame.set_device(g_cnt_lst[0])

    else:
        bg_color = ttk.TTkColor.BG_RED
        wrn_box = ttk.TTkMessageBox(
                title="Warning",
                text="The port is open, but no devices were found at this address!"
            )
        ttk.TTkHelper.overlay(None, wrn_box, 50, 20, True)

    text=ttk.TTkString(' Close ', bg_color)
    g_mb_open_btn.setText(text)
    
    g_read_err_counter = 0


    g_pause_visit_fl = False
    if not g_pull_visit_thrd:
        g_pull_visit_thrd = Thread(target=on_visit_pull)
        g_pull_visit_thrd.daemon = True
        g_pull_visit_thrd.start()


def on_mb_detect_btn():
    global g_ser
    global g_mb_port_name
    global g_mb_adr_ledit
    global g_mb_detect_btn
    global g_current_frame

    port_name = g_mb_port_name.text()

    try:
        if 'Open' in g_mb_open_btn.text().toAscii():
            g_ser = serial.Serial(
                port=str(port_name)
                , baudrate=9600
                , bytesize=8
                , parity='N'
                , stopbits=1
                , timeout=0.1
                , rtscts=False
                , dsrdtr=False
            )
            g_sema = Semaphore()
        else:
            close_serial()
            return
    except serial.SerialException as e:
        err_box = ttk.TTkMessageBox(
                title="Serial port error",
                text=format(e)
            )
        ttk.TTkHelper.overlay(None, err_box, 50, 20, True)
        return


    try:
        bus_adr = []
        for test_adr in range(1, 25):
            g_mb_detect_btn.setText(f"Check {str(test_adr)}")
            g_mb_detect_btn.update()
            ttk.TTkLog.debug(f"check addres {str(test_adr)}")
            if mtr.MilurMeter.check_resp_on_adr(test_adr, g_ser) == True:
                bus_adr.append(str(test_adr))
        
        g_mb_detect_btn.setText(f"Detect..")
        close_serial()

        old_adr = g_mb_adr_ledit.currentText()

        g_mb_adr_ledit.clear()
        if bus_adr:
            g_mb_adr_ledit.addItems(bus_adr)
            if old_adr in bus_adr:
                g_mb_adr_ledit.setCurrentText(old_adr)
            else:
                g_mb_adr_ledit.setCurrentText(bus_adr[0])   

    except Exception as e:
        err_box = ttk.TTkMessageBox( title="General error", text=format(e) )
        ttk.TTkHelper.overlay(None, err_box, 50, 20, True)
        close_serial()        
        return



def on_visit_pull():


    while True:   
        if not g_pause_visit_fl:
            try:
                # for item in g_view_items:
                #     item.upd_from_dev()
                if g_view_frame.isVisible():
                    g_view_frame.on_upd()

            except serial.SerialException as e:
                err_box = ttk.TTkMessageBox(
                        title="Serial port error - it will be closed!",
                        text=format(e)
                    )
                ttk.TTkHelper.overlay(None, err_box, 50, 20, True)
                close_serial()

        time.sleep(1)   




def build_main_screen(root=None):
    global g_current_frame
    global g_mb_open_btn
    global g_mb_port_name
    global g_info_frame
    global g_mb_adr_ledit
    global g_mb_detect_btn
    global g_view_frame
    global g_sett_frame
    global g_rec_frame
    global r1
    global r2
    global r3
    global pass1
    global pass2
    global pass3
    
    root_layout = ttk.TTkGridLayout()
    root.setLayout(root_layout)

    btn_frame = ttk.TTkFrame(parent=root)
    btn_layout = ttk.TTkGridLayout()
    btn_frame.setLayout(btn_layout)

    top_btn_frame = ttk.TTkFrame(border=False, maxWidth = 20)
    top_btn_layout = ttk.TTkVBoxLayout()
    top_btn_frame.setLayout(top_btn_layout)

    # Frames for used data
    login_frame = ttk.TTkFrame(border=True, title="Login", visible=True)
    g_info_frame = HardInfoFrame(border=True, title="HW Info", visible=False)
    g_sett_frame = sview.SettingsFrame(border=True, title="Config", visible=False)
    g_rec_frame = rview.RecordsFrame(border=True, title="Records", visible=False)
    service_frame = ttk.TTkFrame(border=True, title="Service", visible=False)
    g_view_frame = RealFrame(border=True, title="View", visible=False)

    top_btn_frame.addWidget(create_btn_for_frame(True, login_frame))
    top_btn_frame.addWidget(create_btn_for_frame(False, g_info_frame))
    top_btn_frame.addWidget(create_btn_for_frame(False, g_view_frame))
    top_btn_frame.addWidget(create_btn_for_frame(False, g_rec_frame))    
    top_btn_frame.addWidget(create_btn_for_frame(False, g_sett_frame))
    top_btn_frame.addWidget(create_btn_for_frame(False, service_frame))    



    btn_layout.addWidget(top_btn_frame, 1, 0)

    mid_btn_frame = ttk.TTkFrame(border=False)
    btn_layout.addWidget(mid_btn_frame, 2,0)

    bot_btn_frame = ttk.TTkFrame(border=False)
    bot_btn_frame_layout=ttk.TTkVBoxLayout()
    bot_btn_frame.setLayout(bot_btn_frame_layout)
  

    log_inp_togler = ttk.TTkCheckbox(text="Log", checked=False)
    bot_btn_frame_layout.addWidget(log_inp_togler)
    log_inp_togler.stateChanged.connect(lambda x: log_wnd.setVisible(x==ttk.TTkK.Checked))

    exit_btn = ttk.TTkButton(border=True, text="Exit", maxHeight = 5)
    bot_btn_frame_layout.addWidget(exit_btn)  
    exit_btn.clicked.connect(ttk.TTkHelper.quit) 
    
    btn_layout.addWidget(bot_btn_frame, 5,0) 


    main_frame = ttk.TTkFrame(border=False, title="Main")
    root_layout.addWidget(main_frame, 0, 2)
    mframe_layout = ttk.TTkVBoxLayout()
    main_frame.setLayout(mframe_layout)

    #TODO: should be done in one time with button
    mframe_layout.addWidgets([login_frame, g_info_frame, g_view_frame, g_sett_frame, g_rec_frame, service_frame])

    
    log_wnd = ttk.TTkWindow(parent=main_frame, pos = (15,4), size=(87,20), title="Log Window", flags=0, visible=False)
    log_wnd.setLayout(ttk.TTkHBoxLayout())
    log_viever = ttk.TTkLogViewer( parent=log_wnd, follow=True )
    #login__layout.addWidget(log_viever)

    # Build "Login"
    user_frame = ttk.TTkFrame(border=True, title="Authentication", visible=True)
    user_frame.setLayout(user_frame_layout := ttk.TTkVBoxLayout())

    usr_line = ttk.TTkFrame(border=False, title="User input", visible=True)
    usr_layout = ttk.TTkHBoxLayout()
    usr_line.setLayout(usr_layout)
    usr_line.addWidget(ttk.TTkSpacer())
    usr_line.addWidget(r1 := ttk.TTkRadioButton(text="User", radiogroup="log_names", maxWidth = 12, checked=True))
    #usr_line.addWidget(ttk.TTkLabel(text="User", size=(10,1), maxWidth = 20))
    #usr_line.addWidget(ttk.TTkLineEdit(text="0xFF 0xFF 0xFF 0xFF 0xFF 0xFF", inputType=ttk.TTkK.Input_Password))
    usr_line.addWidget(pass1 := ttk.TTkLineEdit(text="0xFF 0xFF 0xFF 0xFF 0xFF 0xFF", size=(35,1), minWidth = 35, maxWidth = 35))
    usr_line.addWidget(ttk.TTkLabel(text=" "))
    usr_line.addWidget(ttk.TTkCheckbox(checked=False, maxWidth = 3))
    usr_line.addWidget(ttk.TTkCheckbox(checked=False, maxWidth = 3))
    usr_line.addWidget(ttk.TTkSpacer())

    adm_line = ttk.TTkFrame(border=False, title="Admin input", visible=True)
    adm_layout = ttk.TTkHBoxLayout()
    adm_line.setLayout(adm_layout)
    adm_line.addWidget(ttk.TTkSpacer())
    adm_line.addWidget(r2 := ttk.TTkRadioButton(text="Admin", radiogroup="log_names", maxWidth = 12))
    #adm_line.addWidget(ttk.TTkLabel(text="Admin", size=(10,1), maxWidth = 20))
    #adm_line.addWidget(ttk.TTkLineEdit(text="0xFF 0xFF 0xFF 0xFF 0xFF 0xFF", inputType=ttk.TTkK.Input_Password))
    adm_line.addWidget(pass2 := ttk.TTkLineEdit(text="0xFF 0xFF 0xFF 0xFF 0xFF 0xFF", size=(35,1), minWidth = 35, maxWidth = 35))
    adm_line.addWidget(ttk.TTkLabel(text=" "))
    adm_line.addWidget(ttk.TTkCheckbox(checked=False, maxWidth = 3))
    adm_line.addWidget(ttk.TTkCheckbox(checked=False, maxWidth = 3))
    adm_line.addWidget(ttk.TTkSpacer())

    dev_line = ttk.TTkFrame(border=False, title="Developer input", visible=True)
    dev_layout = ttk.TTkHBoxLayout()
    dev_line.setLayout(dev_layout)
    dev_line.addWidget(ttk.TTkSpacer())
    dev_line.addWidget(r3 := ttk.TTkRadioButton(text="Developer", radiogroup="log_names", maxWidth = 12))
    #dev_line.addWidget(ttk.TTkLabel(text="Developer", size=(10,1), maxWidth = 20))
    #dev_line.addWidget(ttk.TTkLineEdit(text="0xFF 0xFF 0xFF 0xFF 0xFF 0xFF", inputType=ttk.TTkK.Input_Password))
    dev_line.addWidget(pass3 := ttk.TTkLineEdit(text="", size=(35,1), minWidth = 35, maxWidth = 35))
    dev_line.addWidget(ttk.TTkLabel(text=" "))
    dev_line.addWidget(ttk.TTkCheckbox(checked=False, maxWidth = 3))
    dev_line.addWidget(ttk.TTkCheckbox(checked=False, maxWidth = 3))
    dev_line.addWidget(ttk.TTkSpacer())

    user_frame.layout().addWidget(ttk.TTkSpacer())
    user_frame.layout().addWidget(usr_line)
    user_frame.layout().addWidget(ttk.TTkLabel(text="", maxHeight = 1))
    user_frame.layout().addWidget(adm_line)
    user_frame.layout().addWidget(ttk.TTkLabel(text="", maxHeight = 1))    
    user_frame.layout().addWidget(dev_line)
    user_frame.layout().addWidget(ttk.TTkSpacer())


   # Start "Connections"

    mb_port_line = ttk.TTkFrame(border=False, title="Serial Port", visible=True)
    mb_port_line.setLayout(ttk.TTkHBoxLayout())
    mb_port_line.layout().addWidget(ttk.TTkSpacer())
    mb_port_line.layout().addWidget(ttk.TTkLabel(text="Port", maxWidth = 30))
    g_mb_port_name= ttk.TTkLineEdit(text="Type port name here..")
    mb_port_line.layout().addWidget(g_mb_port_name)
    g_mb_open_btn = ttk.TTkButton(border=True, text="Open", minHeight=3, maxHeight = 5 )
    g_mb_open_btn.clicked.connect(on_mb_open_btn)
    mb_port_line.layout().addWidget(g_mb_open_btn)
    mb_port_line.addWidget(ttk.TTkSpacer())

    mb_scan_line = ttk.TTkFrame(border=False, title="Found Ports", visible=True)
    mb_scan_line.setLayout(ttk.TTkHBoxLayout())
    mb_scan_line.layout().addWidget(ttk.TTkSpacer())
    mb_scan_line.layout().addWidget(ttk.TTkLabel(text="System", maxWidth = 30))
    raw_port_names = serial_ports()
    mb_port_names = ttk.TTkList( items=raw_port_names, border=True )
    mb_port_names.textClicked.connect(lambda s: g_mb_port_name.setText(s))

    if 1 == len(raw_port_names):
        g_mb_port_name.setText(raw_port_names[0])

    mb_scan_line.layout().addWidget( mb_port_names )
    mb_scan_line.layout().addWidget(ttk.TTkButton(border=True, text="ReScan..", maxHeight = 5 ))
    mb_scan_line.addWidget(ttk.TTkSpacer())

    mb_speed_line = ttk.TTkFrame(border=False, title="Speed", visible=True)
    mb_speed_line.setLayout(ttk.TTkHBoxLayout())
    mb_speed_line.layout().addWidget(ttk.TTkSpacer())
    mb_speed_line.layout().addWidget(ttk.TTkLabel(text="Speed", maxWidth = 30))    
    mb_speed_line.layout().addWidget(ttk.TTkComboBox(text="Speed", list=['9600n1', '115200n1'], index=0))
    mb_speed_line.layout().addWidget(ttk.TTkButton(border=True, text="Auto", maxHeight = 5 ))
    mb_speed_line.addWidget(ttk.TTkSpacer())

    mb_adr_line = ttk.TTkFrame(border=False, title="Address", visible=True)
    mb_adr_line.setLayout(ttk.TTkHBoxLayout())
    mb_adr_line.layout().addWidget(ttk.TTkSpacer())
    mb_adr_line.layout().addWidget(ttk.TTkLabel(text="Address", maxWidth = 30))   
    g_mb_adr_ledit = ttk.TTkComboBox(text="Modbus address", list=["20", "21", "22", "23", "24"]) 
    g_mb_adr_ledit.setEditable(True)    
    g_mb_adr_ledit.setCurrentText("21")
    # g_mb_adr_ledit.setCurrentIndex(0)
    mb_adr_line.layout().addWidget(g_mb_adr_ledit)
    g_mb_detect_btn = ttk.TTkButton(border=True, text="Detect..", maxHeight = 5 )
    g_mb_detect_btn.clicked.connect(on_mb_detect_btn)  
    mb_adr_line.layout().addWidget(g_mb_detect_btn)
    mb_adr_line.addWidget(ttk.TTkSpacer())

    mb_frame = ttk.TTkFrame(border=True, visible=False)
    opto_frame = ttk.TTkFrame(border=True, visible=False)

    mb_frame.setLayout(ttk.TTkGridLayout())
    mb_frame.layout().addWidget(mb_port_line, 1, 1)
    mb_frame.layout().addWidget(ttk.TTkLabel(text="", maxHeight = 1), 2, 1)
    mb_frame.layout().addWidget(mb_scan_line, 3, 1)    
    mb_frame.layout().addWidget(mb_speed_line, 4, 1) 
    mb_frame.layout().addWidget(mb_adr_line, 5, 1)     


    con_tab = ttk.TTkTabWidget(border=False, visible=True)
    con_tab.addTab(mb_frame, " ModBus ")
    con_tab.addTab(opto_frame, " OptoPort ")    

    conn_frame = ttk.TTkFrame(border=True, title="Connections", visible=True)
    conn_frame.setLayout(ttk.TTkVBoxLayout())
    conn_frame.layout().addWidget(con_tab)

    login_frame_layout = ttk.TTkVBoxLayout()
    login_frame_layout.addWidget(user_frame)
    login_frame_layout.addWidget(conn_frame)
    login_frame.setLayout(login_frame_layout)



def rh(dev, Id: ReqId):
    return lambda dev: dev.rd_str(Id)



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', help='Full Screen (default)', action='store_true')
    parser.add_argument('-w', help='Windowed',    action='store_true')
    parser.add_argument('-v', '--verbose', dest='verbose', action="store_true", default=False,
                    help='Enable debug messages.')    
    parser.add_argument('-c', '--config', dest='cfg_file_name', action="store", default=False,
                    help='Single config file for this app instance.')    
    args = parser.parse_known_args()
    # windowed = args.w
    # windowed = False

    root = ttk.TTk(title="Fossa - MILUR HMI")

    # if not args.w:
    if False:
        root.setLayout(ttk.TTkGridLayout())
        MainWnd = root
        border = False  
    else:
        MainWnd = ttk.TTkWindow(parent=root,pos=(1,1), size=(120,40), title="Fossa - MILUR HMI", border=True, layout=ttk.TTkGridLayout())
        border = True



    build_main_screen(MainWnd)
    
    root.mainloop()


if __name__ == "__main__":
    main()    