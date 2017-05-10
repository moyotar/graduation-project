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
        # ----------------------
        # 解释器运行状态：
        # 0：正常待机
        # 1：正常运行
        # 其他：异常待机
        # ----------------------
        self.execution_status = 0
        
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
        try:
            value = eval(operand)
        except Exception:
            value = operand
        self.operation_stack.append(value)

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
            'PC' : self.PC + 1,
            'memory' : len(self.memory),
            'loop_stack' : len(self.loop_stack),
        })
        # 创建新的局部存储区
        self.memory.append({})
        # 返回函数地址和当前PC的差值
        return pos - self.PC
    
    def op_return(self):
        # 恢复调用处上下文
        if not len(self.call_stack):
            # 最顶层return，结束运行
            self.execution_status = self.operation_stack.pop()
            return
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
        list_len = eval(operand)
        ls = []
        for i in xrange(list_len):
            ls.append(self.operation_stack.pop())
        self.operation_stack.append(ls)
        
    def op_newdict(self, operand):
        dict_len = eval(operand)
        dt = {}
        for i in xrange(dict_len):
            key = self.operation_stack.pop()
            value = self.operation_stack.pop()
            dt[key] = value
        self.operation_stack.append(dt)
        
    def op_index(self):
        key = self.operation_stack.pop()
        obj = self.operation_stack.pop()
        self.operation_stack.append(obj[key])
        
    def op_scope(self):
        self.memory.append({})

    def op_endscope(self):
        self.memory.pop()

    def op_setitem(self):
        key = self.operation_stack.pop()
        obj = self.operation_stack.pop()
        value = self.operation_stack.pop()
        obj[key] = value
    
    def op_unm(self):
        a = self.operation_stack.pop()
        self.operation_stack.append(-a)
        
    def op_break(self):
        return self.loop_stack[-1][0] - self.PC

    def op_continue(self):
        return self.loop_stack[-1][1] - self.PC

    def op_loop(self, operand):
        self.loop_stack.append((self.PC+1, self.PC+eval(operand)))

    def op_endloop(self):
        self.loop_stack.pop()

    def op_for(self):
        # ------------------------------------------
        # for 指令将迭代当前栈顶元素，在内存中生成两个
        # 列表。
        # 1. *__keyList__*
        # 2. *__valueList__*
        # 此外，还生成两个整形变量
        # 1. *__index__* 初始值为-1
        # 2. *__len__*
        # ------------------------------------------
        local_memory = self.memory[-1]
        for_obj = self.operation_stack.pop()
        local_memory['*__len__*'] = len(for_obj)
        local_memory['*__index__*'] = -1
        if type(for_obj) == type({}):
            local_memory['*__keyList__*'] = for_obj.keys()
            local_memory['*__valueList__*'] = for_obj.values()
        else:
            local_memory['*__keyList__*'] = range(len(for_obj))
            local_memory['*__valueList__*'] = for_obj

    def op_pop(self):
        self.operation_stack.pop()

    def execute(self, orders):
        self.__init__()
        self.orders = orders
        self.execution_status = 1
        while self.execution_status == 1:
            try:
                order = self.orders[self.PC]
                order = order.split('\t')
                operation = getattr(self, ''.join(['op_', order[0]]), None)
                # print('exec order:', order)
                delta = operation(*order[1:])
                if delta == None:
                    delta = 1
                # print('self.operation_stack:', self.operation_stack)
                # print('self.call_stack:', self.call_stack)
                # print('self.memory:', self.memory)
                # print('self.loop_stack:', self.loop_stack)
                self.PC += delta
            except Exception, e:
                print('RuntimeError', e)
                raise RuntimeError
