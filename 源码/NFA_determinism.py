from regulertoNFA import regex_to_nfa

# DFA状态类
class DFAState:
    _counter = 0

    def __init__(self, nfa_states):
        self.id = DFAState._counter  # 给当前状态分配一个唯一的ID
        DFAState._counter += 1

        self.nfa_states = frozenset(nfa_states)
        # 判断DFA状态是否为接受状态，如果NFA状态集合中有任何一个是接受状态，则DFA状态也是接受状态
        self.is_end = any(state.isEnd for state in nfa_states)
        self.transitions = {}

    def __hash__(self):
        return hash(self.nfa_states)

    def __eq__(self, other):
        return self.nfa_states == other.nfa_states

    def __repr__(self):
        return f"DFAState{self.id}"

# 计算epsilon闭包的函数
def epsilon_closure(states):
    stack = list(states)
    closure = set(states)
    while stack:
        state = stack.pop()
        for next_state in state.epsilonTransitions:
            if next_state not in closure:
                closure.add(next_state)
                stack.append(next_state)
    return closure

# 计算在给定符号下的转移状态集的函数
def move(states, symbol):
    transition_states = set()
    for state in states:
        if symbol in state.transition:
            transition_states.update(state.transition[symbol])
    return transition_states

# 将NFA转换为DFA的函数
def nfa_to_dfa(start_state):
    initial_closure = epsilon_closure({start_state})
    start_dfa_state = DFAState(initial_closure)
    dfa_states = {start_dfa_state: start_dfa_state}
    unmarked_states = [start_dfa_state]

    while unmarked_states:
        current_state = unmarked_states.pop()
        for symbol in ['a','b','c','d']:
            transitions = move(current_state.nfa_states, symbol)
            if len(transitions)!=0:
                closure = epsilon_closure(transitions)
                new_state = DFAState(closure)
                if new_state not in dfa_states:
                    dfa_states[new_state] = new_state
                    unmarked_states.append(new_state)
                current_state.transitions[symbol] = new_state

    return dfa_states


# # 使用正则表达式转换为NFA的函数来获取NFA的起始状态
# start_state = regex_to_nfa('a*|b.c')
#
# # 调用NFA到DFA转换函数，并传入NFA的起始状态
# dfa_states = nfa_to_dfa(start_state.start)
#
# # 打印DFA状态和转移
# for state in dfa_states.values():
#     # 构建转移函数的可读形式
#     transitions = {symbol: str(dfa_states[next_state]) for symbol, next_state in state.transitions.items()}
#     print(f"State: {state}, isEnd: {state.is_end}, Transitions: {transitions}")


