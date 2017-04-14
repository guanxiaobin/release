#!/usr/bin/env python
#coding=utf-8
#
# Copyright (c) 2014, Bottle development team
# All rights reserved.
#
# Bottle is distributed under the terms of the (new) BSD License.
# The full license can be found in 'LICENSE.txt'.

"""start a server using tornado.httpserver module."""

import os
import sys
root_path = os.path.split(os.path.realpath(__file__))[0]
sys.path.insert(0, os.path.join(root_path, 'lib'))
reload(sys)
sys.setdefaultencoding('UTF-8')

import tornado.ioloop
import tornado.httpserver
import tornado.web
import tornado.autoreload
import api.web
import api.update
from api.utils import log
#from api.utils import make_cookie_secret
from api.utils import config
from thread import start_new_thread
import MySQLdb
import MySQLdb.cursors
import socket
import time
import argparse
if not sys.platform == "win32": import daemon

def check_agent():
    while True:
        db = connect_mysql()
        with db:
            try:
                c = db.cursor()
                sql = "select id, ip, port from server"
                c.execute(sql)
                rows = c.fetchall()
            except MySQLdb.Error, e:
                logger.error("MySQL Error {error_code}: {error_msg}".format(error_code=e.args[0], error_msg=e.args[1]))

            if rows:
                for row in rows:
                    id = row['id']
                    ip = row['ip']
                    agent_port = row['port']
                    admin_port = int(agent_port) + 1
                    agent_state = get_state(ip, agent_port)
                    admin_state = get_state(ip,admin_port)

                    set_mysql_port_state(id, agent_state,"agent")
                    set_mysql_port_state(id, admin_state,"admin")
            else:
                logger.warning("无法获取server表信息或者server表为空")

        time.sleep(10) 

def get_state(ip, port):
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        sock.connect((ip, port))
    except socket.error,e:
        logger.error("无法连接主机{ip},端口{port}".format(ip=ip,port=port))
        state = -2
    else:    
        check_cmd = "action service_check"
        try:
            sock.sendall(check_cmd)
        except socket.error,e:
            logger.error("socket error {code} {msg}".format(code=e.args[0],msg=e.args[1]))

        recv_data = ""
        try:
            data = sock.recv(8192)
            recv_data += data
        except socket.error,e:
            logger.error("socket error {code} {msg}".format(code=e.args[0],msg=e.args[1]))                

        state = 0 if recv_data == "resp_code 200" else -2

    return state


def set_mysql_port_state(id, state,type):
    db = connect_mysql()
    with db:
        try:
            c = db.cursor()
            if type == "agent":
                sql = 'update server set state = {state} where id = "{id}" '.format(id=id, state=state)
            elif type == "admin":
                sql = 'update server set admin_state = {state} where id = "{id}" '.format(id=id, state=state)

            c.execute(sql)
        except MySQLdb.Error, e:
            logger.error("MySQL Error {error_code}: {error_msg}".format(error_code=e.args[0], error_msg=e.args[1]))            

def connect_mysql():
    cf = config()
    mysql_host = cf.get("mysql", "host")
    mysql_port = cf.getint("mysql", "port")
    mysql_user = cf.get("mysql", "user")
    mysql_pwd = cf.get("mysql", "pass")
    mysql_db = cf.get("mysql", "db")
    try:
        db = MySQLdb.connect(host=mysql_host, port=mysql_port,
                         user=mysql_user, passwd=mysql_pwd,
                         db=mysql_db,charset="utf8",cursorclass=MySQLdb.cursors.DictCursor)
        return db
    except MySQLdb.Error, e:
        logger.error("MySQL Error {error_code}: {error_msg}".format(error_code=e.args[0], error_msg=e.args[1]))   

def start_http_server():
    cf = config()
    server_port = cf.get("server", "port")
    support_ip = cf.get("domain","ip").split("|")

    settings = {
        'support_ip': support_ip,     
        'xsrf_cookies': False,
        'cookie_secret': "aaa",
        'debug' : args.d,
        'logger': log(),
    }

    application = tornado.web.Application([
        (r'/xsrf', api.web.XsrfHandler),
        (r'/release/version/update', api.update.UpdateHandler),
        (r'/release/version/query', api.update.QueryHandler),

        
    ], **settings)

    server = tornado.httpserver.HTTPServer(application)
    server.listen(server_port, address="0.0.0.0")
    tornado.ioloop.IOLoop.instance().start()

def main():
    #start_new_thread(check_agent,())
    start_http_server()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', help='Running process in the front',action='store_true')
    parser.add_argument('-d', help='Running process in the debug mode',action='store_true')
    args = parser.parse_args()
    logger = log()

    if not args.f and not args.d:
        with daemon.DaemonContext():
            main()
    else:
        main()