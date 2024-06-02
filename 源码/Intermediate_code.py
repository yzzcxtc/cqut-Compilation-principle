import lex
from anytree import Node, RenderTree
from fuhao_table import getfuhao


class Token:
    def __init__(self, value, kind):
        self.kind = kind  # Token的类型
        self.value = value  # Token的值，对于数字类型的Token来说是必须的


global quadruples
global temp_count
temp_count = 0
quadruples = []


def new_temp():
    global temp_count
    temp_var = f'T{temp_count}'
    temp_count += 1
    return temp_var


def emit(op, arg1, arg2, result):
    global quadruples
    # if arg1[0]!='T' and arg1 not in fuhaobiao:
    #     print('错误')
    quadruples.append((op, arg1, arg2, result))


class Arithmetic_expression:
    def __init__(self, tokens, midcode):
        self.tokens = tokens
        self.current_token = None
        self.subscript = 0
        self.midcode = midcode
        self.max = len(tokens)
        self.next_token()

    def next_token(self):
        self.current_token = self.tokens[self.subscript]
        self.subscript += 1
        if self.subscript > self.max - 1:
            self.subscript = self.max - 1

    def eat(self, kind):
        if self.current_token.kind in kind:
            self.next_token()
        else:
            raise Exception(f'期望的Token: {kind}, 实际的Token: {self.current_token}')

    def factor(self):
        if self.current_token.kind in [500, 503]:  # 整数: 500, 浮点数: 503

            med_arg = self.current_token.value
            self.eat([500, 503])
            return True, med_arg
        elif self.current_token.kind in [700]:  # 标识符: 700
            med_arg = self.current_token.value
            self.eat([700])
            if med_arg=='read' :
                tmp_name='中间运行的不用管'
                if self.midcode:
                    tmp_name=new_temp()
                    emit('call', 'read', '_', tmp_name)
                self.eat([303])
                self.eat([304])
                return True, tmp_name
            return True, med_arg
        elif self.current_token.kind in [303]:  # (
            self.eat([303])
            valid, factor_result = self.expr()
            if not valid:
                return False, None
            self.eat([304])  # )
            return True, factor_result
        elif self.current_token.kind in [402]:  # -
            self.eat([402])
            valid, factor_result = self.expr()
            if not valid:
                return False, None
            return True, factor_result
        else:
            return False, None

    def term(self):
        valid, term_result = self.factor()
        if not valid:
            return False, None
        while self.current_token.kind in [403, 404]:  # *, /
            op = self.current_token.value
            self.eat([403, 404])
            valid, factor_result = self.factor()
            if not valid:
                return False, None
            temp_var = '中间运行的不用管'
            if self.midcode:
                temp_var = new_temp()
                emit(op, term_result, factor_result, temp_var)
            term_result = temp_var
        return True, term_result

    def expr(self):
        valid, expr_result = self.term()
        if not valid:
            return False, None
        while self.current_token.kind in [401, 402,405]:  # +, -,%
            op = self.current_token.value
            self.eat([401, 402,405])
            valid, term_result = self.term()
            if not valid:
                return False, None
            temp_var = '中间运行的不用管'
            if self.midcode:
                temp_var = new_temp()
                emit(op, expr_result, term_result, temp_var)
            expr_result = temp_var
        return True, expr_result

    def parse(self):
        valid, expr_result = self.expr()
        # if  self.current_token.kind!=307:
        #     valid=False
        #     expr_result='该赋值语句，不是一个仅仅的字符，或者说不是算术表达式'
        if not valid:
            # print(f'算术错误的表达式: {self.current_token.kind, self.current_token.value}')
            return 0, -1, '算术错误'
        return 1, self.subscript, expr_result


class Assignment_expression:
    def __init__(self, tokens,midcode):
        self.tokens = tokens
        self.current_token = None
        self.subscript = 0
        self.max = len(tokens)
        self.midcode=midcode
        self.next_token()

    def next_token(self):

        self.current_token = self.tokens[self.subscript]
        self.subscript += 1
        if self.subscript > self.max - 1:
            self.subscript = self.max - 1

    def eat(self, kind):
        if self.current_token.kind in kind:
            self.next_token()
        else:
            raise Exception(f'期望的Token: {kind}, 实际的Token: {self.current_token.kind, self.current_token.value}')

    def assignment_expression(self):

        ###赋值语句
        if self.current_token.kind in [700]:  # id
            temp_var=self.current_token.value
            self.eat([700])
            if self.current_token.kind in [416]:  # =
                op=self.current_token.value
                self.eat([416])
                med_1 = Arithmetic_expression(self.tokens[self.subscript - 1:],self.midcode)
                val1, sub1,suanshu_reult = med_1.parse()
                med_2 = Boolean_expression(self.tokens[self.subscript - 1:],self.midcode)
                val2, sub2,buer_reult = med_2.parse()
                if not val1 and not val2:
                    return False
                if val1:
                    # 跳转到算术表达式运行到的token为止
                    for yzz in range(sub1 - 1):
                        self.next_token()
                    if self.midcode:
                        emit(op, suanshu_reult, '__', temp_var)
                elif val2:
                    # 跳转到布尔表达式运行到的token为止
                    for yzz in range(sub2 - 1):
                        self.next_token()
                    if self.midcode:
                        emit(op, buer_reult, '__', temp_var)
                return True,temp_var

        return False,'赋值错误'

    def parse(self):
        # 尝试解析赋值表达式
        assign=self.assignment_expression()
        if not assign[0]:
            # print(f'赋值错误的表达式: {self.current_token.value}')
            return 0, -1,'赋值错误'
        return 1, self.subscript,assign[1]


