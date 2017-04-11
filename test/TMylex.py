# test Mylex module
import sys
sys.path.append("../src/")

import lex.Mylex as Mylex
import ply.lex as lex

data = '''
# test Number
112334 1.0 1. .3 .2e+4 .4e-3 2.e-2

# test Name
ksjdf a __sd b_ a_2_1__ ACKD

# test String
"ssdfdssmem" "\1\2\n\e" "s'dk\"k\rss\t"

# test Reserved
for in if else while
 func break continue return and
 or not nil true false local

# test Eq
==

# test Leq
<=

# test Req
>=

# test literal chars
-+*/%>< =,:;{}()[]
'''

lexer = lex.lex(module=Mylex)
lexer.input(data)
while True:
    tok = lexer.token()
    if not tok:
        break
    print(tok)
