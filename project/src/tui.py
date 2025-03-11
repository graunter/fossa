import argparse
import TermTk as ttk        # pip install TermTk
from collections import defaultdict
import sys
import glob
import serial               #pip install pyserial

view_frames = defaultdict(list)


g_current_frame = None
g_mb_open_btn: ttk.TTkButton
g_ser: serial.Serial


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

def modbusCrc(msg:str) -> int:
    crc = 0xFFFF
    for n in range(len(msg)):
        crc ^= msg[n]
        for i in range(8):
            if crc & 1:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc

def on_mb_open_btn():
    global g_mb_open_btn
    global g_ser

    try:
        if g_mb_open_btn.text() == 'Open':
            g_ser = serial.Serial(
                port='COM11'
                , baudrate=9600
                , bytesize=8
                , parity='N'
                , stopbits=1
                , timeout=0.1
                , rtscts=False
                , dsrdtr=False
            )
        else:
            g_ser.close()
            g_mb_open_btn.setChecked(False)
            g_mb_open_btn.setText('Open')
            return
    except serial.SerialException as e:
        err_box = ttk.TTkMessageBox(
                title="Serial port error",
                text=format(e)
            )
        ttk.TTkHelper.overlay(None, err_box, 50, 20, True)
        return
        

    test_adr = 0x17
    open_srv_code = 0x08
    access_lvl_user = 0
    access_adm_user = 1
    access_dev_user = 2

    access_pwd_user = [255]*6

    send_dat = sum([[test_adr], [open_srv_code], [access_lvl_user], list(access_pwd_user)], [])

    crc = modbusCrc(send_dat)
    ba = crc.to_bytes(2, byteorder='little')
    send_packet = sum([send_dat, [ba[0]], [ba[1]]], [])
    g_ser.write(send_packet)
    
    received = g_ser.read(128)
    if received != b'':
        bg_color = ttk.TTkColor.BG_GREEN
    else:
        bg_color = ttk.TTkColor.BG_RED
        wrn_box = ttk.TTkMessageBox(
                title="Warning",
                text="Port is opened but no device was found on this address!"
            )
        ttk.TTkHelper.overlay(None, wrn_box, 50, 20, True)

    text=ttk.TTkString(' Close ', bg_color)
    g_mb_open_btn.setText(text)