class Boolean_expression:
    def __init__(self, tokens, midcode):
        self.tokens = tokens
        self.current_token = None
        self.subscript = 0
        self.max = len(tokens)
        self.midcode = midcode
        self.next_token()
        self.temp_count = 0

    def next_token(self):
        self.current_token = self.tokens[self.subscript]
        self.subscript += 1
        if self.subscript > self.max - 1:
            self.subscript = self.max - 1

    def eat(self, kind):
        if self.current_token.kind in kind:
            self.next_token()
        else:
            raise Exception(f'期望的Token: {kind}, 实际的Token: {self.current_token}')

    def factor(self):
        a1 = True
        a2 = True
        if self.midcode:
            a1 = False
            a2 = True
        else:
            a1 = False
            a2 = False
        med1 = Arithmetic_expression(self.tokens[self.subscript - 1:], a1)  # 算术
        val1, sub1, fuzhi_result = med1.parse()
        if self.current_token.kind in [500, 503, 504]:  # 整数, 浮点数, 负数
            value = self.current_token.value
            self.eat([500, 503, 504])
            return value
        elif val1:####判断一边是不是算术表达式
            med1 = Arithmetic_expression(self.tokens[self.subscript - 1:], a2)  # 算术
            val1, sub1, fuzhi_result = med1.parse()
            for _ in range(sub1 - 1):
                self.next_token()
            return fuzhi_result
        elif self.current_token.kind in [700]:  # 标识符
            value = self.current_token.value
            self.eat([700])
            return value
        elif self.current_token.kind in [412]:  # !
            self.eat([412])
            operand = self.factor()
            temp = '中间运行的不用管'
            if self.midcode:
                temp = new_temp()
                emit('NOT', operand, '_', temp)
            return temp
        else:
            raise Exception(f'无效的因子: {self.current_token}')

    def comparison(self):
        if self.current_token.kind in [303]:  # (
            self.eat([303])
            result = self.comparison()
            self.eat([304])  # )
            return result

        left = self.factor()
        if self.current_token.kind in [425, 426, 427, 428, 429, 430]:  # <, >, <=, >=, ==, !=
            op = self.current_token.value
            self.eat([425, 426, 427, 428, 429, 430])
            right = self.factor()
            temp = '中间运行的不用管'
            if self.midcode:
                temp = new_temp()
                emit(op, left, right, temp)
            return temp
        return left

    def expr(self):
        result = self.comparison()
        while self.current_token.kind in [413, 414]:  # &&, ||
            op = self.current_token.value
            self.eat([413, 414])
            right = self.comparison()
            temp = '中间运行的不用管'
            if self.midcode:
                temp = new_temp()
                emit(op, result, right, temp)
            result = temp
        return result

    def parse(self):
        result = self.expr()
        if result == None:
            raise Exception(f'布尔错误的表达式: {self.current_token.value}')
        return 1, self.subscript, result


class Declaration_statement:
    def __init__(self, tokens,midcode):
        self.tokens = tokens
        self.current_token = None
        self.subscript = 0
        self.max = len(tokens)
        self.midcode=midcode
        self.next_token()

    def next_token(self):
        self.current_token = self.tokens[self.subscript]
        self.subscript += 1
        if self.subscript > self.max - 1:
            self.subscript = self.max - 1

    def eat(self, kind):
        if self.current_token.kind in kind:
            self.next_token()
        else:
            raise Exception(f'期望的Token: {kind}, 实际的Token: {self.current_token}')

    def exper(self):
        #这里没有添加布尔的声明
        if self.current_token.kind in [104, 113, 118, 109]:  # char :104 float :113 int :118  double :109
            type_token = self.current_token
            self.eat([104, 113, 118, 109])
            while self.current_token.kind != 307:  # ;
                if self.current_token.kind in [700]:  # id
                    temp_var=self.current_token.value
                    self.eat([700])
                    # if self.midcode:',': 308
                    #     emit('DECLARE', type_token.value, '_',temp_var)
                    if self.current_token.kind in [416]:  # =
                        op=self.current_token.value
                        self.eat([416])
                        med_ = Arithmetic_expression(self.tokens[self.subscript - 1:],self.midcode)
                        val, sub,suanshu_reult = med_.parse()
                        if not val:
                            return False
                        # 跳转到算术表达式运行到的token为止
                        for yzz in range(sub - 1):
                            self.next_token()
                        if self.midcode:
                            emit(op, suanshu_reult, '__', temp_var)
                    if self.current_token.kind in [308]:   #,
                        self.eat([308])
                else:
                    return False
            return True
        return False

    def parse(self):
        # 尝试解析声明表达式
        if not self.exper():
            # print(48515)
            return 0, -1
        return 1, self.subscript


