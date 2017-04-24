# Test Myyacc.py
import sys
sys.path.append("../src/")

import Mylex
import Myyacc
import ply.lex as lex
import ply.yacc as yacc

data = '''
# test assignments
a = .23e+4

# test if_st
if true:
  _1 = nil;

if _1:
_1 = false
else:
_2 = nil;
'''

lexer = lex.lex(module=Mylex)
parser = yacc.yacc(module=Myyacc)
parser.parse(data)
