import lex
key = {
    'auto': 101, 'break': 102, 'case': 103, 'char': 104, 'const': 105,
    'continue': 106, 'default': 107, 'do': 108, 'double': 109, 'else': 110,
    'enum': 111, 'extern': 112, 'float': 113, 'for': 114, 'goto': 115,
    'if': 116, 'inline': 117, 'int': 118, 'long': 119, 'register': 120,
    'restrict': 121, 'return': 122, 'short': 123, 'signed': 124, 'sizeof': 125,
    'static': 126, 'struct': 127, 'switch': 128, 'typedef': 129, 'union': 130,
    'unsigned': 131, 'void': 132, 'volatile': 133, 'while': 134, 'printf': 135,
    'include': 136,'scanf':137
}
boundary = {
    '{': 301, '}': 302, '(': 303, ')': 304, '[': 305, ']': 306, ';': 307, ',': 308, ':': 309, '.': 310,
    '->': 311, '...': 312, '#': 313, '##': 314, '\'': 314, '\"': 314,'//': 317,
}
calculate = {
    '+': 401, '-': 402, '*': 403, '/': 404, '%': 405,
    '++': 406, '--': 407, '&': 408, '|': 409, '^': 410, '~': 411,
    '!': 412, '&&': 413, '||': 414, '? :': 415, '=': 416,
    '+=': 417, '-=': 418, '*=': 419, '/=': 420, '%=': 421,
    '&=': 422, '|=': 423, '^=': 424,'<': 425,'>': 426,'<=':427,'>=':428,'==':429,'!=':430
}
words = {
    '标识符': 700, '整数': 500, '浮点数': 503,'负数': 504
}
def generate_symbol_tables(tokens,hang):
    variable_table = []
    function_table = []

    i = 0
    tokens_all = tokens['all']

    current_level = 0  # 当前作用域层级
    current_hang=0
    current_scope = f'global-{current_hang}'


    while i < len(tokens_all):
        token, token_type = tokens_all[i]
        current_hang = hang[i]
        # 处理变量声明
        if token_type in key.values() and token in {'int', 'float', 'char', 'double', 'long', 'short', 'unsigned'} and (
                i + 1 < len(tokens_all) and tokens_all[i + 2][0] != '('):
            var_type = token
            i += 1
            while i < len(tokens_all) and tokens_all[i][0] != ';':
                token, token_type = tokens_all[i]
                if token_type == words.get('标识符'):
                    var_name = token
                    initial_value = None
                    i += 1
                    if i < len(tokens_all) and tokens_all[i][0] == '=':
                        i += 1
                        initial_value = tokens_all[i][0]
                        i += 1
                    variable_table.append({
                        'name': var_name,
                        'type': var_type,
                        'initial_value': initial_value,
                        'scope': f"{current_scope}:级别{current_level}"
                    })
                else:
                    i += 1
            i += 1
            continue

        # 处理函数声明
        if token_type == words.get('标识符') and (i + 1 < len(tokens_all) and tokens_all[i + 1][0] == '('):
            func_name = token
            return_type = tokens_all[i - 1][0] if i > 0 else 'int'  # 假设返回类型为int如果未指定
            i += 2  # 跳过'('
            parameters = []
            while i < len(tokens_all) and tokens_all[i][0] != ')':
                param_type = tokens_all[i][0]
                i += 1
                if i < len(tokens_all) and tokens_all[i][1] == words.get('标识符'):
                    param_name = tokens_all[i][0]
                    parameters.append(param_type)
                    i += 1
                if i < len(tokens_all) and tokens_all[i][0] == ',':
                    i += 1
            i += 1  # 跳过')'
            function_table.append({
                'name': func_name,
                'return_type': return_type,
                'num_parameters': len(parameters),
                'parameter_types': parameters
            })
            current_scope = func_name  # 设置当前作用域为函数名
            current_level = 0  # 重置作用域层级
            continue

        # 处理进入新的作用域（如 if, for, while 等）
        if token in {'if', 'for', 'while', 'do', 'else'}:
            current_level += 1

            current_scope = f'{token}+{current_hang}'

        # 处理退出作用域
        if token == '}':
            current_level -= 1
            if current_level == 0:  # 如果到达函数作用域结束，重置当前作用域为全局
                current_scope = 'global'

        i += 1

    return variable_table, function_table

def getfuhao(a):
    token = []
    hang=[]
    print(a)
    for i in a:
        token.append((i[0], i[1]))
        hang.append(i[2])

    print(token)
    tokens={}
    tokens['all']=token
    # print(tokens)
    variable_table, function_table = generate_symbol_tables(tokens,hang)
    return variable_table, function_table

if __name__ == '__main__':
    # 示例 tokens
    # tokens = {
    #     'all': [
    #         ('int', 118), ('main', 700), ('(', 303), (')', 304), ('{', 301),
    #         ('int', 118), ('a', 700), ('=', 416), ('5', 500), (';', 307),
    #         ('float', 113), ('b', 700), ('=', 416), ('3.14', 503), (';', 307),
    #         ('return', 122), ('0', 500), (';', 307),
    #         ('}', 302)
    #     ]
    # }
    # if token_type in key.values() and token in {'int', 'float', 'char', 'double', 'long', 'short', 'unsigned'} and (
    #         i + 1 < len(tokens_all) and tokens_all[i + 2][0] != '('):

    with open(r"D:\桌面\编译原理\test.txt", 'r', encoding='utf-8') as fp:
        text = fp.read()
    a=lex.lex_analysis(text)
    token = []
    hang=[]
    print(a)
    for i in a:
        token.append((i[0], i[1]))
        hang.append(i[2])

    print(token)
    tokens={}
    tokens['all']=token
    # print(tokens)
    variable_table, function_table = generate_symbol_tables(tokens,hang)
    print("Variable Symbol Table:")
    for entry in variable_table:
        print(entry)

    print("\nFunction Symbol Table:")
    for entry in function_table:
        print(entry)