class While_statement:
    def __init__(self, tokens, ROOT, midcode):
        self.tokens = tokens
        self.current_token = None
        self.subscript = 0
        self.max = len(tokens)
        self.root = ROOT
        self.midcode = midcode
        self.next_token()

    def next_token(self):
        self.current_token = self.tokens[self.subscript]
        self.subscript += 1
        if self.subscript > self.max - 1:
            self.subscript = self.max - 1

    def eat(self, kind):
        if self.current_token.kind in kind:
            self.next_token()
        else:
            raise Exception(f'期望的Token: {kind}, 实际的Token: {self.current_token}')

    def yuju_list(self):
        control=0
        while self.current_token.kind not in [302]:  # }
            print(f'while语句第{control+1}轮')
            control=control+1
            # 判断到底填不填加四元式逻辑
            a1 = True
            a2 = True
            if self.midcode:
                a1 = False
                a2 = True
            else:
                a1 = False
                a2 = False
            med1 = Assignment_expression(self.tokens[self.subscript - 1:], a1)  # 赋值
            val1, sub1, fuzhi_result = med1.parse()
            if val1:
                med1 = Assignment_expression(self.tokens[self.subscript - 1:], a2)  # 赋值
                val1, sub1, fuzhi_result = med1.parse()
                for _ in range(sub1 - 1):
                    self.next_token()
                self.eat([307])  # ;
                child1 = Node("赋值表达式", parent=self.root)
                continue

            med3 = Declaration_statement(self.tokens[self.subscript - 1:], a1)
            val3, sub3 = med3.parse()
            if val3:
                med3 = Declaration_statement(self.tokens[self.subscript - 1:], a2)
                val3, sub3 = med3.parse()
                for _ in range(sub3 - 1):
                    self.next_token()
                self.eat([307])  # ;
                child1 = Node("声明表达式", parent=self.root)
                continue

            med4 = IF(self.tokens[self.subscript - 1:], Node("中间，保证运行的，不用管"), a1)
            val4, sub4 = med4.parse()
            if val4:
                child1 = Node("IF语句", parent=self.root)
                med4 = IF(self.tokens[self.subscript - 1:], child1, a2)
                _, _ = med4.parse()
                for _ in range(sub4 - 1):
                    self.next_token()
                continue

            med5 = While_statement(self.tokens[self.subscript - 1:], Node("中间，保证运行的，不用管"), a1)
            val5, sub5 = med5.parse()
            if val5:
                child1 = Node("while语句", parent=self.root)
                med5 = While_statement(self.tokens[self.subscript - 1:], child1, a2)
                _, _ = med5.parse()
                for _ in range(sub5 - 1):
                    self.next_token()
                continue

            med6 = For_statement(self.tokens[self.subscript - 1:], Node("中间，保证运行的，不用管"), a1)
            val6, sub6 = med6.parse()
            if val6:
                child1 = Node("for语句", parent=self.root)
                med6 = For_statement(self.tokens[self.subscript - 1:], child1, a2)
                _, _ = med6.parse()
                for _ in range(sub6 - 1):
                    self.next_token()
                continue

            med7 = write_expression(self.tokens[self.subscript - 1:], a1)
            val7, sub7 = med7.parse()
            if val7:

                med7 = write_expression(self.tokens[self.subscript - 1:], a2)
                _, _ = med7.parse()
                for _ in range(sub7 - 1):
                    self.next_token()
                self.eat([307])  # ;
                child1 = Node("写出语句", parent=self.root)
                continue
            val1, sub1 = 0, -1
            val2, sub2 = 0, -1
            val3, sub3 = 0, -1
            val4, sub4 = 0, -1
            val5, sub5 = 0, -1
            val6, sub6 = 0, -1
            val7, sub7 = 0, -1
        return True

    def while_statement(self):
        # while_statement -> 'while' '(' condition ')' '{' loop_body '}'
        if self.current_token.kind in [134]:  # while
            self.eat([134])
            start_quad = len(quadruples)  # 记录循环开始的位置
            if self.current_token.kind in [303]:  # (
                self.eat([303])
                med1 = Boolean_expression(self.tokens[self.subscript - 1:], self.midcode)  # 布尔表达式
                val1, sub1, buer_result = med1.parse()
                if not val1:
                    return False
                for _ in range(sub1 - 1):
                    self.next_token()
                self.eat([304])  # )

                mid_jump = -1

                if self.midcode:
                    temp = new_temp()
                    emit('JZ', buer_result, '_', temp)
                    jump_quad = len(quadruples) - 1  # 记录跳转指令的位置
                    mid_jump = jump_quad

                if self.current_token.kind in [301]:  # {
                    self.eat([301])
                    valid = self.yuju_list()
                    if not valid:
                        return False
                    self.eat([302])  # }
                    if self.midcode:
                        emit('J', '_', '_', start_quad)  # 跳回循环开始位置
                        quadruples[mid_jump] = ('JZ', buer_result, '_', len(quadruples))  # 更新跳转指令的目标
                    return True
        return False

    def parse(self):
        if not self.while_statement():
            return 0, -1
        return 1, self.subscript


