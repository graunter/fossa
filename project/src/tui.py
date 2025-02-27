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