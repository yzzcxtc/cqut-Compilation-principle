import re

# 定义全局变量
key = {
    'auto': 101, 'break': 102, 'case': 103, 'char': 104, 'const': 105,
    'continue': 106, 'default': 107, 'do': 108, 'double': 109, 'else': 110,
    'enum': 111, 'extern': 112, 'float': 113, 'for': 114, 'goto': 115,
    'if': 116, 'inline': 117, 'int': 118, 'long': 119, 'register': 120,
    'restrict': 121, 'return': 122, 'short': 123, 'signed': 124, 'sizeof': 125,
    'static': 126, 'struct': 127, 'switch': 128, 'typedef': 129, 'union': 130,
    'unsigned': 131, 'void': 132, 'volatile': 133, 'while': 134, 'printf': 135,
    'include': 136, 'scanf': 137
}
boundary = {
    '{': 301, '}': 302, '(': 303, ')': 304, '[': 305, ']': 306, ';': 307, ',': 308, ':': 309, '.': 310,
    '->': 311, '...': 312, '#': 313, '##': 314, '\'': 314, '\"': 314, '//': 317,
}
calculate = {
    '+': 401, '-': 402, '*': 403, '/': 404, '%': 405,
    '++': 406, '--': 407, '&': 408, '|': 409, '^': 410, '~': 411,
    '!': 412, '&&': 413, '||': 414, '? :': 415, '=': 416,
    '+=': 417, '-=': 418, '*=': 419, '/=': 420, '%=': 421,
    '&=': 422, '|=': 423, '^=': 424, '<': 425, '>': 426, '<=': 427, '>=': 428, '==': 429, '!=': 430
}
words = {
    '标识符': 700, '整数': 500, '浮点数': 503, '负数': 504
}

def re_id(txt, i, LineNo, keyword, idword, finall):
    end = i
    while end < len(txt) and (txt[end].isalpha() or txt[end].isdigit() or txt[end] == '_'):
        end += 1
    arr = txt[i:end]
    if arr in key:
        keyword.append((arr, key[arr], LineNo))
        finall.append((arr, key[arr], LineNo))
    else:
        idword.append((arr, words.get('标识符'), LineNo))
        finall.append((arr, words.get('标识符'), LineNo))
    return arr

def redi(txt, i, LineNo, float_, number, finall):
    end = i
    while end < len(txt) and (txt[end].isdigit() or txt[end] == '.'):
        end += 1
    arr = txt[i:end]
    if not arr:
        return ''
    elif '.' in arr:
        float_.append((arr, words.get('浮点数'), LineNo))
        finall.append((arr, words.get('浮点数'), LineNo))
    else:
        number.append((arr, words.get('整数'), LineNo))
        finall.append((arr, words.get('整数'), LineNo))
    return arr

# 主要的词法分析函数
def lex_analysis(text):
    keyword = []
    idword = []
    number = []
    bound = []
    cal = []
    float_ = []

    finall = []
    deal_txt = re.sub(r'//.*|/\*[\s\S]*?\*/', '', text)

    LineNo = 1
    i = 0
    while i < len(deal_txt):
        if deal_txt[i] in ' \t\n':
            if deal_txt[i] == '\n':
                LineNo += 1
            i += 1
            continue
        if deal_txt[i] in boundary:
            bound.append((deal_txt[i], boundary[deal_txt[i]], LineNo))
            finall.append((deal_txt[i], boundary[deal_txt[i]], LineNo))
            i += 1
            continue
        if deal_txt[i] in calculate:
            arr = deal_txt[i:i+2] if deal_txt[i:i+2] in calculate else deal_txt[i]
            cal.append((arr, calculate.get(arr), LineNo))
            finall.append((arr, calculate.get(arr), LineNo))
            i += len(arr)
            continue
        if deal_txt[i].isalpha() or deal_txt[i] == '_':
            identifier = re_id(deal_txt, i, LineNo, keyword, idword, finall)
            i += len(identifier)
            continue
        if deal_txt[i].isdigit() or (deal_txt[i] == '-' and i + 1 < len(deal_txt) and deal_txt[i + 1].isdigit()):
            if deal_txt[i] == '-':
                cal.append((deal_txt[i], calculate.get(deal_txt[i]), LineNo))
                finall.append((deal_txt[i], calculate.get(deal_txt[i]), LineNo))
                i += 1
            dig = redi(deal_txt, i, LineNo, float_, number, finall)
            i += len(dig)
            continue
    return finall

if __name__ == '__main__':
    # 测试代码
    with open(r"D:\桌面\编译原理\test.txt", 'r', encoding='utf-8') as fp:
        text = fp.read()
    print(lex_analysis(text))
    finall=lex_analysis(text)
    formatted_string = ''
    for lst in finall:
        formatted_string += f'{lst[0]}   {lst[1]}   {lst[2]}\n'
    print(formatted_string)