class For_statement:
    def __init__(self, tokens, ROOT, midcode):
        self.midcode = midcode
        self.tokens = tokens
        self.current_token = None
        self.subscript = 0
        self.root = ROOT
        self.max = len(tokens)
        self.next_token()

    def next_token(self):
        self.current_token = self.tokens[self.subscript]
        self.subscript += 1
        if self.subscript > self.max - 1:
            self.subscript = self.max - 1

    def eat(self, kind):
        if self.current_token.kind in kind:
            self.next_token()
        else:
            raise Exception(f'for语句出错，期望的Token: {kind}, 实际的Token: {self.current_token.value}')

    def yuju_list(self):
        control=0
        while self.current_token.kind not in [302]:  # }
            print(f'FOR语句中第{control+1}')
            control=control+1
            # 判断到底填不填加四元式逻辑
            a1 = True
            a2 = True
            if self.midcode:
                a1 = False
                a2 = True
            else:
                a1 = False
                a2 = False
            med1 = Assignment_expression(self.tokens[self.subscript - 1:], a1)  # 赋值
            val1, sub1, fuzhi_result = med1.parse()
            if val1:
                med1 = Assignment_expression(self.tokens[self.subscript - 1:], a2)  # 赋值
                val1, sub1, fuzhi_result = med1.parse()
                for _ in range(sub1 - 1):
                    self.next_token()
                self.eat([307])  # ;
                child1 = Node("赋值表达式", parent=self.root)
                continue

            med3 = Declaration_statement(self.tokens[self.subscript - 1:], a1)
            val3, sub3 = med3.parse()
            if val3:
                med3 = Declaration_statement(self.tokens[self.subscript - 1:], a2)
                val3, sub3 = med3.parse()
                for _ in range(sub3 - 1):
                    self.next_token()
                self.eat([307])  # ;
                child1 = Node("声明表达式", parent=self.root)
                continue

            med4 = IF(self.tokens[self.subscript - 1:], Node("中间，保证运行的，不用管"), a1)
            val4, sub4 = med4.parse()
            if val4:
                child1 = Node("IF语句", parent=self.root)
                med4 = IF(self.tokens[self.subscript - 1:], child1, a2)
                _, _ = med4.parse()
                for _ in range(sub4 - 1):
                    self.next_token()
                continue

            med5 = While_statement(self.tokens[self.subscript - 1:], Node("中间，保证运行的，不用管"), a1)
            val5, sub5 = med5.parse()
            if val5:
                child1 = Node("while语句", parent=self.root)
                med5 = While_statement(self.tokens[self.subscript - 1:], child1, a2)
                _, _ = med5.parse()
                for _ in range(sub5 - 1):
                    self.next_token()
                continue

            med6 = For_statement(self.tokens[self.subscript - 1:], Node("中间，保证运行的，不用管"), a1)
            val6, sub6 = med6.parse()
            if val6:
                child1 = Node("for语句", parent=self.root)
                med6 = For_statement(self.tokens[self.subscript - 1:], child1, a2)
                _, _ = med6.parse()
                for _ in range(sub6 - 1):
                    self.next_token()
                continue

            med7 = write_expression(self.tokens[self.subscript - 1:], a1)
            val7, sub7 = med7.parse()
            if val7:

                med7 = write_expression(self.tokens[self.subscript - 1:], a2)
                _, _ = med7.parse()
                for _ in range(sub7 - 1):
                    self.next_token()
                self.eat([307])  # ;
                child1 = Node("写出语句", parent=self.root)
                continue
            val1, sub1 = 0, -1
            val2, sub2 = 0, -1
            val3, sub3 = 0, -1
            val4, sub4 = 0, -1
            val5, sub5 = 0, -1
            val6, sub6 = 0, -1
            val7, sub7 = 0, -1
        return True

    def for_statement(self):
        # for_statement -> 'for' '(' initialization ';' condition ';' iteration ')' '{' loop_body '}'
        if self.current_token.kind in [114]:  # 'for'
            self.eat([114])
            if self.current_token.kind in [303]:  # '('
                self.eat([303])

                # 初始化
                med1 = Assignment_expression(self.tokens[self.subscript - 1:], self.midcode)
                val1, sub1,fuzhi_result = med1.parse()
                if not val1:
                    return False
                for yzz in range(sub1 - 1):
                    self.next_token()
                self.eat([307])  # ';'

                # 条件
                start_quad = len(quadruples)  # 记录循环开始的位置
                med2 = Boolean_expression(self.tokens[self.subscript - 1:], self.midcode)
                val2, sub2, buer_result = med2.parse()
                if not val2:
                    return False
                for yzz in range(sub2 - 1):
                    self.next_token()
                self.eat([307])  # ';'
                mid_jump1 = -1
                mid_jump2 = -1
                if self.midcode:
                    emit('jnz', buer_result, '_', '-1')
                    jump_quad = len(quadruples) - 1  # 记录跳转指令的位置,记录真的跳到哪里跳转出去
                    mid_jump1 = jump_quad

                    emit('jz', buer_result, '_', '-1')
                    jump_quad = len(quadruples) - 1  # 记录跳转指令的位置，跳转到假的执行的位置
                    mid_jump2 = jump_quad

                # 迭代
                start_quad2 = len(quadruples)
                med3 = Assignment_expression(self.tokens[self.subscript - 1:], self.midcode)
                val3, sub3, fuzhi_result = med3.parse()
                if not val3:
                    return False
                for yzz in range(sub3 - 1):
                    self.next_token()
                self.eat([304])  # ')'
                if self.midcode:
                    emit('J', '_', '_', start_quad)  # 跳回循环判断的位置

                if self.current_token.kind in [301]:  # '{'
                    self.eat([301])
                    if self.midcode:
                        quadruples[mid_jump1] = ('jnz', buer_result, '_', len(quadruples))  # 更新跳转指令的目标
                    valid = self.yuju_list()
                    if not valid:
                        return False
                    if self.midcode:
                        emit('J', '_', '_', start_quad2)  # 跳回for ; ; zheli
                    self.eat([302])  # '}'
                    if self.midcode:
                        quadruples[mid_jump2] = ('jz', buer_result, '_', len(quadruples))  # 更新跳转指令的目标
                    return True
        return False

    def parse(self):
        # 尝试解析声明表达式
        if not self.for_statement():
            # print(48515)
            return 0, -1
        return 1, self.subscript