def BuildMainScreen(root=None):
    global g_current_frame
    global g_mb_open_btn

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
    config_frame = ttk.TTkFrame(border=True, title="Config", visible=False)
    service_frame = ttk.TTkFrame(border=True, title="Service", visible=False)
    view_frame = ttk.TTkFrame(border=True, title="View", visible=False)


    top_btn_frame.addWidget(create_btn_for_frame(True, login_frame))
    top_btn_frame.addWidget(create_btn_for_frame(False, config_frame))
    top_btn_frame.addWidget(create_btn_for_frame(False, service_frame))    
    top_btn_frame.addWidget(create_btn_for_frame(False, view_frame))


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

    mframe_layout.addWidget(login_frame)
    mframe_layout.addWidget(config_frame)
    mframe_layout.addWidget(service_frame)
    mframe_layout.addWidget(view_frame)
    
    log_wnd = ttk.TTkWindow(parent=main_frame, pos = (15,4), size=(87,20), title="Log Window", flags=0, visible=False)
    log_wnd.setLayout(ttk.TTkHBoxLayout())
    log_viever = ttk.TTkLogViewer( parent=log_wnd, follow=True )
    #login__layout.addWidget(log_viever)

    # Build "Login"
    user_frame = ttk.TTkFrame(border=True, title="Users", visible=True)
    user_frame.setLayout(user_frame_layout := ttk.TTkVBoxLayout())
    usr_line = ttk.TTkFrame(border=False, title="User input", visible=True)
    usr_layout = ttk.TTkHBoxLayout()
    usr_line.setLayout(usr_layout)
    usr_line.addWidget(ttk.TTkSpacer())
    usr_line.addWidget(r1 := ttk.TTkRadioButton(text="User", radiogroup="log_names", maxWidth = 3, checked=True))
    usr_line.addWidget(ttk.TTkLabel(text="User", size=(10,1), maxWidth = 30))
    #usr_line.addWidget(ttk.TTkLineEdit(text="0xFF 0xFF 0xFF 0xFF 0xFF 0xFF", inputType=ttk.TTkK.Input_Password))
    usr_line.addWidget(ttk.TTkLineEdit(text="0xFF 0xFF 0xFF 0xFF 0xFF 0xFF"))
    usr_line.addWidget(ttk.TTkCheckbox(checked=False, maxWidth = 3))
    usr_line.addWidget(ttk.TTkCheckbox(checked=False, maxWidth = 3))
    usr_line.addWidget(ttk.TTkSpacer())

    adm_line = ttk.TTkFrame(border=False, title="Admin input", visible=True)
    adm_layout = ttk.TTkHBoxLayout()
    adm_line.setLayout(adm_layout)
    adm_line.addWidget(ttk.TTkSpacer())
    adm_line.addWidget(r1 := ttk.TTkRadioButton(text="Admin", radiogroup="log_names", maxWidth = 3))
    adm_line.addWidget(ttk.TTkLabel(text="Admin", size=(10,1), maxWidth = 30))
    #adm_line.addWidget(ttk.TTkLineEdit(text="0xFF 0xFF 0xFF 0xFF 0xFF 0xFF", inputType=ttk.TTkK.Input_Password))
    adm_line.addWidget(ttk.TTkLineEdit(text=""))
    adm_line.addWidget(ttk.TTkCheckbox(checked=False, maxWidth = 3))
    adm_line.addWidget(ttk.TTkCheckbox(checked=False, maxWidth = 3))
    adm_line.addWidget(ttk.TTkSpacer())

    dev_line = ttk.TTkFrame(border=False, title="Developer input", visible=True)
    dev_layout = ttk.TTkHBoxLayout()
    dev_line.setLayout(dev_layout)
    dev_line.addWidget(ttk.TTkSpacer())
    dev_line.addWidget(r1 := ttk.TTkRadioButton(text="Developer", radiogroup="log_names", maxWidth = 3))
    dev_line.addWidget(ttk.TTkLabel(text="Developer", size=(10,1), maxWidth = 30))
    #adm_line.addWidget(ttk.TTkLineEdit(text="0xFF 0xFF 0xFF 0xFF 0xFF 0xFF", inputType=ttk.TTkK.Input_Password))
    dev_line.addWidget(ttk.TTkLineEdit(text=""))
    dev_line.addWidget(ttk.TTkCheckbox(checked=False, maxWidth = 3))
    dev_line.addWidget(ttk.TTkCheckbox(checked=False, maxWidth = 3))
    dev_line.addWidget(ttk.TTkSpacer())

    user_frame_layout.addWidget(ttk.TTkSpacer())
    user_frame_layout.addWidget(usr_line)
    user_frame_layout.addWidget(adm_line)
    user_frame_layout.addWidget(dev_line)
    user_frame_layout.addWidget(ttk.TTkSpacer())


   # Start "Connections"

    mb_port_line = ttk.TTkFrame(border=False, title="Serial Port", visible=True)
    mb_port_line.setLayout(ttk.TTkHBoxLayout())
    mb_port_line.layout().addWidget(ttk.TTkSpacer())
    mb_port_line.layout().addWidget(ttk.TTkLabel(text="Port", maxWidth = 30))
    mb_port_line.layout().addWidget(ttk.TTkLineEdit(text="Type port name here.."))
    g_mb_open_btn = ttk.TTkButton(border=True, text="Open", height=5, minHeight=5, maxHeight = 5 )
    g_mb_open_btn.clicked.connect(on_mb_open_btn)
    mb_port_line.layout().addWidget(g_mb_open_btn)
    mb_port_line.addWidget(ttk.TTkSpacer())

    mb_scan_line = ttk.TTkFrame(border=False, title="Found Ports", visible=True)
    mb_scan_line.setLayout(ttk.TTkHBoxLayout())
    mb_scan_line.layout().addWidget(ttk.TTkSpacer())
    mb_scan_line.layout().addWidget(ttk.TTkLabel(text="Ports", maxWidth = 30))
    mb_scan_line.layout().addWidget(ttk.TTkList( items=serial_ports(), border=True ) )
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
    mb_adr_line.layout().addWidget(ttk.TTkLineEdit(text="0x01"))
    mb_adr_line.layout().addWidget(ttk.TTkButton(border=True, text="Detect..", maxHeight = 5 ))
    mb_adr_line.addWidget(ttk.TTkSpacer())

    mb_frame = ttk.TTkFrame(border=True, visible=False)
    opto_frame = ttk.TTkFrame(border=True, visible=False)

    mb_frame.setLayout(ttk.TTkVBoxLayout())
    mb_frame.layout().addWidget(mb_port_line)
    mb_frame.layout().addWidget(mb_scan_line)    
    mb_frame.layout().addWidget(mb_speed_line) 
    mb_frame.layout().addWidget(mb_adr_line)     


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

    


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', help='Full Screen (default)', action='store_true')
    parser.add_argument('-w', help='Windowed',    action='store_true')
    args = parser.parse_args()
    windowed = args.w
    windowed = False

    root = ttk.TTk(title="Fossa - MILUR HMI")

    if windowed:
        MainWnd = ttk.TTkWindow(parent=root,pos=(1,1), size=(120,40), title="Fossa - MILUR HMI", border=True, layout=ttk.TTkGridLayout())
        border = True
    else:
        root.setLayout(ttk.TTkGridLayout())
        MainWnd = root
        border = False

    BuildMainScreen(MainWnd)
    
    root.mainloop()


if __name__ == "__main__":
    main()    