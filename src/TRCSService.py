# -*- coding: utf-8 -*-

import win32serviceutil
import win32service
import win32event
import winerror
import servicemanager
import Mylex
import Myyacc
from MyInterpreter import MyInterpreter
from socket import *
import struct
import ply.lex as lex
import ply.yacc as yacc
import urllib2
import os
import sys
import base64

# ---------------------------------------------
# 数据包格式：
# 头部+正文
# 头部：消息号（16位短整型）+正文长度（64位长整型）
# 消息号：
# 1：执行正文，正文为MY源码
# 2：执行正文，正文为MY字节码
# 3：以正文为http地址，下载MY源码执行
# 4：以正文为http地址，下载MY字节码执行
# ---------------------------------------------

class TRCSService(win32serviceutil.ServiceFramework):
    '''TRCS: The Remote Control Software'''
    DEBUG = True
    _svc_name_ = "TRCSService"  #服务名
    _svc_display_name_ = "TRCSService"  #服务在windows系统中显示的名称
    _svc_description_ = "The Remote Control Software Service"  #服务的描述
    # 头部长度，2个字节+8个字节
    HeaderSize = 10
    EXEC_MY = 1
    EXEC_MYC = 2
    HTTP_EXEC_MY = 3
    HTTP_EXEC_MYC = 4
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.run = True
        self.listen_sock = None
        self.client = None
        self.databuf = None
        if self.DEBUG:
            self.init_debug()
        lexer = lex.lex(module=Mylex)
        self.parser = yacc.yacc(module=Myyacc)
        self.interpreter = MyInterpreter()
        
    def init_debug(self):
        self.logger = open('log.txt', 'w')
        
    def log(self, msg):
        if self.DEBUG:
            self.logger.write(msg+os.linesep)
            self.logger.flush()
        
    def deal_connection(self):
        if self.listen_sock == None:
            self.listen_sock = socket(AF_INET, SOCK_STREAM)
            # 保活两分钟
            self.listen_sock.setsockopt(SOL_SOCKET, SO_KEEPALIVE, 120)
            # 超时5分钟，不设置超时，服务将停止不了
            # self.listen_sock.settimeout(5*60)
            self.listen_sock.bind((gethostname(), 8140))
            self.listen_sock.listen(1)
        self.client, addr = self.listen_sock.accept()
        self.log('new connection: ' + str(addr))
        self.databuf = ''

    def exec_my(self, body):
        orders = self.parser.parse(body)
        self.interpreter.execute(orders)
        
    def exec_myc(self, body):
        orders = body.split(os.linesep)
        self.interpreter.execute(orders)
        
    def http_exec_my(self, body):
        f = urllib2.urlopen(body)
        self.exec_my(f.read())
        
    def http_exec_myc(self, body):
        f = urllib2.urlopen(body)
        orders = f.read().split(os.linesep)
        self.interpreter.execute(orders)
        
    def deal_msg(self, msg_type, body):
        try:
            if msg_type == self.EXEC_MY:
                self.exec_my(body)
            elif msg_type == self.EXEC_MYC:
                self.exec_myc(body)
            elif msg_type == self.HTTP_EXEC_MY:
                self.http_exec_my(body)
            elif msg_type == self.HTTP_EXEC_MYC:
                self.http_exec_myc(body)
            else:
                raise Exception
        except Exception:
            self.client.sendall('Failure')
        else:
            self.client.sendall('Success')
            
    def SvcDoRun(self):
        while self.run:
            try:
                self.deal_connection()
                while True:
                    data = self.client.recv(4096)
                    if not data:
                        self.client.close()
                        break
                    self.databuf += data
                    while True:
                        if self.HeaderSize > len(self.databuf):
                            # 还没收到完整的数据包
                            break
                        header = struct.unpack('!hq', self.databuf[:self.HeaderSize])
                        msg_type, bodysize = header
                        if len(self.databuf) < self.HeaderSize + bodysize:
                            # 还没收到完整的数据包
                            break
                        self.log('new message: ' + str(header))
                        body = self.databuf[self.HeaderSize:self.HeaderSize + bodysize]
                        body = base64.decodestring(body)
                        self.log(body)
                        self.deal_msg(msg_type, body)
                        self.databuf = self.databuf[self.HeaderSize + bodysize:]
            except error, e:
                # socket出错
                self.log(str(e))
                if self.client:
                    self.client.close()
                continue
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
        
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        if self.listen_sock:
            self.listen_sock.close()
        if self.client:
            self.client.close()
        self.run = False
        
if __name__=='__main__':
    if len(sys.argv) == 1:
        try:
            evtsrc_dll = os.path.abspath(servicemanager.__file__)
            servicemanager.PrepareToHostSingle(TRCSService)
            servicemanager.Initialize('TRCSService', evtsrc_dll)
            servicemanager.StartServiceCtrlDispatcher()
        except win32service.error, details:
            if details[0] == winerror.ERROR_FAILED_SERVICE_CONTROLLER_CONNECT:
                win32serviceutil.usage()
    else:
        win32serviceutil.HandleCommandLine(TRCSService)    