class IF:
    def __init__(self, tokens, ROOT, midcode):
        self.tokens = tokens
        self.current_token = None
        self.subscript = 0
        self.max = len(tokens)
        self.midcode = midcode
        self.root = ROOT
        self.next_token()

    def next_token(self):
        self.current_token = self.tokens[self.subscript]
        self.subscript += 1
        if self.subscript > self.max - 1:
            self.subscript = self.max - 1

    def eat(self, kind):
        if self.current_token.kind in kind:
            self.next_token()
        else:
            raise Exception(f'期望的Token: {kind}, 实际的Token: {self.current_token.value, self.current_token.kind}')

    def yuju_list(self):
        control = 0
        while self.current_token.kind not in [302]:  # }
            print(f'IF语句中第{control+1}')
            control = control + 1
            # 判断到底填不填加四元式逻辑
            a1 = True
            a2 = True
            if self.midcode:
                a1 = False
                a2 = True
            else:
                a1 = False
                a2 = False
            med1 = Assignment_expression(self.tokens[self.subscript - 1:], a1)  # 赋值
            val1, sub1, fuzhi_result = med1.parse()
            if val1:
                med1 = Assignment_expression(self.tokens[self.subscript - 1:], a2)  # 赋值
                val1, sub1, fuzhi_result = med1.parse()
                for _ in range(sub1 - 1):
                    self.next_token()
                self.eat([307])  # ;
                child1 = Node("赋值表达式", parent=self.root)
                continue

            med3 = Declaration_statement(self.tokens[self.subscript - 1:], a1)
            val3, sub3 = med3.parse()
            if val3:
                med3 = Declaration_statement(self.tokens[self.subscript - 1:], a2)
                val3, sub3 = med3.parse()
                for _ in range(sub3 - 1):
                    self.next_token()
                self.eat([307])  # ;
                child1 = Node("声明表达式", parent=self.root)
                continue

            med4 = IF(self.tokens[self.subscript - 1:], Node("中间，保证运行的，不用管"), a1)
            val4, sub4 = med4.parse()
            if val4:
                child1 = Node("IF语句", parent=self.root)
                med4 = IF(self.tokens[self.subscript - 1:], child1, a2)
                _, _ = med4.parse()
                for _ in range(sub4 - 1):
                    self.next_token()
                continue

            med5 = While_statement(self.tokens[self.subscript - 1:], Node("中间，保证运行的，不用管"), a1)
            val5, sub5 = med5.parse()
            if val5:
                child1 = Node("while语句", parent=self.root)
                med5 = While_statement(self.tokens[self.subscript - 1:], child1, a2)
                _, _ = med5.parse()
                for _ in range(sub5 - 1):
                    self.next_token()
                continue

            med6 = For_statement(self.tokens[self.subscript - 1:], Node("中间，保证运行的，不用管"), a1)
            val6, sub6 = med6.parse()
            if val6:
                child1 = Node("for语句", parent=self.root)
                med6 = For_statement(self.tokens[self.subscript - 1:], child1, a2)
                _, _ = med6.parse()
                for _ in range(sub6 - 1):
                    self.next_token()
                continue

            med7 = write_expression(self.tokens[self.subscript - 1:], a1)
            val7, sub7 = med7.parse()
            if val7:

                med7 = write_expression(self.tokens[self.subscript - 1:], a2)
                _, _ = med7.parse()
                for _ in range(sub7 - 1):
                    self.next_token()
                self.eat([307])  # ;
                child1 = Node("写出语句", parent=self.root)
                continue
            val1, sub1 = 0, -1
            val2, sub2 = 0, -1
            val3, sub3 = 0, -1
            val4, sub4 = 0, -1
            val5, sub5 = 0, -1
            val6, sub6 = 0, -1
            val7, sub7 = 0, -1
        return True

    def exper(self):
        # exp -> if (布尔) {yuju} | if (布尔) {yuju} else {yuju}
        if self.current_token.kind in [116]:  # if
            self.eat([116])
            if self.current_token.kind in [303]:  # (
                self.eat([303])

                med3 = Boolean_expression(self.tokens[self.subscript - 1:], self.midcode)
                val3, sub3, buer_result = med3.parse()
                if not val3:
                    return False
                for yzz in range(sub3 - 1):
                    self.next_token()
                self.eat([304])  # ')'

                mid_jump1 = -1
                mid_jump2 = -1
                mid_jump3 = -1
                if self.midcode:
                    emit('jnz', buer_result, '_', '-1')
                    jump_quad = len(quadruples) - 1  # 记录跳转指令的位置,真就跳转出去
                    mid_jump1 = jump_quad

                    emit('jz', buer_result, '_', '-1')
                    jump_quad = len(quadruples) - 1  # 记录跳转指令的位置，跳转到真的执行的位置
                    mid_jump2 = jump_quad

                if self.current_token.kind in [301]:  # {
                    self.eat([301])
                    if self.midcode:
                        quadruples[mid_jump1] = ('jnz', buer_result, '_', len(quadruples))  # 更新跳转指令的目标
                    valid = self.yuju_list()
                    if not valid:
                        return False
                    if self.midcode:
                        emit('J', '_', '_', '-1')  # 更新跳转指令的目标
                        mid_jump3 = len(quadruples) - 1
                    self.eat([302])  # }
                    if self.current_token.kind in [110]:  # else
                        self.eat([110])
                        if self.midcode:
                            quadruples[mid_jump2] = ('jz', buer_result, '_', len(quadruples))  # 更新跳转指令的目标
                        if self.current_token.kind in [301]:  # {
                            self.eat([301])
                            valid = self.yuju_list()
                            if not valid:
                                return False
                            self.eat([302])  # }
                        if self.midcode:
                            quadruples[mid_jump3] = ('J', '_', '_', len(quadruples))  # 更新跳转指令的目标
                        return True
                    else:
                        if self.midcode:
                            quadruples[mid_jump2] = ('jz', buer_result, '_', len(quadruples))  # 更新跳转指令的目标
                            quadruples[mid_jump3] = ('J', '_', '_', len(quadruples))  # 更新跳转指令的目标
                        return True
        return False

    def parse(self):
        # 尝试解析if表达式
        if not self.exper():
            # print(48515)
            return 0, -1
        # print(48515)
        return 1, self.subscript

