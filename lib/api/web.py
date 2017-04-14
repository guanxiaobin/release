#!/usr/bin/env python
#coding=utf-8

"""define a numbers of request handler."""
import tornado.web
import tornado.escape
import MySQLdb
import MySQLdb.cursors
import binascii
import uuid
import json
from tornado import gen
import tornado_mysql
import sys
import utils
import hashlib
from tornado.escape import utf8 as _u
from tornado.escape import to_unicode as _d
import re
reload(sys)
sys.setdefaultencoding('UTF8')

class RequestHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def prepare(self):
        self.logger = self.settings['logger']
        self.parse_jason_args()
        yield self.auth_request()
        
    def parse_jason_args(self):
        content_type = self.request.headers.get("Content-Type", "")
        if content_type.startswith("application/json"):
            try:
                arguments = json.loads(tornado.escape.native_str(self.request.body))
                for name, value in arguments.iteritems():
                    name = _u(name)
                    if isinstance(value, unicode):
                        value = _u(value)
                    elif isinstance(value, int):
                        value = str(value)
                    else:
                        value = ''

                    self.request.arguments.setdefault(name, []).append(value)
            except:
                pass
            
    @gen.coroutine
    def auth_request(self):               
        ip = self.request.headers.get("X-Forwarded-For",'')
        if ip in self.settings['support_ip']:
            pass
        else:
            self.write({"code":1, "msg":'你的出口ip不合法请及时和管理员联系'})
            self.finish()
            
        
    @gen.coroutine            
    def fetch_all_row(self,sql):
        msg = self.sql_keyword_in(sql)
        if msg == 0:
            self.write({"code":2, "msg":'你的sql语句不合法请检查'})
            self.finish()
        else:
            cur = yield self.connect_mysql()
            try:
                yield cur.execute(sql)
                row = cur.fetchall()
            except tornado_mysql.Error, e:
                self.logger.error("MySQL Error {error_code}: {error_msg} sql:{sql}".format(
                                sql=sql, error_code=e.args[0], error_msg=e.args[1]))
                self.write({"code":7, "message":"执行sql出现异常"})
    
            if row:
                raise gen.Return(row)
            
        
    @gen.coroutine
    def fetch_one_row(self, sql):
        cur = yield self.connect_mysql()
        try:
            yield cur.execute(sql)
            row = cur.fetchone()
        except tornado_mysql.Error, e:
            self.logger.error("MySQL Error {error_code}: {error_msg} sql:{sql}".format(
                            sql=sql, error_code=e.args[0], error_msg=e.args[1]))
            self.write({"code":7, "message":"执行sql出现异常"})

        if row:
            raise gen.Return({key:val if isinstance(val,long) else str(val) for key,val in row.iteritems()})
          
    @gen.coroutine
    def connect_mysql(self):
        try:
            conn = yield tornado_mysql.connect(host=self.mysql_host, port=self.mysql_port, user=self.mysql_user,
             passwd=self.mysql_pass, db=self.mysql_db,cursorclass=tornado_mysql.cursors.DictCursor,autocommit=True,charset="utf8")
        except tornado_mysql.Error, e:
            self.write({"code":7, "message":"更新数据库出现异常"})

        cur = conn.cursor()
        raise gen.Return(cur)
    
    def sql_keyword_in(self,sql):
        if "insert" in sql:
            pass
        elif "select" in sql:
            pass
        elif "update" in sql:
            pass
        elif "delete" in sql:
            pass
        elif "alter" in sql:
            pass
        else:
            return 0
    
class XsrfHandler(RequestHandler):

    def get(self): 
        self.xsrf_token