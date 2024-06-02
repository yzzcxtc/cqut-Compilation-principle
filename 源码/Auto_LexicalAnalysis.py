# -*- coding: utf-8 -*-

import ply.lex as lex
import re
# import Grammar_analysis as Gn

class auto_Lexer:
    # List of token names.   This is always required
    code = {
        'char': '101',
        'int': '102',
        'float': '103',
        'break': '104',  # 关键字
        'const': '105',
        'return': '106',
        'void': '107',
        'continue': '108',
        'do': '109',
        'while': '110',
        'if': '111',
        'else': '112',
        'for': '113',
        'double': '114',
        'enum': '115',
        'long': '116',
        'short': '117',
        'signed': '118',
        'struct': '119',
        'union': '120',
        'unsigned': '121',
        'goto': '122',
        'switch': '123',
        'case': '124',
        'default': '125',
        'auto': '126',
        'extern': '127',
        'register': '128',
        'static': '129',
        'sizeof': '130',
        'typdef': '131',
        'volatile': '132',
        '(': '201',
        ')': '202',
        '[': '203',
        ']': '204',
        '!': '205',
        '*': '206',
        '/': '207',
        '%': '208',  # 运算符
        '+': '209',
        '-': '210',
        '<': '211',
        '<=': '212',
        '>': '213',
        '>=': '214',
        '==': '215',
        '!=': '216',
        '&&': '217',
        '||': '218',
        '=': '219',
        '.': '220',  # 无识别
        '|': '221',
        '&': '222',
        '++': '223',
        '--': '224',
        '+=': '225',
        '-=': '226',
        '*=': '227',
        '/=': '228',
        '|=': '229',
        '&=': '230',
        '%=': '231',
        '>>=': '232',
        '<<=': '233',
        '>>': '234',
        '<<': '235',
        # '//': '236',  # 无识别
        # '/*': '237',  # 无识别
        # '*/': '238',  # 无识别
        ':': '239',
        '\\': '240',
        '{': '301',
        '}': '302',
        ';': '303',
        ',': '304',
        'integer': '400',  # 整数字
        'charReal': '500',  # 字符
        'string': '600',  # 字符串
        'realNumer': '800',  # 实数
        'id': '700',  # 标识符
        '#': '241'
    }  # 内码表

    basic_arithmetic_operator = [
        '+', '-', '*', '%', '/', '=', '|', '&', '>', '<', '!', '(', ')', '[', ']'
    ]  # 运算符
    delimiters = [
        ';', ',', '{', '}'
    ]  # 界符表
    esc = {'\n', '\t', ' ', '\r\n'}

    tokens = [
                 'integer',
                 'ch',
                 'str',
                 'identifier',
                 'float',
                 'error1'
             ] + list(code.values())

    errors = []

    t_ignore = ' \t'

    def t_newline(self, t):  # 行号
        r"""\n+"""
        t.lexer.lineno += len(t.value)

    def t_comment(self, t):  # 注释
        r"""(/\*(.|\n)*\*/) | (//.*)"""
        s = t.value
        n = re.findall(r"\n+", s)
        t.lexer.lineno += len(n)

    def t_error1(self, t):  # 注释无结尾
        r"""/\*(.|\n)*"""
        self.errors.append("第{}行, 注释无结尾*/错误".format(t.lexer.lineno))

    def t_ch(self, t):
        r""" (')  [^'\n]* """
        if self.data[self.lexer.lexpos] == "'":
            t.lexer.lexpos += 1
            t.type = '500'
            t.value = self.data[t.lexpos:t.lexer.lexpos]
            return t
        else:
            self.errors.append("第{}行, 字符错误".format(t.lexer.lineno))

    def t_str(self, t):
        r""" (")  [^"\n]* """
        if self.data[t.lexer.lexpos] == '"':
            t.lexer.lexpos += 1
            t.type = '600'
            t.value = self.data[t.lexpos:t.lexer.lexpos]
            return t
        else:
            self.errors.append("第{}行, 字符串错误".format(t.lexer.lineno))

    def t_identifier(self, t):  # 标识符、关键字
        r"""[a-zA-Z_][a-zA-Z_0-9]*"""
        t.type = self.code.get(t.value, '700')  # Check for reserved words
        return t

    def t_flot(self, t):
        r"""  ((0 | ([1-9][0-9]*))) (\.[0-9]+) ([Ee][+-]?[0-9]+)? """
        if t.lexer.lexpos == self.length:
            t.type = '800'
        elif self.data[t.lexer.lexpos] in self.basic_arithmetic_operator:
            t.type = '800'
            return t
        elif self.data[t.lexer.lexpos] in self.delimiters:
            t.type = '800'
            return t
        elif self.data[t.lexer.lexpos] in self.esc:
            t.type = '800'
            return t
        else:
            self.errors.append("第{}行, 数字错误".format(t.lexer.lineno))

    def t_integer(self, t):
        r""" 0 | ([1-9][0-9]*)"""
        if t.lexer.lexpos == self.length:
            t.type = '400'
        elif self.data[t.lexer.lexpos] in self.basic_arithmetic_operator:
            t.type = '400'
            return t
        elif self.data[t.lexer.lexpos] in self.delimiters:
            t.type = '400'
            return t
        elif self.data[t.lexer.lexpos] in self.esc:
            t.type = '400'
            return t
        else:
            self.errors.append("第{}行, 数字错误".format(t.lexer.lineno))

    # def t_number(self, t):
    #     r""" (0(([Xx][A-Fa-f1-9][A-Fa-f0-9]*)|([1-7][0-7]*)|(\.[0-9]+([Ee][+-]?[0-9]+)?))?)
    #     |([1-9][0-9]*(\.[0-9]+)?([Ee][+-]?[0-9]+)?)"""
    #     t.type = '1'
    #     if t.lexer.lexpos == self.length:
    #         t.type = '1'
    #         return t
    #     elif self.data[t.lexer.lexpos] in self.basic_arithmetic_operator:
    #         t.type = '1'
    #         return t
    #     elif self.data[t.lexer.lexpos] in self.delimiters:
    #         t.type = '1'
    #         return t
    #     elif self.data[t.lexer.lexpos] in self.esc:
    #         t.type = '1'
    #         return t
    #     else:
    #         self.errors.append("第{}行, 数字错误".format(t.lexer.lineno))

    def t_operator(self, t):  # 符号
        r"""(>>=) | (<<=) | (>>) | (<<) |

        (\+\+) | (--) | (\+=) | (-=) | (\*=) | (/=) | (%=)|

        (\|\|) | (&&) | (==) |

        (\|=) | (&=) | (!=) | (>=) | (<=) |

        (\+) | (-) | (\*) | (%) | (/) | (\|) | (&) | (!) | (=) | (>) | (<) |

        (\() | (\)) | (\{) | (\}) | (\[) | (\]) |

        (,) | (;) | (:) | (\\) | (\.) | (\#)"""
        t.type = self.code.get(t.value)
        return t

    def t_error(self, t):  # 非法字符
        self.errors.append("第{}行, 非法字符 {}".format(t.lexer.lineno, t.value[0]))
        t.lexer.skip(1)

    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    # Test it output
    def test(self, data):
        self.data = data
        self.length = len(data)
        self.lexer.input(data)

if __name__ == '__main__':
    d = """
        @
    """

    m = auto_Lexer()
    m.build()  # Build the lexer
    m.test(d)

    token = []
    # Tokenize
    for tok in m.lexer:
        token.append([int(tok.type), tok.value])
        print(tok)

    for i in m.errors:
        print(i)