#write语句
class write_expression:
    def __init__(self, tokens,midcode):
        self.tokens = tokens
        self.current_token = None
        self.subscript = 0
        self.max = len(tokens)
        self.midcode=midcode
        self.next_token()
    def next_token(self):
        self.current_token = self.tokens[self.subscript]
        self.subscript += 1
        if self.subscript > self.max - 1:
            self.subscript = self.max - 1
    def eat(self, kind):
        if self.current_token.kind in kind:
            self.next_token()
        else:
            raise Exception(
                f'函数语句出错：期望的Token: {kind}, 实际的Token: {self.current_token.value, self.current_token.kind}')
    def exper(self):
        # exp -> type id (shengming){statement_list}
        if self.current_token.kind in [700] and self.tokens[self.subscript].value=='(':  # 标识符
            start_cur=self.current_token.value
            self.eat([700])  # 下一个token
            self.eat([303])# (
            while self.current_token.kind!=304:#)

                if self.current_token.kind in [700]:# 标识符
                    tmp_cur=self.current_token.value
                    if self.midcode:
                        emit('para',tmp_cur,'_','_')
                    self.eat([700])
                    continue
                self.eat([self.current_token.kind])
            self.eat([304])#)
            if self.midcode:
                new_=new_temp()
                emit('call',start_cur,'_',new_)
            return True
        return False

    def parse(self):
        # 尝试解析write语句
        if not self.exper():
            # print(48515)
            return 0, -1
        # print(48515)
        return 1, self.subscript

#函数语句
class function_expression:
    def __init__(self, tokens, ROOT,midcode):
        self.tokens = tokens
        self.current_token = None
        self.subscript = 0
        self.max = len(tokens)
        self.midcode=midcode
        self.next_token()
        self.root = ROOT
    def next_token(self):
        self.current_token = self.tokens[self.subscript]
        self.subscript += 1
        if self.subscript > self.max - 1:
            self.subscript = self.max - 1
    def eat(self, kind):
        if self.current_token.kind in kind:
            self.next_token()
        else:
            raise Exception(
                f'函数语句出错：期望的Token: {kind}, 实际的Token: {self.current_token.value, self.current_token.kind}')

    def yuju_list(self):
        control=0
        while self.current_token.kind not in [302]:  # }
            print(f'函数语句中第{control+1}')
            control=control+1
            #判断到底填不填加四元式逻辑
            a1=True
            a2=True
            if self.midcode:
                a1=False
                a2=True
            else:
                a1=False
                a2=False
            med1 = Assignment_expression(self.tokens[self.subscript - 1:],a1)  # 赋值
            val1, sub1,fuzhi_result = med1.parse()
            if val1:
                med1 = Assignment_expression(self.tokens[self.subscript - 1:],a2)  # 赋值
                val1, sub1,fuzhi_result = med1.parse()
                for _ in range(sub1 - 1):
                    self.next_token()
                self.eat([307])  # ;
                child1 = Node("赋值表达式", parent=self.root)
                continue


            med3 = Declaration_statement(self.tokens[self.subscript - 1:],a1)
            val3, sub3 = med3.parse()
            if val3:
                med3 = Declaration_statement(self.tokens[self.subscript - 1:],a2)
                val3, sub3 = med3.parse()
                for _ in range(sub3 - 1):
                    self.next_token()
                self.eat([307])  # ;
                child1 = Node("声明表达式", parent=self.root)
                continue

            med4 = IF(self.tokens[self.subscript - 1:], Node("中间，保证运行的，不用管"),a1)
            val4, sub4 = med4.parse()
            if val4:
                child1 = Node("IF语句", parent=self.root)
                med4 = IF(self.tokens[self.subscript - 1:], child1,a2)
                _, _ = med4.parse()
                for _ in range(sub4 - 1):
                    self.next_token()
                continue

            med5 = While_statement(self.tokens[self.subscript - 1:], Node("中间，保证运行的，不用管"),a1)
            val5, sub5 = med5.parse()
            if val5:
                child1 = Node("while语句", parent=self.root)
                med5 = While_statement(self.tokens[self.subscript - 1:], child1,a2)
                _, _ = med5.parse()
                for _ in range(sub5 - 1):
                    self.next_token()
                continue

            med6 = For_statement(self.tokens[self.subscript - 1:], Node("中间，保证运行的，不用管"),a1)
            val6, sub6 = med6.parse()
            if val6:
                child1 = Node("for语句", parent=self.root)
                med6 = For_statement(self.tokens[self.subscript - 1:], child1,a2)
                _, _ = med6.parse()
                for _ in range(sub6 - 1):
                    self.next_token()
                continue

            med7 = write_expression(self.tokens[self.subscript - 1:],a1)
            val7, sub7 = med7.parse()
            if val7:

                med7 = write_expression(self.tokens[self.subscript - 1:],a2)
                _, _ = med7.parse()
                for _ in range(sub7 - 1):
                    self.next_token()
                self.eat([307])  # ;
                child1 = Node("写出语句", parent=self.root)
                continue
            val1, sub1 = 0, -1
            val2, sub2 = 0, -1
            val3, sub3 = 0, -1
            val4, sub4 = 0, -1
            val5, sub5 = 0, -1
            val6, sub6 = 0, -1
            val7, sub7 = 0, -1
        return True

    def canshu_list_pie(self):
        # shengming`->, type id shengming`| 空
        # 代码逻辑：先判断每个声明，如果不等于type，就返回True（这时认定为空）
        if self.current_token.kind in [307]:  # ;
            self.eat([307])
            if self.current_token.kind in [104, 113, 118, 109]:  # char :104 float :113 int :118double :109
                self.eat([104, 113, 118, 109])  # 下一个token
                if self.current_token.kind in [700]:  # '标识符': 700
                    self.eat([700])
                    if self.canshu_list_pie:  # 进入递归
                        return True
        elif self.current_token.kind in [304]:  # )
            # print(self.current_token.value, self.current_token.kind, self.subscript)
            return True

        return False

    def canshu_list(self):
        # shengming->type id shengming`
        while self.current_token.kind not in [304]:  # )
            if self.current_token.kind in [104, 113, 118, 109]:  # char :104 float :113 int :118 double :109
                self.eat([104, 113, 118, 109])  # 下一个token
                if self.current_token.kind in [700]:  # '标识符': 700
                    self.eat([700])
                    if self.tokens[self.subscript - 1].kind in [304]:  # )
                        yzz = 0
                    else:
                        self.eat([308])  # ,
        return True

    def exper(self):
        # exp -> type id (shengming){statement_list}
        if self.current_token.kind in [104, 113, 118, 132, 109]:  # char :104 float :113 int :118 void 132 double :109
            self.eat([104, 113, 118, 132, 109])  # 下一个token
            if self.current_token.kind in [700]:  # 标识符
                func_name = self.current_token.value
                self.eat([700])
                if self.current_token.kind in [303]:  # (
                    self.eat([303])
                    valid = self.canshu_list()
                    if not valid:
                        return False
                    # print(self.current_token.value, self.current_token.kind, self.subscript)
                    self.eat([304])  # )
                    # return True
                    if self.current_token.kind in [301]:  # {
                        self.eat([301])

                        valid = self.yuju_list()
                        if not valid:
                            return False
                        self.eat([302])  # }

                        return True
        return False

    def parse(self):
        # 尝试解析函数语句
        if not self.exper():
            # print(48515)
            return 0, -1
        # print(48515)
        return 1, self.subscript


