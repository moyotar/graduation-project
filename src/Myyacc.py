# -*- coding: utf-8 -*-

import ply.yacc as yacc
from Mylex import tokens

# 定义优先级
precedence = (
    ('nonassoc', '='),
    ('left', 'AND', 'OR'),
    ('nonassoc', '>', '<', 'Eq', 'Leq', 'Req'),
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
# ---------------------------------------------------

# ---------------------------------------------------
# p[0]除开chunk全部都是一个dict类型，包含两个字段：
# 1. type 类型
# 2. value 值
# ---------------------------------------------------

TYPE = 'type'
VALUE = 'value'

# 存储用户函数对应指令代码
# 序号为0，保留
ORDERS = ['',]

def p_chunk(p):
    'chunk : block'
    global ORDERS
    p[0] = []
    p[0].append(''.join(['jmp\t', str(len(ORDERS))]))
    p[0] += ORDERS[1:]
    p[0] += p[1][VALUE]
    # 程序最后执行return 0
    p[0].append('push\t0')
    p[0].append('return')
    # 最后，重置ORDERS
    ORDERS = ['',]
    
# 定义空产生式
def p_empty(p):
    'empty :'
    p[0] = {
        TYPE : 'empty',
        VALUE : [],
    }

def p_block(p):
    '''block : empty
             | stat
             | block stat'''
    p[0] = {
        TYPE : 'block',
    }
    p[0][VALUE] = p[1][VALUE]
    if len(p) == 3:
        p[0][VALUE] += p[2][VALUE]

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
    p[0] = {
        TYPE : 'stat',
        VALUE : [],
    }
    if p[1][TYPE] == 'func_call':
        # 函数调用语句，而非表达式，所以需要跟着pop操作
        p[1][VALUE].append('pop')
    p[0][VALUE] = p[1][VALUE]
    
def p_if_st(p):
    '''
    if_st : IF exp ':' block ';'
          | IF exp ':' block ELSE ':' block ';'    
    '''
    p[0] = {
        TYPE : 'if_st',
        VALUE : [],
    }
    block = ['scope'] + p[4][VALUE]
    length = len(p[4][VALUE]) + 3
    if p[5] != ';':
        length += 1
        block.append('endscope')
        block.append(''.join(['jmp\t', str(len(p[7][VALUE])+3)]))
        block.append('scope')
        block += p[7][VALUE]
    block.append('endscope')
    value = p[0][VALUE]
    value += p[2][VALUE]
    value.append('test\t2')
    value.append(''.join(['jmp\t', str(length)]))
    value += block

def p_for_st(p):
    '''
    for_st : FOR namelist IN list ':' block ';'
           | FOR namelist IN String ':' block ';'   
           | FOR namelist IN dict ':' block ';'
           | FOR namelist IN Name ':' block ';'   
    '''
    p[0] = {
        TYPE : 'for_st',
        VALUE : ['scope'],
    }
    value = p[0][VALUE]
    namelist = p[2][VALUE][0:2]
    # 先把要迭代的对象压入堆栈
    if p[4][TYPE] in ['list', 'dict']:
        value += p[4][VALUE]
    elif p[4][TYPE] == 'String':
        value.append(''.join(['push\t', p[4][VALUE]]))
    else:
        value.append(''.join(['load\t', p[4][VALUE]]))
    # ------------------------------------------
    # for 指令将迭代当前栈顶元素，在内存中生成两个
    # 列表。
    # 1. *__keyList__*
    # 2. *__valueList__*
    # 此外，还生成两个整形变量
    # 1. *__index__* 初始值为-1
    # 2. *__len__*
    # ------------------------------------------
    value.append('for')
    loop_body = []
    loop_body.append('push\t1')
    loop_body.append('load\t*__index__*')
    loop_body.append('add')
    loop_body.append('setl\t*__index__*')
    loop_body.append('load\t*__len__*')
    loop_body.append('load\t*__index__*')
    loop_body.append('lt')
    loop_body.append('test\t2')
    loop_body.append(''.join(['jmp\t', str(len(p[6][VALUE])+9)]))
    loop_body.append('load\t*__valueList__*')
    loop_body.append('load\t*__keyList__*')
    loop_body.append('load\t*__index__*')
    loop_body.append('index')
    loop_body.append(''.join(['setl\t', namelist[0]]))
    loop_body.append('index')
    if len(namelist) == 2:
        loop_body.append(''.join(['setl\t', namelist[1]]))
    else:
        loop_body.append('pop')
    loop_body += p[6][VALUE]
    # 循环的最后，执行jmp操作，回到循环开始处
    loop_body.append(''.join(['jmp\t', str(-len(loop_body))]))
    value.append(''.join(['loop\t', str(len(loop_body)+1)]))
    value += loop_body
    value.append('endloop')
    value.append('endscope')
    
def p_while_st(p):
    '''
    while_st : WHILE exp ':' block ';'
    '''
    p[0] = {
        TYPE : 'while_st',
        VALUE : ['scope',],
    }
    value = p[0][VALUE]
    block = p[4][VALUE]
    loop_body = []
    # 循环的主体，先加载exp
    loop_body += p[2][VALUE]
    # test, 判断循环条件，为真则指令计数器加2
    loop_body.append('test\t2')
    # 如果假，则执行下一条指令，利用jmp跳出循环
    loop_body.append(''.join(['jmp\t', str(len(block)+2)]))
    loop_body += block
    # 循环的最后，执行jmp操作，回到循环开始处
    loop_body.append(''.join(['jmp\t', str(-len(loop_body))]))
    # 整个循环的指令：loop + loop_body + endloop
    value.append(''.join(['loop\t', str(len(loop_body)+1)]))
    value += loop_body
    value.append('endloop')
    value.append('endscope')
    
def p_break_st(p):
    'break_st : BREAK'
    p[0] = {
        TYPE : 'break_st',
        VALUE : ['break'],
    }

def p_continue_st(p):
    'continue_st : CONTINUE'
    p[0] = {
        TYPE : 'continue_st',
        VALUE : ['continue'],
    }

def p_return_st(p):
    '''return_st : RETURN ';'
                 | RETURN explist ';'
    '''
    p[0] = {
        TYPE : 'return_st',
        VALUE : [],
    }
    if len(p) == 3:
        p[0][VALUE].append('push\tNone')
    else:
        explist = p[2][VALUE]
        explist.reverse()
        len_exp = len(explist)
        p[0][VALUE] = [order for exp_value in explist
                       for order in exp_value]
        if len(explist) > 1:
            # 以list形式返回
            p[0][VALUE].append(''.join(['newlist\t', str(len(explist))]))
    # return op
    p[0][VALUE].append('return')
    
def p_assign_st(p):
    '''
        assign_st : namelist '=' explist
                  | obj_domains '=' exp
    '''
    p[0] = {
        TYPE : 'assign_st',
        VALUE : []
    }
    if p[1][TYPE] == 'namelist':
        namelist = p[1][VALUE]
        len_namelist = len(namelist)
        explist = p[3][VALUE]
        len_exp = len(explist)
        if len_namelist > len_exp:
             explist += [['push\tNone']] * (len_namelist - len_exp)
        for index, name in enumerate(namelist):
            p[0][VALUE] += explist[index]
            p[0][VALUE].append(''.join(['setg\t', name]))
    else:
        # 先把值压入堆栈
        p[0][VALUE] += p[3][VALUE]
        # 将要赋值的对象加载进栈
        p[0][VALUE] += p[1][VALUE][0]
        # 依次index操作，除了最后一项
        for exp_value in p[1][VALUE][1:-1]:
            p[0][VALUE] += exp_value
            # index op
            p[0][VALUE].append('index')
        # 执行setitem操作
        p[0][VALUE] += p[1][VALUE][-1]
        p[0][VALUE].append('setitem')
        
def p_local_def_st(p):
    '''
    local_def_st : LOCAL namelist
                 | LOCAL namelist '=' explist     
    '''
    p[0] = {
        TYPE : 'local_def_st',
        VALUE : [],
    }
    namelist = p[2][VALUE]
    len_namelist = len(namelist)
    explist = [['push\tNone']] * len_namelist
    if len(p) > 3:
        explist = p[4][VALUE]
        len_exp = len(explist)
        if len_namelist > len_exp:
            explist += [['push\tNone']] * (len_namelist - len_exp)
    for index, name in enumerate(namelist):
        p[0][VALUE] += explist[index]
        p[0][VALUE].append(''.join(['setl\t', name]))

def p_func_def_st(p):
    '''
    func_def_st : LOCAL FUNC Name '(' ')' ':' block ';'
                | LOCAL FUNC Name '(' namelist ')' ':' block ';'
                | FUNC Name '(' namelist ')' ':' block ';'
                | FUNC Name '(' ')' ':' block ';'
    '''
    name = namelist = block = None
    opcode = 'setg'
    if p[1][VALUE] == 'local':
        opcode = 'setl'
        name = p[3]
        if p[5] != ')':
            namelist = p[5][VALUE]
            block = p[8]
        else:
            block = p[7]
            namelist = []
    else:
        name = p[2]
        if p[4] != ')':
            namelist = p[4][VALUE]
            block = p[7]
        else:
            block = p[6]
            namelist = []
    func_pre_orders = []
    namelist.reverse()
    for _name in namelist:
        # 进入函数前，先把实参传递给形参，用操作setl
        func_pre_orders.append(''.join(['setl\t', _name]))
    # record function postion
    global ORDERS
    pos = len(ORDERS)
    ORDERS += func_pre_orders + block[VALUE]
    # 函数的最后，自动加上return语句
    ORDERS += ['push\tNone', 'return']
    p[0] = {
        TYPE : 'func_def_st',
        VALUE : []
    }
    # 创建一个字典，记录函数必要的信息
    p[0][VALUE].append(''.join(['push\t', str(pos)]))
    p[0][VALUE].append('push\tpos')
    p[0][VALUE].append(''.join(['push\t', str(len(namelist))]))
    p[0][VALUE].append('push\tparams')
    p[0][VALUE].append('newdict\t2')
    # 把函数信息存储到内存
    p[0][VALUE].append(''.join([opcode, '\t', name[VALUE]]))
    
def p_func_call(p):
    '''
    func_call : Name '(' ')'
              | Name '(' explist ')'
    '''
    p[0] = {
        TYPE : 'func_call',
        VALUE : [],
    }
    if len(p) == 4:
        # 0个实参
        p[0][VALUE].append('push\t0')
        p[0][VALUE].append(''.join(['call\t', p[1][VALUE]]))
    else:
        length = len(p[3][VALUE])
        # exp入栈
        p[0][VALUE] = [order for exp_value in p[3][VALUE]
                       for order in exp_value]
        # 实参个数入栈
        p[0][VALUE].append(''.join(['push\t', str(len(p[3][VALUE]))]))
        # 函数调用操作
        p[0][VALUE].append(''.join(['call\t', p[1][VALUE]]))
        
def p_namelist(p):
    '''
    namelist : Name
             | namelist ',' Name
    '''
    p[0] = {
        TYPE : 'namelist',
        VALUE : [],
    }
    if len(p) == 2:
        p[0][VALUE].append(p[1][VALUE])
    else:
        p[0][VALUE] = p[1][VALUE]
        p[0][VALUE].append(p[3][VALUE])
        
def p_explist(p):
    '''
    explist : exp
            | explist ',' exp
    ''' 
    p[0] = {
        TYPE : 'explist',
        VALUE : [],
    }
    if len(p) == 2:
        p[0][VALUE].append(p[1][VALUE])
    else:
        p[0][VALUE] = p[1][VALUE]
        p[0][VALUE].append(p[3][VALUE])

def deal_exp_len2(p):
    res = {
        VALUE : []
    }
    tp = p[1][TYPE]
    if tp in ['NIL', 'FALSE', 'TRUE', 'Number', 'String']:
        # 常量，指令push
        res[VALUE].append("".join(["push\t", str(p[1][VALUE])]))
    elif tp in ['list', 'dict', 'func_call']:
        res[VALUE] = p[1][VALUE]
    elif tp == 'Name':
        # 变量, load
        res[VALUE].append("".join(["load\t", str(p[1][VALUE])]))
    else:
        # obj_domains
        values_list = p[1][VALUE]
        res_values = res[VALUE]
        # 先把要做元素访问的对象load进操作栈
        res_values += values_list[0]
        for exp_values in values_list[1:]:
            # 依次加载每个exp的值进栈，然后执行index指令
            res_values += exp_values
            res_values.append('index')
    p[0] = res
            
def deal_exp_len3(p):
    # 处理负号和not
    p[0] = {VALUE : p[1][VALUE]}
    if p[1] == '-':
        p[0][VALUE].append('unm')
    else:
        p[0][VALUE].append('not')
        
def deal_exp_len4(p):
    if p[1] == '(':
        p[0] = p[2]
        return
    p[0] = {VALUE : []}
    if p[2] in ['>=', '>']:
        # 对调位置，转换成小于或则和小于等于
        p[0][VALUE] += p[1][VALUE]
        p[0][VALUE] += p[3][VALUE]
        if p[2] == '>=':
            p[0][VALUE].append('le')
        else:
            p[0][VALUE].append('lt')
        return
    p[0][VALUE] += p[3][VALUE]
    p[0][VALUE] += p[1][VALUE]
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
    key = p[2]
    if type(p[2]) == type({}):
        key = p[2][VALUE]
    p[0][VALUE].append(dt[key])
        
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
    p[0][TYPE] = 'exp'

def p_list(p):
    '''
    list : '[' ']'
         | '[' explist ']'
    '''
    p[0] = {
        TYPE : 'list',
        VALUE : [],
    }
    if len(p) == 3:
        # 创建空list，即元素数个数为0
        p[0][VALUE].append('newlist\t0')
    else:
        # 把exp都加载入操作栈，然后newlist操作
        p[2][VALUE].reverse()
        values_list = p[2][VALUE]
        for values in values_list:
            p[0][VALUE] += values
        p[0][VALUE].append(''.join(['newlist\t', \
                                      str(len(values_list))]))
        
def p_dict(p):
    '''
    dict : '{' '}'
         | '{' itemlist '}'
    '''
    p[0] = {
        TYPE : 'dict',
        VALUE : []
    }
    if len(p) == 3:
        # 空dict，0个元素
        p[0][VALUE].append('newdict\t0')
    else:
        length = len(p[2][VALUE]) / 2
        # 先加载所有的item入栈
        p[0][VALUE] = [value for item_values in p[2][VALUE]
                        for value in item_values]
        # 执行创建dict操作
        p[0][VALUE].append(''.join(['newdict\t', str(length)]))
        
def p_itemlist(p):
    '''
    itemlist : item
             | itemlist ',' item
    '''
    p[0] = {
        TYPE : 'itemlist',
        VALUE : []
    }
    if len(p) == 2:
        p[0][VALUE].append(p[1][VALUE])
    else:
        p[0][VALUE] = p[1][VALUE]
        p[0][VALUE].append(p[3][VALUE])

def p_item(p):
    '''
    item : exp ':' exp
    '''
    p[0] = {
        TYPE : 'item',
        VALUE : p[3][VALUE] + p[1][VALUE]
    }

def p_obj_domains(p):
    '''
    obj_domains : Name domains
    '''
    p[0] = {
        TYPE : 'obj_domains',
        VALUE : [],
    }
    p[0][VALUE].append([''.join(['load\t', p[1][VALUE]])])
    p[0][VALUE] += p[2][VALUE]

def p_domains(p):
    '''
    domains : '[' exp ']'
            | domains '[' exp ']'    
    '''
    p[0] = {
        TYPE : 'domains',
        VALUE : [],
    }
    if p[1] == '[':
        p[0][VALUE].append(p[2][VALUE])
    else:
        p[0][VALUE] = p[1][VALUE]
        p[0][VALUE].append(p[3][VALUE])

def p_error(p):
    print("Syntax error!"+str(p))
