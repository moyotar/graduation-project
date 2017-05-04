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
        self.memory = [{}]
        self.PC = 0
        self.loop_stack = []
        self.orders = []
        
    # --------------------------------------------------------
    # 内存采用分层机制，以处理变量的作用域，memory[0]代表最外层
    # ，也就是全局区，每进入新的scope则加一层，作为当前局部区
    # 所有指令实现函数均以op_为前缀，返回值为PC增量，None代表默认的+1。
    # --------------------------------------------------------    
    def op_setg(self, operand):
        top_stack = self.operation_stack.pop()
        memory_depth = len(self.memory)
        # 依层次查找，如果没有，说明是新定义的全局变量，存储
        # 在内存0层
        for i in xrange(memory_depth-1, -1, -1):
            if self.memory[i].has_key(operand):
                self.memory[i][operand] = top_stack
                return
        self.memory[0][operand] = top_stack
        
    def op_setl(self, operand):
        # 存储在局部空间
        top_stack = self.operation_stack.pop()
        self.memory[-1][operand] = top_stack

    def op_push(self, operand):
        self.operation_stack.append(eval(operand))

    def op_load(self, operand):
        # 从局部到全局，依层查找要压栈的变量
        memory_depth = len(self.memory)
        for i in xrange(memory_depth-1, -1, -1):
            if self.memory[i].has_key(operand):
                self.operation_stack.append(self.memory[i][operand])
                return
        # 没有找到，说明是未声明定义的变量，默认为None
        self.operation_stack.append(None)
        
    def op_add(self):
        a = self.operation_stack.pop()
        b = self.operation_stack.pop()
        self.operation_stack.append(a+b)
    
    def op_sub(self):
        a = self.operation_stack.pop()
        b = self.operation_stack.pop()
        self.operation_stack.append(a-b)

    def op_times(self):
        a = self.operation_stack.pop()
        b = self.operation_stack.pop()
        self.operation_stack.append(a*b)
    
    def op_div(self):
        a = self.operation_stack.pop()
        b = self.operation_stack.pop()
        self.operation_stack.append(a/b)

    def op_mod(self):
        a = self.operation_stack.pop()
        b = self.operation_stack.pop()
        self.operation_stack.append(a%b)

    def op_call(self, operand):
        memory_depth = len(self.memory)
        func_info = None
        for i in xrange(memory_depth-1, -1, -1):
            if self.memory[i].has_key(operand):
                func_info = self.memory[i][operand]
                break
        pos = func_info['pos']
        params = func_info['params']
        real_params = self.operation_stack.pop()
        if params >= real_params:
            # 形参个数多于实参
            # 操作堆栈补足None
            self.operation_stack += [None] * (params - real_params)
        else:
            # 实参个数多于形参，去掉多余的
            self.operation_stack = self.operation_stack[:params-real_params]
        # 保存当前上下文,压入调用堆栈
        self.call_stack.append({
            'PC' : self.PC,
            'memory' : len(self.memory),
            'loop_stack' : len(self.loop_stack),
        })
        # 创建新的局部存储区
        self.memory.append({})
        # 返回函数地址和当前PC的差值
        return pos - self.PC
    
    def op_return(self):
        # 恢复调用处上下文
        origin = self.call_stack.pop()
        self.memory = self.memory[:origin['memory']]
        self.loop_stack = self.loop_stack[:origin['loop_stack']]
        return origin['PC'] - self.PC
    
    def op_jmp(self, operand):
        return eval(operand)

    def op_lq(self):
        a = self.operation_stack.pop()
        b = self.operation_stack.pop()
        self.operation_stack.append(a==b)
        
    def op_lt(self):
        a = self.operation_stack.pop()
        b = self.operation_stack.pop()
        self.operation_stack.append(a<b)

    def op_le(self):
        a = self.operation_stack.pop()
        b = self.operation_stack.pop()
        self.operation_stack.append(a<=b)

    def op_not(self):
        a = self.operation_stack.pop()
        self.operation_stack.append(not a)

    def op_and(self):
        a = self.operation_stack.pop()
        b = self.operation_stack.pop()
        self.operation_stack.append(bool(a and b))
        
    def op_or(self):
        a = self.operation_stack.pop()
        b = self.operation_stack.pop()
        self.operation_stack.append(bool(a or b))

    def op_test(self, operand):
        if self.operation_stack.pop():
            return eval(operand)
        
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