#函数声明
class funcdec_expression:
    def __init__(self, tokens,midcode):
        self.tokens = tokens
        self.current_token = None
        self.subscript = 0
        self.max = len(tokens)
        self.midcode=midcode
        self.next_token()

    def next_token(self):
        self.current_token = self.tokens[self.subscript]
        self.subscript += 1
        if self.subscript > self.max - 1:
            self.subscript = self.max - 1
    def eat(self, kind):
        if self.current_token.kind in kind:
            self.next_token()
        else:
            raise Exception(
                f'函数语句出错：期望的Token: {kind}, 实际的Token: {self.current_token.value, self.current_token.kind}')
    def canshu_list(self):
        # 这里写的函数声明中，必须有参数
        while self.current_token.kind not in [304]:  # )
            if self.current_token.kind in [104, 113, 118, 109]:  # char :104 float :113 int :118 double :109
                self.eat([104, 113, 118, 109])  # 下一个token
                if self.current_token.kind in [700]:  # '标识符': 700
                    self.eat([700])
                if self.tokens[self.subscript - 1].kind in [304]:  # )
                    yzz = 0
                    return True
                else:
                    self.eat([308])  # ,
            else:
                return False
        return False
    def exper(self):
        # exp -> type id (shengming){statement_list}
        if self.current_token.kind in [104, 113, 118, 132, 109]:  # char :104 float :113 int :118 void 132 double :109
            self.eat([104, 113, 118, 132, 109])  # 下一个token
            if self.current_token.kind in [700]: #关键字
                self.eat([700])  # 下一个token
                if self.current_token.kind in [303]:  # (
                    self.eat([303])  # 下一个token
                    valid = self.canshu_list()
                    if not valid:
                        return False
                    # print(self.current_token.value, self.current_token.kind, self.subscript)
                    self.eat([304])  # )
                    if self.current_token.value=='{':
                        return False
                    return True
        return False

    def parse(self):
        # 尝试解析函数声明语句
        if not self.exper():
            # print(48515)
            return 0, -1
        # print(48515)
        return 1, self.subscript

