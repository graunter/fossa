import argparse
import TermTk as ttk    # pip install TermTk
from collections import defaultdict

view_frames = defaultdict(list)


g_current_frame = None


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


def BuildMainScreen(root=None):
    global g_current_frame

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


    conn_frame = ttk.TTkFrame(border=True, title="Connections", visible=True)

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