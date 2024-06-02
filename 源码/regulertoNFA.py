
# Shunting Yard 算法：将正则表达式的前置表达式转换为后缀表达式
def shunt(infix):
    specials = {'*': 50, '.': 40, '|': 30}  # 定义操作符的优先级
    pofix = ""
    stack = ""
    for c in infix:
        if c == '(':
            stack += c
        elif c == ')':
            while stack[-1] != '(':
                pofix += stack[-1]
                stack = stack[:-1]
            stack = stack[:-1]  # 弹出'('
        elif c in specials:
            while stack and specials.get(c, 0) <= specials.get(stack[-1], 0):
                pofix += stack[-1]
                stack = stack[:-1]
            stack += c
        else:
            pofix += c
    while stack:
        pofix, stack = pofix + stack[-1], stack[:-1]
    return pofix


# NFA类：表示非确定性有限自动机
class NFA:
    def __init__(self, start, end):
        self.start = start
        self.end = end


class State:
    count = 0  # 新增静态变量来跟踪状态数量

    def __init__(self, isEnd):
        self.id = State.count  # 为每个状态分配一个唯一的ID
        State.count += 1  # 更新状态计数
        self.isEnd = isEnd
        self.transition = {}  # 字符转换
        self.epsilonTransitions = []  # ε转换

    def __str__(self):
        return f"State({self.id}, isEnd={self.isEnd})"


# 给状态添加ε转换
def addEpsilonTransition(come, to):
    come.epsilonTransitions.append(to)
    # come.epsilonTransitions=to

# 给状态添加字符转换
def addTransitions(come, to, symbol):
    if symbol in come.transition:
        come.transition[symbol].append(to)
    else:
        come.transition[symbol] = [to]


# 创建ε-NFA
def fromEpsilon():
    start = State(False)
    end = State(True)
    addEpsilonTransition(start, end)
    return start, end


# 创建符号NFA
def fromSymbol(symbol):
    start = State(False)
    end = State(True)
    addTransitions(start, end, symbol)
    return start, end


# 创建字符NFA
def createNFA(symbol):
    start, end = fromSymbol(symbol)
    return NFA(start, end)

#链接两个NFA
def concat(first, second):
    addEpsilonTransition(first.end, second.start)
    first.end.isEnd = False

    return NFA(first.start, second.end)

# 创建并集NFA
def union(first, second):
    start = State(False)

    addEpsilonTransition(start, first.start)
    addEpsilonTransition(start, second.start)
    end = State(True)
    addEpsilonTransition(first.end, end)
    first.end.isEnd = False
    addEpsilonTransition(second.end, end)
    second.end.isEnd = False
    return NFA(start, end)

    # second.start=first.start
    # second.end=first.end



# 创建闭包NFA
def closure(nfa):
    start = State(False)
    end = State(True)

    addEpsilonTransition(start, end)
    addEpsilonTransition(start, nfa.start)

    addEpsilonTransition(nfa.end, end)
    addEpsilonTransition(nfa.end, nfa.start)

    nfa.end.isEnd = False

    return NFA(start, end)


# 将后缀表达式转换为NFA
def regex_to_nfa(postfix):
    if postfix == '':
        return fromEpsilon()
    pofix = shunt(postfix)
    print('后缀表达式：',pofix)
    stack = []
    for c in pofix:
        # print(c)
        if c == '.':
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            new_nfa = concat(nfa1, nfa2)
            stack.append(new_nfa)
        elif c == '|':
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            new_nfa = union(nfa1, nfa2)
            stack.append(new_nfa)
        elif c == '*':
            nfa = stack.pop()
            new_nfa = closure(nfa)
            stack.append(new_nfa)
        else:
            nfa = createNFA(c)
            stack.append(nfa)

    # #如果栈里面有多个值，就将其链接在一起
    # while len(stack)>1:
    #     nfa2 = stack.pop()
    #     nfa1 = stack.pop()
    #     new_nfa = concat(nfa1, nfa2)
    #     stack.append(new_nfa)

    return stack.pop()
# 新增函数，用于打印NFA的状态和转换
# def print_nfa(start, visited=None):
#     if visited is None:
#         visited = set()
#     if start in visited:
#         return
#     visited.add(start)
#     # print(str(start))
#     for symbol, states in start.transition.items():
#         for state in states:
#             print(f"State {start.id} --{symbol}--> State {state.id}")
#             print_nfa(state, visited)
#     for state in start.epsilonTransitions:
#         print(f"State {start.id} --ε--> State {state.id}")
#         print_nfa(state, visited)
#
# # 打印NFA
# a=regex_to_nfa('a*|b.c')
# print_nfa(a.start)

