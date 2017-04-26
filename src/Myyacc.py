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

# ---------------------------------------------------
# 直接在语义动作里面做代码自动生成
# 每条指令有以下两种格式：
# 1. opcode '\t' operand
# 2. opcode
# 所有opcode参见指令设计文档instructions
# 如果有operand部分，以tab字符隔开其和opcode,如指令格式1
# 归约生成时指令存放在p[0]的order字段中
# ---------------------------------------------------

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
    '''return_st : RETURN ';'
                 | RETURN explist ';'
    '''
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

def deal_exp_len2(p):
    res = {
        "orders" : []
    }
    tp = p[1]["type"]
    if tp in ['NIL', 'FALSE', 'TRUE', 'Number', 'String']:
        # 常量，指令push
        res["orders"].append("".join(["push\t", str(p[1]["value"])]))
    elif tp in ['list', 'dict', 'func_call']:
        res["orders"] = p[1]["orders"]
    elif tp == 'Name':
        # 变量, load
        res["orders"].append("".join(["load\t", str(p[1]["value"])]))
    else:
        # obj_domains
        orders_list = p[1]["orders_list"]
        name = p[1]["Name"]
        res_orders = res['orders']
        # 先把要做元素访问的对象load进操作栈
        res_orders.append("".join(["load\t", str(name)]))
        for exp_orders in orders_list:
            # 依次加载每个exp的值进栈，然后执行index指令
            res_orders += exp_orders
            res_orders.append('index')
    p[0] = res
            
def deal_exp_len3(p):
    # 处理负号和not
    p[0] = {'orders' : p[1]['orders']}
    if p[1] == '-':
        p[0]['orders'].append('unm')
    else:
        p[0]['orders'].append('not')
        
def deal_exp_len4(p):
    if p[1] == '(':
        p[0] = p[2]
        return
    p[0] = {'orders' : []}
    if p[2] in ['>=', '>']:
        # 对调位置，转换成小于或则和小于等于
        p[0]['orders'] += p[1]['orders']
        p[0]['orders'] += p[3]['orders']
        if p[2] == '>=':
            p[0]['orders'].append('le')
        else:
            p[0]['orders'].append('lt')
        return
    p[0]['orders'] += p[3]['orders']
    p[0]['orders'] += p[1]['orders']
    dt = {
        '+' : 'add',
        '-' : 'sub',
        '*' : 'times',
        '/' : 'div',
        '%' : 'mod',
        '<' : 'lt',
        '==': 'lq',             # Eq
        '<=': 'le',             # Leq
        'or': 'or',
        'and' : 'and',
    }
    p[0]['orders'].append(dt[p[2]])
        
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
    length = len(p)
    if length == 2:
        deal_exp_len2(p)
    elif length == 3:
        deal_exp_len3(p)
    else:
        deal_exp_len4(p)
    p[0]['type'] = 'exp'

def p_list(p):
    '''
    list : '[' ']'
         | '[' explist ']'
    '''
    p[0] = {
        'type' : 'list',
        'orders' : [],
    }
    

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
