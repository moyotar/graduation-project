# -*- coding: utf-8 -*-

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
import re

# ---------------------------------------
# 客户端采用命令行方式进行交互，支持7种命令：
# connect
# run
# compile
# remy
# remyc
# rhemy
# rhemyc
# ---------------------------------------

class TRCSClient():
    '''TRCS: The Remote Control Software'''
    EXEC_MY = 1
    EXEC_MYC = 2
    HTTP_EXEC_MY = 3
    HTTP_EXEC_MYC = 4
    RESPONSE_SIZE = 7
    def __init__(self):
        self.sock = None
        lexer = lex.lex(module=Mylex)
        self.parser = yacc.yacc(module=Myyacc)
        self.interpreter = MyInterpreter()
        
    def close_connect(self):
        if self.sock:
            self.sock.close()
            self.sock = None
            
    def connect(self, server_ip):
        self.close_connect()
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.settimeout(120)
        self.sock.connect((server_ip, 8140))
        self.recv_buf = ''
        
    def run(self, file_name):
        f = open(file_name, 'r')
        orders = self.parser.parse(f.read())
        f.close()        
        self.interpreter.execute(orders)
    
    def compile(self, file_name):
        f = open(file_name, 'r')
        compile_file_name = file_name.split('.')[0] + '.myc'
        orders = self.parser.parse(f.read())
        f.close()
        f = open(compile_file_name, 'w')
        for order in orders:
            f.write(order+os.linesep)
        f.close()
        
    def send_data(self, tp, body):
        crypt_body = base64.encodestring(body)
        header = struct.pack('!hq', tp, len(crypt_body))
        data = header + crypt_body
        self.sock.sendall(data)

    def get_response(self):
        while len(self.recv_buf) < self.RESPONSE_SIZE:
            data = self.sock.recv(1024)
            self.recv_buf += data
        print(self.recv_buf[:self.RESPONSE_SIZE])
        self.recv_buf = self.recv_buf[self.RESPONSE_SIZE:]
        
    def remy(self, file_name):
        '''remote_exec_my'''
        f = open(file_name)
        source_code = f.read()
        f.close()
        self.send_data(self.EXEC_MY, source_code)
        self.get_response()
        
    def remyc(self, file_name):
        '''remote_exec_myc'''
        f = open(file_name)
        byte_code = f.read()
        f.close()
        self.send_data(self.EXEC_MYC, byte_code)
        self.get_response()
    
    def rhemy(self, addr):
        '''remote_http_exec_my'''
        self.send_data(self.HTTP_EXEC_MY, addr)
        self.get_response()
        
    def rhemyc(self, addr):
        '''remote_http_exec_myc'''
        self.send_data(self.HTTP_EXEC_MYC, addr)
        self.get_response()

    def main(self):
        while True:
            input = raw_input('$: ')
            try:
                command, arg = re.split(r"[\s]+", input.strip(), 1)
                func = getattr(self, command, None)
                if func:
                    func(arg)
                else:
                    print('Illegal command!')
            except error, e:
                print(e)
                self.close_connect()
            except Exception, e:
                print(e)

if __name__ == '__main__':
    client = TRCSClient()
    client.main()
