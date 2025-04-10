#!/usr/bin/env python3

import os, re, time, json, argparse, signal
import paho.mqtt.client as mqtt # pip install paho-mqtt
from my_config import MyConfig
import logging
import json
from threading import Thread
from timeit import default_timer as timer
from milur_meter import PwrMeter
import serial   #pip install pyserial


verbose = False

def debug(msg):
    if verbose:
        print (msg + "\n")

class Fossa:

    def __init__(self, Cfg: MyConfig):
        self.pause_pins_fl = True
        self.pause_blocks_fl = True
        self.pull_pins_thrd = None
        self.pull_blocks_thrd = None
        self.cfg = Cfg


        logging.debug(f'Fossa strted')
        self.status_timer_begin = 0

    def signal_handler(self, signal, frame):
        print(' You pressed Ctrl+C!')
        client.disconnect()

    # TODO: restore of all pins state from persistent storage
    def on_start(self):
        ser = serial.Serial(port='COM11', baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=0.1, rtscts=False, dsrdtr=False)
        cnt = PwrMeter(21, ser)   
        #ver_val, ver_str = cnt.read_version()
        #logging.debug(f'Counter version: {ver_str}, row value: {ver_val}')

    def on_connect(self, client, userdata, connect_flags, reason_code, properties):
        # Подписка при подключении означает, что если было потеряно соединение
        # и произошло переподключение - то подписка будет обновлена

        if reason_code != 0:
            logging.debug(f"Failed to connect: {reason_code}. loop_forever() will retry connection")
            return

        logging.debug("Connected with result code "+str(reason_code))

        self.status_timer_begin = timer()
        #if self.cfg.blocks_cfg["repetition_time_sec"] > 0:
        self.pause_blocks_fl = False
        if not self.pull_blocks_thrd:
            self.pull_blocks_thrd = Thread(target=self.on_blocks_pull)
            self.pull_blocks_thrd.daemon = True
            self.pull_blocks_thrd.start()    


    def on_disconnect(self):
        logging.debug('Disconected from client') 
        self.pause_pins_fl = True

        for i, (key, CompLst) in enumerate(self.pins.items()):
            for OneComp in CompLst:
                OneComp.on_disconnect()


    def on_blocks_pull(self):
        #TODO: may be could be faster
        re_time = self.cfg.blocks_cfg["repetition_time_sec"] if self.cfg.blocks_cfg["repetition_time_sec"]>0 else 1
        
        while True:
            time.sleep(Cfg.pull_period_ms/1000)   
            if not self.pause_blocks_fl:
                for one_block in self.block_lst:

                    if is_upd := one_block.upd_state():
                        one_block.send_state()
                    elif False == self.cfg.changes_only:
                        one_block.send_state()

                    if self.cfg.blocks_cfg["repetition_time_sec"] > 0:
                        if ( (the_time:=timer()) -self.status_timer_begin) > re_time:
                            one_block.send_state()
                            self.status_timer_begin = the_time


    def on_message(self, client: mqtt.Client, userdata, msg: mqtt.MQTTMessage):
        pass
        # for item in self.pins[msg.topic]:
        #     item.on_message( client, userdata, msg )


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Send MQTT payload received from a topic to any.', 
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    
    parser.add_argument('-a', '--adr-broker', dest='host', action="store",
                    help='Specify the MQTT host to connect to.')
    parser.add_argument('-p', '--port-broker', dest='port', action="store",
                    help='Specify the MQTT host to connect to.')    
    parser.add_argument('-u', '--user-broker', dest='user', action="store",
                    help='User name for Broker connection')  
    parser.add_argument('-w', '--pass-broker', dest='pasw', action="store",
                    help='Password for Broker connection.')  
    parser.add_argument('-v', '--verbose', dest='verbose', action="store_true", default=False,
                    help='Enable debug messages.')
    parser.add_argument('-c', '--config', dest='cfg_file_name', action="store", default=False,
                    help='Single config file for this app instance.')

    args = parser.parse_args()
    
    loglevel = logging.INFO 
    if args.verbose: 
        loglevel = logging.DEBUG

    logging.basicConfig(level=loglevel)
    
    Cfg = MyConfig(args.cfg_file_name)
    
    fossa = Fossa(Cfg)
    if args.verbose: 
        fossa.verbose = True

    signal.signal(signal.SIGINT, fossa.signal_handler)
    signal.signal(signal.SIGTERM, fossa.signal_handler)

    debug("Fossa started!")

    fossa.on_start()

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = fossa.on_connect
    client.on_message = fossa.on_message
    client.on_disconnect = lambda client, userdata, rc: fossa.on_disconnect() 
    client.on_socket_close = lambda client, userdata, rc: fossa.on_disconnect() 

    # For test purposes
    #if args.verbose: 
        # client.enable_logger()
    
    Host = args.host if args.host is not None else Cfg.host
    Port = args.port if args.port is not None else Cfg.port
    User = args.user if args.user is not None else Cfg.user
    Pasw = args.pasw if args.pasw is not None else Cfg.pasw

    logging.debug("Try connection to " + str(Host) + " with port " + str(Port) + ': '+User+'+'+Pasw)

    client.username_pw_set(User, Pasw)
 
    ConnectedFl = False
    while not ConnectedFl:
        try:
            client.connect(Host, Port)
            ConnectedFl = True
        except:
            logging.debug(f"Can't connect - wait for some seconds.." )
            time.sleep(5)
        
    client.loop_forever()

