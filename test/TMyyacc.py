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

# test func
local func foo(b,c):
     a = b * c
     return a;
;
foo(1, 3, 4)
a = foo(1, 3, 4)

func GCD(a,b):
    if a>=b:
        if a%b==0:
             return b;
        else:
             return GCD(b, a%b);
        ;
    else:
        return GCD(b,a);
;
;

# test while
a = 0
while a < 10:
a = a + 1
;

# test for
a = [2,2,2,2,4]
for key in a:
   a[key] = key
;

# test list and dict
ls = [a,[[]]]
dt = {1:2,2:[], 3:{}}

# test binop
a = 1<2*1+1 and (2+1)*1 <4
b = 1+-2*4-5%2/3
'''

lexer = lex.lex(module=Mylex)
parser = yacc.yacc(module=Myyacc)
orders = (parser.parse(data))
f = open('a.myc', 'w')
for order in orders:
    f.write(order+'\n')
