import glob
import re
import yaml #pip install pyyaml
from pathlib import Path
from constants import *


from threading import Lock, Thread
import logging
import os
from collections import defaultdict
from collections import namedtuple
from typing import List, Dict

from common import MySingletone



class MyConfig(metaclass=MySingletone):

    def __init__(self, CfgFile) -> None:
        

        self.host = "localhost"
        self.port = 1883
        self.pasw = ""
        self.user = ""

        self.pull_period_ms = 1000
        self.status_period_sec = 0
        self.changes_only = False

        self.NoNameCnt=0

        self.blocks_cfg = defaultdict(dict)

        self.blocks_cfg["common_path"] = DEFAULT_COMMON_PATH_TOPIC
        self.blocks_cfg["repetition_time_sec"] = DEFAULT_REPETITION_TIME
        self.blocks_cfg["reset_to_def_topic"] = ""
     
        logging.debug("Load of configuration" )
        
        if CfgFile:
            __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
            cfg_files = [ Path(os.path.join(__location__, CfgFile)) ]
        else:
            golden_p = Path(__file__).with_name(CONFIG_FILE)
            system_p = Path( SYSTEM_PATH + COMMON_PATH )/CONFIG_FILE
            #user_p = Path.home()/COMMON_PATH/CONFIG_FILE

            cfg_files_p = []
            try:
                cfg_files_p = [f for f in (Path.home()/COMMON_PATH).iterdir() if f.match("*config.yaml")]
            except FileNotFoundError as e:
                logging.warning( "There is no file " + e.filename + " : " + ': Message: ' + format(e) ) 
            except Exception as e:
                logging.error( "There is some problem with " + COMMON_PATH + " - it will be skipped: " + ': Message: ' + format(e) ) 

            #TODO: The same with system files

            #cfg_files = [golden_p, system_p] + cfg_files_p # TODO: golden file should be without config for hardware
            cfg_files = [system_p] + cfg_files_p

        for cfg_file in cfg_files:
            # todo: wrong file name processing
            try:
                with cfg_file.open("r") as user_f:
                    logging.debug('config file processing: ' + str(user_f.name))
                    try:
                        u_CfgData = yaml.safe_load(user_f)
                        self.extract_config(u_CfgData)
                    except Exception as e:
                        logging.error("YAML file " + user_f.name + " is incorrect and will be skipped: " + ': Message: ' + format(e) )
                        pass     
            except Exception as e:
                logging.error("Can't open file" + str(cfg_file) + " - it will be skipped: " + ': Message: ' + format(e) )
                pass     


    def extract_config(self, CfgData: list):
       
        self.extract_connection(CfgData)
        self.extract_misc_conf(CfgData)        


    def extract_misc_conf(self, CfgData: list):

        MiscCfg = CfgData.get("cfg", {})

        if MiscCfg is not None:
            self.pull_period_ms = MiscCfg.get("pull_period_ms", self.pull_period_ms)
            self.pull_period_ms = MiscCfg.get("pool_period_ms", self.pull_period_ms)
            self.changes_only = MiscCfg.get("changes_only", self.changes_only) 
            self.status_period_sec = MiscCfg.get("status_period_sec", self.status_period_sec) 
            

    def extract_connection(self, CfgData: list):

        Broker = CfgData.get("broker", {})

        if Broker is not None:
            self.host = Broker.get("host", self.host)
            self.port = Broker.get("port", self.port)   
            self.user = Broker.get("user", self.user)
            self.pasw = Broker.get("password", self.pasw)
        


if __name__ == "__main__":
        Cfg = MyConfig("config.yaml")