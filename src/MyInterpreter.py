# -*- coding: utf-8 -*-

class MyInterpreter(object):
    def __init__(self):
        '''
        解释器采用栈式计算机结构
        operation_stack: 操作堆栈
        call_stack: 调用堆栈
        memory: 内存
        PC: 程序计数器
        loop_stack: 循环堆栈，维护循环非自然结束跳转(break,continue)
        orders: 指令列表
        '''
        self.operation_stack = []
        self.call_stack = []
        self.memory = []
        self.PC = 0
        self.loop_stack = []
        self.orders = []

    def op_setg(self, operand):
        pass

    def op_setl(self, operand):
        pass

    def op_push(self, operand):
        pass

    def op_load(self, operand):
        pass

    def op_add(self):
        pass
    
    def op_sub(self):
        pass

    def op_times(self):
        pass
    
    def op_div(self):
        pass

    def op_mod(self):
        pass

    def op_call(self, operand):
        pass

    def op_return(self):
        pass

    def op_jmp(self, operand):
        pass

    def op_lq(self):
        pass

    def op_lt(self):
        pass

    def op_le(self):
        pass

    def op_not(self):
        pass

    def op_and(self):
        pass

    def op_or(self):
        pass

    def op_test(self, operand):
        pass

    def op_newlist(self, operand):
        pass

    def op_newdict(self, operand):
        pass

    def op_index(self):
        pass
    
    def op_scope(self):
        pass

    def op_endscope(self):
        pass

    def op_setitem(self):
        pass
    
    def op_unm(self):
        pass
    
    def op_break(self):
        pass

    def op_continue(self):
        pass

    def op_loop(self, operand):
        pass

    def op_endloop(self):
        pass

    def op_for(self):
        pass

    def op_pop(self):
        pass

    def execute(self, orders):
        pass
