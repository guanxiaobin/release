#coding=utf-8
import base64
import uuid
import sys
import os
import md5
import ConfigParser
import logging
import hashlib
import time
import random
import string
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex

reload(sys)
sys.setdefaultencoding('UTF-8')
cur_path = os.path.split(os.path.realpath(__file__))[0]


#获取数据库的配置信息
def config():
    cfg = os.path.join(cur_path, '../../data/db.conf')
    cf = ConfigParser.ConfigParser()
    cf.read(cfg)
    return cf

def log():
    # 创建一个logger  
    lg = logging.getLogger('api')  
    lg.setLevel(logging.INFO)
 
    # 创建一个handler，用于写入日志文件
    log_path = os.path.join(cur_path, '../../data/',"api.log")
    fh = logging.FileHandler(log_path)
    fh.setLevel(logging.INFO)
 
    # 定义handler的输出格式  
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')  
    fh.setFormatter(formatter)
 
    # 给logger添加handler  
    lg.addHandler(fh)
    return lg



