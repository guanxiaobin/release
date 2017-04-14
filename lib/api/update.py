#coding=utf-8
import utils
import hashlib
import time
import sys
import api.web
import re
import tornado_mysql
from tornado import gen
from tornado import iostream
import socket
from itertools import izip
from thread import start_new_thread
reload(sys)
sys.setdefaultencoding('UTF8')


class RequestHandler(api.web.RequestHandler):

    def initialize(self):
        cf = utils.config()
        self.mysql_host = cf.get("mysql", "host")
        self.mysql_port = cf.getint("mysql", "port")
        self.mysql_user = cf.get("mysql", "user")
        self.mysql_pass = cf.get("mysql", "pass")
        self.mysql_db = cf.get("mysql", "db")
                 
            
class UpdateHandler(RequestHandler):
    @gen.coroutine
    def post(self):
        sql = self.request.body
        if not sql:
            self.write({"code":9, "message":'参数为空'})
        row = yield self.fetch_all_row(sql)
        self.write({"code":0, "message":""})

        
class QueryHandler(RequestHandler):
    @gen.coroutine
    def post(self):
        sql = self.request.body
        if not sql:
            self.write({"code":9, "message":'参数为空'})
        else:
            row = yield self.fetch_all_row(sql)
            if row == None:
                self.write({"code":8, "message":""})
            else:
                self.write({"code":0, "message":""})
            
 

    
