import regulertoNFA
import NFA_determinism


def minimize_dfa(dfa_states):
    # 删除不可达状态
    def remove_unreachable_states(dfa_states):
        reachable = set()
        stack = [next(iter(dfa_states))]
        while stack:
            state = stack.pop()
            if state not in reachable:
                reachable.add(state)
                stack.extend(dfa_states[state].transitions.values())
        return {state: dfa_states[state] for state in reachable}

    # 识别等价状态
    def identify_equivalent_states(dfa_states):
        end_states = {state for state in dfa_states if state.is_end}
        non_end_states = {state for state in dfa_states if not state.is_end}
        partitions = {frozenset(end_states), frozenset(non_end_states)}


        state_to_partition = {state: (0 if state.is_end else 1) for state in dfa_states}

        while True:
            new_partitions = set()
            new_state_to_partition = {}
            new_partition_id = 0

            for partition in partitions:
                partition_transitions = {}

                for state in partition:
                    transition_pattern = tuple((symbol, state_to_partition[dfa_states[state].transitions[symbol]])
                                               for symbol in sorted(state.transitions))

                    if transition_pattern not in partition_transitions:
                        partition_transitions[transition_pattern] = {state}
                        new_state_to_partition[state] = new_partition_id
                        new_partition_id += 1
                    else:

                        partition_transitions[transition_pattern].add(state)
                        new_state_to_partition[state] = new_state_to_partition[
                            next(iter(partition_transitions[transition_pattern]))]

                new_partitions.update(frozenset(group) for group in partition_transitions.values())

            if new_partitions == partitions:
                break

            partitions = new_partitions
            state_to_partition = new_state_to_partition

        return {state: partition_id for state, partition_id in state_to_partition.items()}

    def merge_equivalent_states(res_min):
        new_dfa_states = {}

        # 更新转移函数
        for i, j in res_min.items():
            if len(j) == 1:
                # j[0].nfa_states=set()

                new_dfa_states[j[0]] = j[0]
            else:

                #修改指向自己的边
                new_dfa = NFA_determinism.DFAState(set())
                new_dfa.transitions = {}
                for med_dfa in j:  # j是一个列表
                    if med_dfa.is_end:
                        new_dfa.is_end=True
                    for key, value in med_dfa.transitions.items():
                        if value in j:
                            new_dfa.transitions[key] = new_dfa#自己到自己
                        else:
                            new_dfa.transitions[key] = value#自己到别人

                #修改别人到自己的边
                #先找还没有遍历到的
                for i2, j2 in res_min.items():
                    if j!=j2:
                        for med_dfa in j2:
                            for key, value in med_dfa.transitions.items():
                                if value in j:
                                    med_dfa.transitions[key]=new_dfa

                #再找已经遍历过得
                for i3, j3 in new_dfa_states.items():
                    for key, value in j3.transitions.items():
                        if value in j:
                            j3.transitions[key]=new_dfa
                #
                new_dfa_states[new_dfa] = new_dfa

        return new_dfa_states

    dfa_states = remove_unreachable_states(dfa_states)
    partitions = identify_equivalent_states(dfa_states)
    res_min = {}
    for i, j in partitions.items():
        if j not in res_min:
            res_min[j] = []
            res_min[j].append(i)
        else:
            res_min[j].append(i)
    minimized_dfa_states = merge_equivalent_states(res_min)
    return minimized_dfa_states



#
# nfa = regulertoNFA.regex_to_nfa('a.b*.c|d.a.b*.c')
# dfa = NFA_determinism.nfa_to_dfa(nfa.start)
# print("DFA:")
# for state in dfa.values():
#     transitions = {symbol: str(dfa[next_state]) for symbol, next_state in state.transitions.items()}
#     print(f"State: {state}, isEnd: {state.is_end}, Transitions: {transitions}")
#
# # 最小化DFA
# minimized_dfa_states = minimize_dfa(dfa)
#
# # 打印最小化后的DFA状态和转移
# print("\nMinimized DFA:")
# for state in minimized_dfa_states.values():
#     transitions = {symbol: str(minimized_dfa_states[next_state]) for symbol, next_state in state.transitions.items()}
#     print(f"State: {state}, isEnd: {state.is_end}, Transitions: {transitions}")
#
# print(454)