#总的入口
class start_expression:
    def __init__(self, tokens, ROOT,midcode):
        self.tokens = tokens
        self.current_token = None
        self.subscript = 0
        self.max = len(tokens)
        self.midcode=midcode
        self.next_token()
        self.root = ROOT
    def next_token(self):
        self.current_token = self.tokens[self.subscript]
        self.subscript += 1
        if self.subscript > self.max - 1:
            self.subscript = self.max - 1
    def eat(self, kind):
        if self.current_token.kind in kind:
            self.next_token()
        else:
            raise Exception(
                f'函数语句出错：期望的Token: {kind}, 实际的Token: {self.current_token.value, self.current_token.kind}')
    def yuju(self):
        control=0

        while self.subscript < self.max-1 :
            print(f'当前是{control+1}轮次')
            control=control+1
            # 判断到底填不填加四元式逻辑
            a1 = True
            a2 = True
            if self.midcode:
                a1 = False
                a2 = True
            else:
                a1 = False
                a2 = False
            med1 = Assignment_expression(self.tokens[self.subscript - 1:], a1)  # 赋值
            val1, sub1, fuzhi_result = med1.parse()
            if val1:
                med1 = Assignment_expression(self.tokens[self.subscript - 1:], a2)  # 赋值
                val1, sub1, fuzhi_result = med1.parse()
                for _ in range(sub1 - 1):
                    self.next_token()
                self.eat([307])  # ;
                child1 = Node("赋值表达式", parent=self.root)
                continue

            med3 = Declaration_statement(self.tokens[self.subscript - 1:], a1)
            val3, sub3 = med3.parse()
            if val3:
                med3 = Declaration_statement(self.tokens[self.subscript - 1:], a2)
                val3, sub3 = med3.parse()
                for _ in range(sub3 - 1):
                    self.next_token()
                self.eat([307])  # ;
                child1 = Node("声明表达式", parent=self.root)
                continue

            med4 = IF(self.tokens[self.subscript - 1:], Node("中间，保证运行的，不用管"), a1)
            val4, sub4 = med4.parse()
            if val4:
                child1 = Node("IF语句", parent=self.root)
                med4 = IF(self.tokens[self.subscript - 1:], child1, a2)
                _, _ = med4.parse()
                for _ in range(sub4 - 1):
                    self.next_token()
                continue

            med5 = While_statement(self.tokens[self.subscript - 1:], Node("中间，保证运行的，不用管"), a1)
            val5, sub5 = med5.parse()
            if val5:
                child1 = Node("while语句", parent=self.root)
                med5 = While_statement(self.tokens[self.subscript - 1:], child1, a2)
                _, _ = med5.parse()
                for _ in range(sub5 - 1):
                    self.next_token()
                continue

            med6 = For_statement(self.tokens[self.subscript - 1:], Node("中间，保证运行的，不用管"), a1)
            val6, sub6 = med6.parse()
            if val6:
                child1 = Node("for语句", parent=self.root)
                med6 = For_statement(self.tokens[self.subscript - 1:], child1, a2)
                _, _ = med6.parse()
                for _ in range(sub6 - 1):
                    self.next_token()
                continue

            med7 = write_expression(self.tokens[self.subscript - 1:], a1)
            val7, sub7 = med7.parse()
            if val7:
                med7 = write_expression(self.tokens[self.subscript - 1:], a2)
                _, _ = med7.parse()
                for _ in range(sub7 - 1):
                    self.next_token()
                self.eat([307])  # ;
                child1 = Node("写出语句", parent=self.root)
                continue

            med8 = funcdec_expression(self.tokens[self.subscript - 1:],  a1)#函数声明
            val8, sub8 = med8.parse()
            if val8:
                med8 = funcdec_expression(self.tokens[self.subscript - 1:], a2)
                val8, sub8 = med8.parse()
                for _ in range(sub8 - 1):
                    self.next_token()
                self.eat([307])  # ;
                child1 = Node("函数声明表达式", parent=self.root)
                continue

            med9 = function_expression(self.tokens[self.subscript - 1:], Node("中间，保证运行的，不用管"), a1)#函数语句
            val9, sub9 = med9.parse()
            if val9:
                child1 = Node("函数语句", parent=self.root)
                med9 = function_expression(self.tokens[self.subscript - 1:], child1, a2)
                _, _ = med9.parse()
                for _ in range(sub9 - 1):
                    self.next_token()
                continue
            val1, sub1 = 0, -1
            val2, sub2 = 0, -1
            val3, sub3 = 0, -1
            val4, sub4 = 0, -1
            val5, sub5 = 0, -1
            val6, sub6 = 0, -1
            val7, sub7 = 0, -1
            val8, sub8 = 0, -1
            val9, sub9 = 0, -1



    def parse(self):
        if self.midcode:
            emit('main', '_', '_', '_')  # 生成开始的中间代码
        # 尝试解析所有的tokens串
        self.yuju()
        if self.midcode:
            emit('sys', '_', '_', '_')  # 生成的中间代码

# with open(r"D:\桌面\编译原理\test.txt", 'r', encoding='utf-8') as fp:
#     text = fp.read()

def yufa_and_zhongjian(a):
    token = []
    for i in a:
        token.append(Token(i[0], i[1]))
    root = Node("开始")
    parser = start_expression(token,root, True)
    parser.parse()

    return root,quadruples
text='''

//for嵌套if,求1到给定数N以内所有奇数的和
int main()

{
  int i,N,sum = 0;
  N = read();
  for(i=1;i<=N;i=i+1)
{

     if(i%2 == 1)
	sum = sum+i;
    }

  write(sum);

}
'''

####do-while没有写
####if,while,for必须加{}号
####所有函数必须加上返回类型，即int main,,,,void adsda()
# a=lex.lex_analysis(text)
# token = []
# for i in a:
#     token.append(Token(i[0], i[1]))
# print(a)
# temp_count=0
# quadruples=[]
# parser = start_expression(token, Node("开始"),True)
# parser.parse()
# for j,quad in enumerate(quadruples):
#     print(j,quad)







