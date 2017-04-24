# -*- coding: utf-8 -*-

import ply.yacc as yacc
from Mylex import tokens

# 定义优先级
precedence = (
    ('left', '='),
    ('left', 'AND', 'OR'),
    ('left', '>', '<', 'Eq', 'Leq', 'Req'),
    ('left', '+', '-'),
    ('left', '*', '/', '%'),
    ('right', 'UMINUS', 'NOT'),   
)

def p_chunk(p):
    'chunk : block'
    pass

# 定义空产生式
def p_empty(p):
    'empty :'
    pass

def p_block(p):
    '''block : empty
             | stat
             | block stat'''
    pass

def p_stat(p):
    '''stat : if_st
            | for_st		
            | while_st		
            | break_st		
            | continue_st	
            | return_st	
            | assign_st	
            | local_def_st	
            | func_def_st	
            | func_call
    '''	
    pass

def p_if_st(p):
    '''
    if_st : IF exp ':' block ';'
          | IF exp ':' block ELSE ':' block ';'    
    '''
    pass

def p_for_st(p):
    '''
    for_st : FOR namelist IN list ':' block ';'
           | FOR namelist IN String ':' block ';'   
           | FOR namelist IN dict ':' block ';'
           | FOR namelist IN Name ':' block ';'   
    '''
    pass

def p_while_st(p):
    '''
    while_st : WHILE exp ':' block ';'
    '''
    pass

def p_break_st(p):
    'break_st : BREAK'
    pass

def p_continue_st(p):
    'continue_st : CONTINUE'
    pass

def p_return_st(p):
    'return_st : RETURN'
    pass

def p_assign_st(p):
    '''
        assign_st : namelist '=' explist
                  | obj_domains '=' exp
    '''
    pass

def p_local_def_st(p):
    '''
    local_def_st : LOCAL namelist
                 | LOCAL namelist '=' explist     
    '''
    pass

def p_func_def_st(p):
    '''
    func_def_st : LOCAL FUNC Name '(' ')' ':' block ';'
                | LOCAL FUNC Name '(' namelist ')' ':' block ';'
                | FUNC Name '(' namelist ')' ':' block ';'
                | FUNC Name '(' ')' ':' block ';'
    '''
    pass

def p_func_call(p):
    '''
    func_call : Name '(' ')'
              | Name '(' explist ')'
    '''
    pass

def p_namelist(p):
    '''
    namelist : Name
             | namelist ',' Name
    '''
    pass

def p_explist(p):
    '''
    explist : exp
            | explist ',' exp
    '''
    pass

def p_exp(p):
    '''
    exp : NIL
        | FALSE
        | TRUE
        | Number      
        | String
        | dict
        | Name
        | obj_domains
        | func_call
        | list
        | '-' exp %prec UMINUS
        | NOT exp
        | '(' exp ')'                                        
        | exp '+' exp
        | exp '-' exp
        | exp '*' exp
        | exp '%' exp
        | exp '/' exp
        | exp '>' exp
        | exp '<' exp
        | exp Eq exp
        | exp Leq exp
        | exp Req exp
        | exp OR exp
        | exp AND exp
    '''
    pass

def p_list(p):
    '''
    list : '(' exp ',' ')'
         | '(' exp ',' explist ')'
    '''
    pass

def p_dict(p):
    '''
    dict : '{' '}'
         | '{' itemlist '}'
    '''
    pass

def p_itemlist(p):
    '''
    itemlist : item
             | itemlist ',' item
    '''
    pass

def p_item(p):
    '''
    item : exp ':' exp
    '''
    pass

def p_obj_domains(p):
    '''
    obj_domains : Name domains
    '''
    pass

def p_domains(p):
    '''
    domains : '[' exp ']'
            | domains '[' exp ']'    
    '''
    pass

def p_error(p):
    print("Syntax error!")
