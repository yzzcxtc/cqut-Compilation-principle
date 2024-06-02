from Auto_LexicalAnalysis import auto_Lexer
index = 0  # token串的下标
error = 0  # 分析的错误个数
wrong = []  # 错误
token = []  # token串
NXQ = 0  # 指针
four_formula = []  # 四元式
nti = 1  # 临时变量的下标
variate_na = []
variate_di = {}
scope = [0]
scope1 = [0]
R_operator = [">", "<", ">=", "<=", "==", "!="]  # 关系运算符
V_type = ["int", "float", "char"]  # 变量类型
C_type = ["int", "float", "char"]  # 常量类型
F_type = ["int", "float", "char", "void"]  # 函数类型
func_call_stack = []
infer = []  # 推导所用产生式


def gencode(op, v1, v2, vr):
    global four_formula, NXQ
    four_formula.append([op, v1, v2, vr])
    NXQ += 1


# 产生新的临时变量
def newtemp():
    global nti
    nt = 'T' + str(nti)
    nti += 1
    return nt


# 算术表达式
def A():
    print("A->E A1")
    infer.append("A->E A1")
    v1 = E()
    v2 = None
    vr = None
    if token[index][1] in ["+", "-"]:
        op = token[index][1]
        v2 = A1()
        vr = newtemp()
        gencode(op, v1, v2, vr)
    else:
        print("A1→null")
        infer.append("A1→null")
    if v2 is None:
        vr = v1
    return vr


def A1():
    global index, token, error
    index += 1
    print("A1->+ E A1|- E A1 ")
    v1 = E()
    v2 = None
    vr = None
    if token[index][1] in ["+", "-"]:
        op = token[index][1]
        v2 = A1()
        vr = newtemp()
        gencode(op, v1, v2, vr)
    else:
        print("A1→null")
        infer.append("A1→null")
    if v2 is None:
        vr = v1
    return vr


# 项
def E():
    print("E->F E1")
    infer.append("E->F E1")
    v1 = F()
    v2 = None
    vr = None
    if token[index][1] in ["*", "/", "%"]:
        op = token[index][1]
        v2 = E1()
        vr = newtemp()
        gencode(op, v1, v2, vr)
    if v2 is None:
        vr = v1
    return vr


def E1():
    global index, token, error
    index += 1
    v1 = F()
    v2 = None
    vr = None
    if token[index][1] in ["*", "/", "%"]:
        print("E1→* F E1 | / F E1 | % F E1")
        infer.append("E1→* F E1 | / F E1 | % F E1")
        op = token[index][1]
        v2 = E1()
        vr = newtemp()
        gencode(op, v1, v2, vr)
    else:
        print("E1→F")
        infer.append("E1→F")
    if v2 is None:
        vr = v1
    return vr


# 因子
def F():
    global index, token, error, wrong
    vr = None
    if token[index][1] == "(":
        index += 1
        print("<因子>->(<算术表达式>)") #文法定义
        infer.append("<因子>->(<算术表达式>)")
        vr = A()  # （算术表达式）
        if token[index][1] == ")":
            index += 1
        else:
            error += 1
    elif token[index][0] in [400, 500, 600, 800]:  # 常量
        print("<因子>-><常量>")
        infer.append("<因子>-><常量>")
        vr = token[index][1]
        index += 1
    elif token[index][0] == 700:  # 函数调用
        ide = token[index][1]
        index += 1
        print("<因子>-><函数调用>")
        infer.append("<因子>-><函数调用>")
        vr = H(ide)  # 函数调用
    else:
        error += 1
        wrong.append("ERROR! 缺少算术表达式因子")
    return vr


# 函数调用
def H(ide):
    global index, token, error
    id = token[index - 1][1]
    if token[index][1] == "(":
        if id not in variate_na:
            error += 1
            wrong.append("ERROR! 函数" + id + "未声明")
        index += 1
        print("<函数调用>→<标识符>(<实参列表>)")
        infer.append("<函数调用>→<标识符>(<实参列表>)")
        J()
        if token[index][1] == ")":
            index += 1
        else:
            error += 1
            wrong.append("ERROR! 函调调用缺少)")
        return newtemp()
    else:
        print("H→null")
        if id not in variate_na:
            error += 1
            wrong.append("ERROR! 变量" + id + "未声明定义")
        return ide


#  实参列表
def J():
    global index, token, error, func_call_stack
    if (token[index][1] in ["(", "!"]) or (token[index][0] in [400, 500, 600, 700, 800]):
        print("<实参列表>→<实参>")
        infer.append("<实参列表>→<实参>")
        pa = K()
        gencode("para", pa, "", "")
    else:
        print("<实参列表>→null")
        infer.append("<实参列表>→null")


# 实参
def K():
    global index, token, error, func_call_stack
    vr = expression()
    if token[index][1] == ",":
        index += 1
        print("<实参>→<表达式>,<实参>")
        infer.append("<实参>→<表达式>,<实参>")
        pa = K()
        gencode("para", pa, "", "")
    else:
        print("<实参>→<表达式>")
        infer.append("<实参>→<表达式>")
    return vr


# 关系表达式
def B():
    print("B->ALA")
    infer.append("B->ALA")
    A()
    L()
    A()


def L():
    global index, token, error
    vr = None
    print("关系运算符：L→>|<|>=|<=|==|!=")
    infer.append("关系运算符：L→>|<|>=|<=|==|!=")
    if token[index][1] in R_operator:
        vr = token[index][1]
        index += 1
    else:
        error += 1
        wrong.append("ERROR! 缺少关系运算符")
    return vr


def C():  # bool表达式
    print("C→M C1")
    infer.append("C→M C1")
    v1 = M()
    v2 = None
    vr = None
    if token[index][1] == "||":
        op = token[index][1]
        v2 = C1()
        vr = newtemp()
        gencode(op, v1, v2, vr)
    else:
        print("C1→null")
        infer.append("C1→null")
    if v2 is None:
        vr = v1
    return vr


def C1():
    global index, token, error
    index += 1
    print("C1→|| MC1")
    infer.append("C1→|| MC1")
    v1 = M()
    v2 = None
    vr = None
    if token[index][1] == "||":
        op = token[index][1]
        v2 = C1()
        vr = newtemp()
        gencode(op, v1, v2, vr)
    else:
        print("C1→null")
        infer.append("C1→null")
    if v2 is None:
        vr = v1
    return vr


def M():
    print("M→N M1")
    infer.append("M→N M1")
    v1 = N()
    v2 = None
    vr = None
    if token[index][1] == "&&":
        op = token[index][1]
        v2 = M1()
        vr = newtemp()
        gencode(op, v1, v2, vr)
    else:
        print("M1→null")
        infer.append("M1→null")
    if v2 is None:
        vr = v1
    return vr


def M1():
    global index, token, error
    index += 1
    print("M1→&& N M1")
    infer.append("M1→&& N M1")
    v1 = N()
    v2 = None
    vr = None
    if token[index][1] == "&&":
        op = token[index][1]
        v2 = M1()
        vr = newtemp()
        gencode(op, v1, v2, vr)
    else:
        print("M1→null")
        infer.append("M1→null")
    if v2 is None:
        vr = v1
    return vr


def N():
    global index, token, error
    vr = None
    if token[index][1] == "!":
        op = token[index][1]
        index += 1
        print("布尔因子：N→!C")
        infer.append("布尔因子：N→!C")
        v1 = C()
        vr = newtemp()
        gencode(op, v1, "", vr)
    elif (token[index][0] in [400, 500, 600, 700, 800]) or (token[index][1] == "("):
        print("布尔因子：N→A O")
        infer.append("布尔因子：N→A O")
        v1 = A()
        if token[index][1] in R_operator:
            op = token[index][1]
            v2 = O()
            vr = newtemp()
            gencode(op, v1, v2, vr)
        else:
            vr = v1
    else:
        error += 1
        print("ERROR! ")
    return vr


def O():
    global index, token, error
    vr = None
    if token[index][1] in R_operator:
        print("O→L A")
        infer.append("O→L A")
        L()
        vr = A()
    else:
        print("O→null")
        infer.append("O→null")
    return vr


def P():
    global index, token, error
    v1 = None
    v2 = None
    vr = None
    if token[index][1] == "&&":
        print("P→M1 C1")
        infer.append("P→M1 C1")
        v1 = M1()
    else:
        print("P->null")
        infer.append("P->null")
    if token[index][1] == "||":
        if v1 is None:
            v1 = C1()
        else:
            v2 = C1()
            vr = newtemp()
            gencode("||", v1, v2, vr)
    if v2 is None:
        vr = v1
    return vr


def Q(ide):
    global index, token, error
    v1 = None
    vr = None
    if token[index][1] in ["(", "*", "/", "%", "+", "-", "||", "&&"] or token[index][1] in R_operator:
        print("Q→H E1 A1 O P")
        infer.append("Q→H E1 A1 O P")
        if token[index][1] == "(":
            vr = H(ide)  # 函数调用
            gencode("call", ide, "", vr)
            v1 = vr
        if token[index][1] in ["*", "/", "%"]:
            op = token[index][1]
            if v1 is None:
                v1 = ide
            v2 = E1()
            vr = newtemp()
            gencode(op, v1, v2, vr)
            v1 = vr
        if token[index][1] in ["+", "-"]:
            op = token[index][1]
            if v1 is None:
                v1 = ide
            v2 = A1()
            vr = newtemp()
            gencode(op, v1, v2, vr)
            v1 = vr
        if token[index][1] in R_operator:
            op = token[index][1]
            if v1 is None:
                v1 = ide
            v2 = O()
            vr = newtemp()
            gencode(op, v1, v2, vr)
            v1 = vr
        if token[index][1] in ["||", "&&"]:
            op = token[index][1]
            if v1 is None:
                v1 = ide
            v2 = P()
            vr = newtemp()
            gencode(op, v1, v2, vr)
            v1 = vr
        if v1 is None:
            vr = ide
    elif token[index][1] == "=":  # 赋值表达式
        index += 1
        print("Q→= EX")
        infer.append("Q→= EX")
        vr = expression()
        gencode("=", vr, "", ide)
    return vr


# 赋值表达式
def D():
    global index, token, error
    if token[index][0] == 700:
        index += 1
        if token[index][1] == "=":
            index += 1
            print("赋值表达式：D→id = EX")
            infer.append("赋值表达式：D→id = EX")
            expression()
        else:
            error += 1
            print("ERROR!")
            wrong.append("ERROR! 赋值表达式错误")
    else:
        error += 1
        print("ERROR! 赋值表达式错误")
        wrong.append("ERROR! 赋值表达式")


# 表达式
def expression():
    global index, token, error
    op = None
    v2 = None
    vr = None
    if token[index][1] == "(":
        index += 1
        print("EX→(A) E1 A1 O P")
        infer.append("EX→(A) E1 A1 O P")
        v1 = A()
        if token[index][1] == ")":
            index += 1
        else:
            error += 1
            wrong.append("ERROR! 算术表达式后缺少)")
        if token[index][1] in ["*", "/", "%"]:
            op = token[index][1]
            v2 = E1()
            vr = newtemp()
            gencode(op, v1, v2, vr)
            v1 = vr
        if token[index][1] in ["+", "-"]:
            op = token[index][1]
            v2 = A1()
            vr = newtemp()
            gencode(op, v1, v2, vr)
            v1 = vr
        if token[index][1] in R_operator:
            op = token[index][1]
            v2 = O()
            vr = newtemp()
            gencode(op, v1, v2, vr)
            v1 = vr
        if token[index][1] in ["||", "&&"]:
            op = token[index][1]
            v2 = P()
            vr = newtemp()
            gencode(op, v1, v2, vr)
            v1 = vr
        if v2 is None:
            vr = v1
    elif token[index][0] in [400, 500, 600, 800]:
        print("EX→G E1 A1 O P")
        infer.append("EX→G E1 A1 O P")
        v1 = token[index][1]
        index += 1
        print("常量：G→字符型常量 | 数值型常量")
        infer.append("常量：G→字符型常量 | 数值型常量")
        if token[index][1] in ["*", "/", "%"]:
            op = token[index][1]
            v2 = E1()
            vr = newtemp()
            gencode(op, v1, v2, vr)
            v1 = vr
        if token[index][1] in ["+", "-"]:
            op = token[index][1]
            v2 = A1()
            vr = newtemp()
            gencode(op, v1, v2, vr)
            v1 = vr
        if token[index][1] in R_operator:
            op = token[index][1]
            v2 = O()
            vr = newtemp()
            gencode(op, v1, v2, vr)
            v1 = vr
        if token[index][1] in ["||", "&&"]:
            op = token[index][1]
            v2 = P()
            vr = newtemp()
            gencode(op, v1, v2, vr)
            v1 = vr
        if v2 is None:
            vr = v1
    elif token[index][1] == "!":
        print("EX→! C M1 C1")
        infer.append("EX→! C M1 C1")
        index += 1
        v1 = C()
        vr = newtemp()
        gencode(op, v1, '', vr)
        if token[index][1] == "&&":
            op = token[index][1]
            v2 = M1()
            vr = newtemp()
            gencode(op, v1, v2, vr)
            v1 = vr
        if token[index][1] == "||":
            op = token[index][1]
            v2 = C1()
            vr = newtemp()
            gencode(op, v1, v2, vr)
            v1 = vr
        if v2 is None:
            vr = v1
    elif token[index][0] == 700:
        print("EX→id Q")
        infer.append("EX→id Q")
        ide = token[index][1]
        index += 1
        if token[index][1] in ["(", "*", "/", "%", "+", "-", "||", "&&", "="] or token[index][1] in R_operator:
            vr = Q(ide)  # 函数返回值
        else:
            vr = ide
    else:
        error += 1
        wrong.append("ERROR! 表达式缺少符号")
    return vr


# 声明语句
def declaration_statement():
    global index, token, error, variate_na, variate_di, scope
    if token[index][1] == "const":
        print("声明语句->常量声明")
        infer.append("声明语句->常量声明")
        constant_declaration()
    elif token[index][1] in F_type:
        ty = token[index][1]
        id = None
        index += 1
        if token[index][0] == 700:  #标识符
            id = token[index][1]
            if id in variate_di.keys():
                wrong.append("WARNING! 变量" + id + "重复声明")
                variate_na.pop()
            index += 1
        else:
            error += 1
            wrong.append("ERROR! 函数类型或变量常量声明后无名称")
        if token[index][1] == "(":
            print("声明语句->函数声明")
            infer.append("声明语句->函数声明")

            variate_na.append(id)
            variate_di[id] = {}
            variate_di[id]["type"] = ty
            para_list = function_declaration()  # 函数声明
            variate_di[id]["parameter"] = para_list
        elif token[index][1] in [",", "=", ";"]:
            if ty == "void":
                error += 1
                wrong.append("ERROR! 变量" + id + "类型为void")
            else:
                print("声明语句->变量声明")
                infer.append("声明语句->变量声明")
                variate_na.append(id)
                variate_di[id] = {}
                variate_di[id]["type"] = ty
                variate_di[id]["scope"] = scope
                variable_declaration_table1(id, ty)  # 变量声明
        else:
            error += 1
            wrong.append("ERROR! 标识符后无符号")
    print("声明语句->声明表")
    infer.append("声明语句->声明表")
    declaraton_table()


# 声明表
def declaraton_table():
    global index, token, error
    if (token[index][1] == "const") or token[index][1] in F_type:
        print("声明表->声明语句")
        infer.append("声明表->声明语句")
        declaration_statement()
    else:
        print("声明表->null")
        infer.append("声明表->null")


# 常量声明
def constant_declaration():
    global index, token, error
    consttype = None
    if token[index][1] == "const":
        print("<常量声明>->const<常量类型><常量声明表>")
        infer.append("<常量声明>->const<常量类型><常量声明表>")
        index += 1
        if token[index][1] in C_type:
            consttype = token[index][1]
            index += 1
            print("<常量类型>->int|char|float")
            infer.append("<常量类型>->int|char|float")
        else:
            error += 1
            wrong.append("ERROR! 缺少常量类型")
        constant_declaration_table(consttype)


# 常量声明表
def constant_declaration_table(consttype):
    global index, token, error, variate_na, variate_di, scope
    id = None
    if token[index][0] == 700:
        id = token[index][1]
        if id in variate_di.keys():
            wrong.append("WARNING! 常量" + id + "已经存在")
            variate_na.pop()
        index += 1
    else:
        error += 1
        wrong.append("ERROR! 缺少常量名称")
    if token[index][1] == "=":
        index += 1
    else:
        error += 1
        wrong.append("ERROR! 缺少=")
    if token[index][0] in [400, 500, 600, 800]:
        gencode("=", token[index][0], "", id)
        if consttype == "int":
            ct = "integer"
        elif consttype == "char":
            ct = "ch"
        else:
            ct = consttype
        if main.identifier[ct] == token[index][0]:
            val = token[index][1]
            variate_na.append(id)
            variate_di[id] = {}
            variate_di[id]["type"] = consttype
            variate_di[id]["scope"] = scope
            variate_di[id]["val"] = int(val) if consttype == 'int' else val
        else:
            wrong.append("ERROR! 常量值与声明类型不符！")
        index += 1
    else:
        error += 1
        wrong.append("ERROR! 缺少常量")
    if token[index][1] == ";":
        index += 1
        print("<常量声明表>-><标识符>=<常量>;")
        infer.append("<常量声明表>-><标识符>=<常量>;")
    elif token[index][1] == ",":
        index += 1
        print("<常量声明表>-><标识符>=<常量>,<常量声明表>")
        infer.append("<常量声明表>-><标识符>=<常量>,<常量声明表>")
        constant_declaration_table(consttype)
    else:
        error += 1
        wrong.append("ERROR! 缺少；或，")


# 变量声明表 不全
def variable_declaration_table1(id, ty):
    global index, token, error
    if token[index][1] == ";":
        index += 1
    elif token[index][1] == ",":
        index += 1
        variable_declaration_table(ty)
    elif token[index][1] == "=":
        index += 1
        vr = expression()
        gencode("=", vr, "", id)
        if token[index][1] == ";":
            index += 1
        elif token[index][1] == ",":
            index += 1
            variable_declaration_table(ty)
        else:
            error += 1
            wrong.append("ERROR! 缺少；或，")


# 变量声明表
def variable_declaration_table(ty):
    global index, token, error
    single_variable_declaration(ty)
    if token[index][1] == ";":
        index += 1
        print("<变量声明表>-><单变量声明>;")
        infer.append("<变量声明表>-><单变量声明>;")
    elif token[index][1] == ",":
        index += 1
        print("<变量声明表>-><单变量声明>,<变量声明表>")
        infer.append("<变量声明表>-><单变量声明>,<变量声明表>")
        variable_declaration_table(ty)
    else:
        error += 1
        wrong.append("ERROR! 缺少；或，")


# 单变量声明
def single_variable_declaration(ty):
    global index, token, error
    if token[index][0] == 700:
        id = token[index][1]
        variate_na.append(token[index][1])
        variate_di[token[index][1]] = {}
        variate_di[token[index][1]]["type"] = ty
        variate_di[token[index][1]]["scope"] = scope
        index += 1
    else:
        error += 1
        wrong.append("ERROR! 缺少变量名称")
    if token[index][1] == "=":
        index += 1
        print("<单变量声明>→<变量>=<表达式>")
        infer.append("<单变量声明>→<变量>=<表达式>")
        print("<变量>→<标识符>")
        infer.append("<变量>→<标识符>")
        vr = expression()
        gencode("=", vr, "", id)
    else:
        print("<单变量声明>→<变量>")
        infer.append("<单变量声明>→<变量>")
        print("<变量>→<标识符>")
        infer.append("<变量>→<标识符>")


# 函数声明
def function_declaration():
    global index, token, error
    para_list = []
    index += 1
    print("<函数声明>→<函数类型><标识符>(<函数声明形参列表>);")
    infer.append("<函数声明>→<函数类型><标识符>(<函数声明形参列表>);")
    print("<函数类型>→int|char|float|void")
    infer.append("<函数类型>→int|char|float|void")
    function_declaration_formal_parameter_list(para_list)
    if token[index][1] == ")":
        index += 1
    else:
        error += 1
        wrong.append("ERROR! 函数声明函数名后缺少)")
    if token[index][1] == ";":
        index += 1
    else:
        error += 1
        wrong.append("ERROR! 函数声明末尾缺少;")
    return para_list


# 函数声明形参
def function_declaration_formal_parameter(para_list):
    global index, token, error
    para_list.append(token[index][1])
    index += 1
    if token[index][1] == ",":
        index += 1
        print("<函数声明形参>-><变量类型>,<函数声明形参>")
        infer.append("<函数声明形参>-><变量类型>,<函数声明形参>")
        function_declaration_formal_parameter(para_list)
    else:
        print("<函数声明形参>-><变量类型>")
        infer.append("<函数声明形参>-><变量类型>")


# 函数声明形参列表
def function_declaration_formal_parameter_list(para_list):
    global index, token, error
    if token[index][1] in F_type:
        print("<函数声明形参列表>-><函数声明形参>")
        infer.append("<函数声明形参列表>-><函数声明形参>")
        function_declaration_formal_parameter(para_list)
    else:
        print("<函数声明形参列表>->null")
        infer.append("<函数声明形参列表>->null")


# 复合语句
def compound_statement():
    global index, token, error
    if token[index][1] == "{":
        index += 1
    else:
        error += 1
        wrong.append("ERROR! 函数块缺少{ ")
    print("<复合语句>→{<语句表>}")
    infer.append("<复合语句>→{<语句表>}")
    statement_table()
    if token[index][1] == "}":
        index += 1
    else:
        error += 1
        wrong.append("ERROR! 函数块末尾缺少}")


# 执行语句
def execution_statement():
    global index, token, error
    if token[index][0] == 700:
        print("<执行语句>-><数据处理语句>")
        infer.append("<执行语句>-><数据处理语句>")
        data_processing_statement()
    elif token[index][1] in ["if", "for", "while", "do", "return"]:
        print("<执行语句>-><控制语句>")
        infer.append("<执行语句>-><控制语句>")
        control_statement()
    elif token[index][1] == "{":
        print("<执行语句>-><复合语句>")
        infer.append("<执行语句>-><复合语句>")
        compound_statement()
    else:
        error += 1
        wrong.append("ERROR! 缺少执行语句")


# 数据处理语句
def data_processing_statement():
    global index, token, error
    id = token[index][1]
    index += 1
    if token[index][1] == "=":
        if id not in variate_na:
            error += 1
            wrong.append("ERROR! 变量" + id + "未声明定义")
        print("<数据处理语句>-><赋值语句>")
        infer.append("<数据处理语句>-><赋值语句>")
        assignment_statement(id)
    elif token[index][1] == "(":
        if id not in variate_na:
            error += 1
            wrong.append("ERROR! 函数" + id + "未声明")
        print("<数据处理语句>-><函数调用语句>")
        infer.append("<数据处理语句>-><函数调用语句>")
        vr = function_call_statement()
        gencode("call", id, "", vr)


# 赋值语句
def assignment_statement(id):
    global index, token, error
    index += 1
    print("<赋值语句>→<赋值表达式>;")
    infer.append("<赋值语句>→<赋值表达式>;")
    v1 = expression()
    gencode("=", v1, " ", id)
    if token[index][1] == ";":
        index += 1
    else:
        error += 1
        wrong.append("ERROR! 赋值语句后缺少;")


# 函数调用语句
def function_call_statement():
    global index, token, error, func_call_stack
    index += 1
    print("<函数调用语句>→<函数调用>;")
    infer.append("<函数调用语句>→<函数调用>;")
    J()
    if func_call_stack != []:
        gencode("para", func_call_stack.pop(), "", "")
    if token[index][1] == ")":
        index += 1
    else:
        error += 1
        wrong.append("ERROR! 函数调用函数函数名后缺少)")
    if token[index][1] == ";":
        index += 1
    else:
        error += 1
        wrong.append("ERROR! 函数调用末尾缺少;")
    return newtemp()


# 控制语句
def control_statement():
    global index, token, error
    if token[index][1] == "if":
        print("<控制语句>→<if语句>")
        infer.append("<控制语句>→<if语句>")
        if_statement_for_loop()
    elif token[index][1] == "for":
        print("<控制语句>→<for语句>")
        infer.append("<控制语句>→<for语句>")
        for_statement()
    elif token[index][1] == "while":
        print("<控制语句>→<while语句>")
        infer.append("<控制语句>→<while语句>")
        while_statement()
    elif token[index][1] == "do":
        print("<控制语句>→<do while语句>")
        infer.append("<控制语句>→<do while语句>")
        do_while_statement()
    elif token[index][1] == "return":
        print("<控制语句>→<return语句>")
        infer.append("<控制语句>→<return语句>")
        return_statement()


# 语句
def statement():
    global index, token, error
    if token[index][1] == "const" or token[index][1] in F_type:
        print("<语句>→<声明语句>")
        infer.append("<语句>→<声明语句>")
        declaration_statement()
    elif (token[index][0] == 700) or (token[index][1] in ["{", "for", "if", "while", "do", "return"]):
        print("<语句>→<执行语句>")
        infer.append("<语句>→<执行语句>")
        execution_statement()
    else:
        error += 1
        wrong.append("ERROR! 缺少语句")


# 语句表
def statement_table():
    global index, token, error
    print("<语句表>→<语句> | <语句><语句表>")
    infer.append("<语句表>→<语句> | <语句><语句表>")
    statement()
    if ((token[index][1] in ["const", "{", "if", "for", "while", "do", "return"]) or (token[index][1] in F_type) or (
            token[index][0] == 700)):
        statement_table()


def backpatch(P, t):
    global four_formula, NXQ
    Q = P
    while Q != 0:
        m = four_formula[Q][3]
        if m == 0:
            four_formula[Q][3] = t
        Q = m
        if type(Q) != int:
            break


def merge(p1, p2):
    global four_formula
    if p2 == 0:
        return p1
    else:
        p = p2
        while four_formula[p][3] != 0:
            p = four_formula[p][3]
            if type(p) != int:
                break
        four_formula[p][3] = p1
        return p2


def BE():  # 布尔表达式
    global index, token, error, NXQ
    betc, befc = BT()
    fc = befc
    while token[index][1] == "||":
        backpatch(fc, NXQ)
        index += 1
        bttc, btfc = BT()
        fc = befc
        betc = merge(betc, bttc)
    return betc, befc


def BT():
    global index, token, error, NXQ
    bttc, btfc = BF()
    tc = bttc
    while token[index][1] == "&&":
        backpatch(tc, NXQ)
        index += 1
        bftc, bffc = BF()
        tc = bftc
        btfc = merge(btfc, bffc)
    return bttc, btfc


def BF():
    global index, token, error, NXQ
    if token[index][1] == "!":
        index += 1
        bffc, bftc = BE()
    elif token[index][1] == "(":
        index += 1
        bftc, bffc = BE()
        if token[index][1] == ")":
            index += 1
        else:
            error += 1
            wrong.append("ERROR! 布尔因子后缺少)")
    else:
        i1 = A()
        if token[index][1] in R_operator:
            op = token[index][1]
            index += 1
            i2 = A()
            bftc = NXQ
            bffc = NXQ + 1
            gencode("j" + op, i1, i2, 0)
        else:
            bftc = NXQ
            bffc = NXQ + 1
            gencode("jnz", i1, "", 0)
        gencode("j", "", "", 0)
    return bftc, bffc


# if语句
def if_statement():
    global index, token, error
    print("<if语句>→if(<布尔表达式>)<语句> | if(<布尔表达式>)<语句>else<语句>")
    infer.append("<if语句>→if(<布尔表达式>)<语句> | if(<布尔表达式>)<语句>else<语句>")
    index += 1
    if token[index][1] == "(":
        index += 1
    else:
        error += 1
        wrong.append("ERROR! if语句if后缺少(")
    tc, fc = BE()
    print(tc, fc)
    if token[index][1] == ")":
        index += 1
    else:
        error += 1
        wrong.append("ERROR! if语句表达式后缺少)")
    statement()
    if token[index][1] == "else":
        index += 1
        statement()


# for语句
def for_statement():
    global index, token, error, NXQ
    index += 1
    if token[index][1] == "(":
        index += 1
    else:
        error += 1
        wrong.append("ERROR! for语句for后缺少(")
    print("<for语句>→for (<表达式>;<布尔表达式>;<表达式>)<循环语句>")
    infer.append("<for语句>→for (<表达式>;<布尔表达式>;<表达式>)<循环语句>")
    expression()
    if token[index][1] == ";":
        index += 1
    else:
        error += 1
        wrong.append("ERROR! 缺少;")
    e2 = NXQ
    tc, fc = BE()
    if token[index][1] == ";":
        index += 1
    else:
        error += 1
        wrong.append("ERROR! 缺少;")
    e3 = NXQ
    expression()
    gencode("j", "", "", e2)
    if token[index][1] == ")":
        index += 1
    else:
        error += 1
        wrong.append("ERROR! for语句表达式后缺少)")
    backpatch(tc, NXQ)
    loop_statement()
    gencode("j", "", "", e3)
    backpatch(fc, NXQ)


# while语句
def while_statement():
    global index, token, error
    index += 1
    if token[index][1] == "(":
        index += 1
    else:
        error += 1
        wrong.append("ERROR! while语句while后缺少(")
    print("<while语句>→while(<布尔表达式>)<循环语句>")
    infer.append("<while语句>→while(<布尔表达式>)<循环语句>")
    q = NXQ
    tc, fc = BE()
    if token[index][1] == ")":
        index += 1
    else:
        error += 1
        wrong.append("ERROR! while语句表达式后缺少)")
    backpatch(tc, NXQ)
    loop_statement()
    gencode("j", "", "", q)
    backpatch(fc, NXQ)


# do while语句
def do_while_statement():
    global index, token, error, NXQ
    index += 1
    dos = NXQ
    print("<do while语句>→do<循环用复合语句> while(<布尔表达式>);")
    infer.append("<do while语句>→do<循环用复合语句> while(<布尔表达式>);")
    compound_statement_for_loop()
    if token[index][1] == "while":
        index += 1
    else:
        error += 1
        wrong.append("ERROR! do while语句 缺少while")
    if token[index][1] == "(":
        index += 1
    else:
        error += 1
        wrong.append("ERROR! do while语句while后缺少(")
    tc, fc = BE()
    backpatch(tc, dos)
    if token[index][1] == ")":
        index += 1
    else:
        error += 1
        wrong.append("ERROR! do while语句表达式后缺少)")
    if token[index][1] == ";":
        index += 1
    else:
        error += 1
        wrong.append("ERROR! do while语句末尾缺少;")
    backpatch(fc, NXQ)

# 循环用if语句
def if_statement_for_loop():
    global index, token, error, NXQ
    index += 1
    if token[index][1] == "(":
        index += 1
    else:
        error += 1
        wrong.append("ERROR! if语句if后缺少(")
    print("<循环用if语句>→if(<表达式>)<循环语句>|if(<表达式>)<循环语句>else<循环语句>")
    infer.append("<循环用if语句>→if(<表达式>)<循环语句>|if(<表达式>)<循环语句>else<循环语句>")
    tc, fc = BE()
    if token[index][1] == ")":
        index += 1
    else:
        error += 1
        wrong.append("ERROR! if语句表达式后缺少)")
    backpatch(tc, NXQ)  # 回填真出口
    loop_statement()
    q = NXQ
    if token[index][1] == "else":
        gencode("j", "", "", 0)  # q
        backpatch(fc, NXQ)
        index += 1
        loop_statement()
        backpatch(q, NXQ)
    else:
        backpatch(fc, NXQ)


# return语句
def return_statement():
    global index, token, error
    index += 1
    if token[index][1] == ";":
        print("<return语句>->return;")
        infer.append("<return语句>->return;")
        index += 1
        gencode("ret", "", "", "")
    elif (token[index][1] in ["(", "!"]) or (token[index][0] in [400, 500, 600, 700, 800]):
        print("<return语句>->return<表达式>;")
        infer.append("<return语句>->return<表达式>;")
        rv = expression()
        gencode("ret", "", "", rv)
        if token[index][1] == ";":
            index += 1
        else:
            error += 1
            wrong.append("ERROR! return 表达式后缺少；")
    else:
        error += 1
        wrong.append("ERROR! return后缺少表达式或；")


# break语句
def break_statement():
    global index, token, error
    index += 1
    if token[index][1] == ";":
        index += 1
        print("<break语句>->break;")
        infer.append("<break语句>->break;")
    else:
        error += 1
        wrong.append("ERROR! break后缺少；")


# continue语句
def continue_statement():
    global index, token, error
    index += 1
    if token[index][1] == ";":
        index += 1
        print("<continue语句>→continue;")
        infer.append("<continue语句>→continue;")
    else:
        error += 1
        wrong.append("ERROR! continue后缺少；")


# 循环语句
def loop_statement():
    global index, token, error
    if token[index][1] == "const" or token[index][1] in F_type:
        print("<循环语句>→<声明语句>")
        infer.append("<循环语句>→<声明语句>")
        declaration_statement()
    elif token[index][1] in ["continue", "if", "for", "break", "while", "do", "return"]:
        print("<循环语句>→<循环执行语句>")
        infer.append("<循环语句>→<循环执行语句>")
        loop_execution_statement()
    elif token[index][1] == "{":
        print("<循环语句>→<循环用复合语句>")
        infer.append("<循环语句>→<循环用复合语句>")
        compound_statement_for_loop()
    elif token[index][0] == 700:
        print("<循环语句>-><数据处理语句>")
        infer.append("<循环语句>-><数据处理语句>")
        data_processing_statement()
    else:
        error += 1
        wrong.append("ERROR! 缺少循环语句")


# 循环执行语句
def loop_execution_statement():
    global index, token, error
    if token[index][1] == "if":
        print("<循环执行语句>→<循环用if语句>")
        infer.append("<循环执行语句>→<循环用if语句>")
        if_statement_for_loop()
    elif token[index][1] == "for":
        print("<循环执行语句>→<for语句>")
        infer.append("<循环执行语句>→<for语句>")
        for_statement()
    elif token[index][1] == "while":
        print("<循环执行语句>→<while语句>")
        infer.append("<循环执行语句>→<while语句>")
        while_statement()
    elif token[index][1] == "do":
        print("<循环执行语句>→<do while语句>")
        infer.append("<循环执行语句>→<do while语句>")
        do_while_statement()
    elif token[index][1] == "return":
        print("<循环执行语句>→<return语句>")
        infer.append("<循环执行语句>→<return语句>")
        return_statement()
    elif token[index][1] == "break":
        print("<循环执行语句>→<break语句>")
        infer.append("<循环执行语句>→<break语句>")
        break_statement()
    elif token[index][1] == "continue":
        print("<循环执行语句>→<continue语句>")
        infer.append("<循环执行语句>→<continue语句>")
        continue_statement()


# 循环用复合语句
def compound_statement_for_loop():
    global index, token, error
    if token[index][1] == "{":
        index += 1
    else:
        error += 1
        wrong.append("ERROR! 循环体后缺少}")
    print("<循环用复合语句>→{<循环语句表>}")
    infer.append("<循环用复合语句>→{<循环语句表>}")
    loop_statement_table()
    if token[index][1] == "}":
        index += 1
    else:
        error += 1
        wrong.append("ERROR! 循环体后缺少}")


# 循环语句表
def loop_statement_table():
    global index, token, error
    print("<循环语句表>→<循环语句>|<循环语句><循环语句表>")
    infer.append("<循环语句表>→<循环语句>|<循环语句><循环语句表>")
    loop_statement()
    if (token[index][0] == 700 or (token[index][1] in V_type) or (
            token[index][1] in ["continue", "{", "if", "for", "break", "while", "do", "return", "const"])):
        loop_statement_table()


# 函数块
def function_block():
    global index, token
    if token[index][1] in F_type:
        print("<函数块>-><函数定义><函数块>")
        infer.append("<函数块>-><函数定义><函数块>")
        function_definition()
        function_block()
    else:
        print("<函数块>->null")
        infer.append("<函数块>->null")



# 函数定义形参列表
def function_definition_formal_parameter_list(fdp):
    global index, token, error
    if token[index][1] in V_type:
        print("<函数定义形参列表>→<函数定义形参>")
        infer.append("<函数定义形参列表>→<函数定义形参>")
        function_definition_formal_parameter(fdp)
    else:
        print("<函数定义形参列表>→null")
        infer.append("<函数定义形参列表>→null")


# 函数定义形参
def function_definition_formal_parameter(fdp):
    global index, token, error
    ty = None
    if token[index][1] in V_type:
        ty = token[index][1]
        fdp.append(token[index][1])
        index += 1
    else:
        error += 1
        wrong.append("ERROR! 缺少函数定义形参类型")
    if token[index][0] == 700:
        id = token[index][1]
        variate_na.append(id)
        variate_di[id] = {}
        variate_di[id]["type"] = ty
        variate_di[id]["scope"] = scope
        index += 1
    else:
        error += 1
        wrong.append("ERROR! 缺少函数定义形参名称")
    if token[index][1] == ",":
        index += 1
        print("<函数定义形参>-><变量类型><标识符>,<函数定义形参>")
        infer.append("<函数定义形参>-><变量类型><标识符>,<函数定义形参>")
        print("<变量类型>->int|char|float")
        infer.append("<变量类型>->int|char|float")
        function_definition_formal_parameter(fdp)
    else:
        print("<函数定义形参>-><变量类型><标识符>")
        infer.append("<函数定义形参>-><变量类型><标识符>")
        print("<变量类型>->int|char|float")
        infer.append("<变量类型>->int|char|float")


# 函数定义
def function_definition():
    global index, token, error, variate_di, variate_na
    index += 1
    print("<函数定义>→<函数类型><标识符>(<函数定义形参列表>)<复合语句>")
    infer.append("<函数定义>→<函数类型><标识符>(<函数定义形参列表>)<复合语句>")
    print("<函数类型>->int|char|float|void")
    infer.append("<函数类型>->int|char|float|void")
    fdp = []
    id = None
    if token[index][0] == 700:
        id = token[index][1]
        index += 1
    else:
        error += 1
        wrong.append("ERROR! 缺少函数定义名称")
    gencode(id, "", "", "")
    if token[index][1] == "(":
        index += 1
    else:
        error += 1
        wrong.append("ERROR! 函数定义名称后缺少(")
    function_definition_formal_parameter_list(fdp)
    if id is not None:
        if variate_di[id]["parameter"] != fdp:
            error += 1
            wrong.append("ERROR! 函数定义与声明参数不匹配")
    if token[index][1] == ")":
        index += 1
    else:
        error += 1
        wrong.append("ERROR! 函数定义名称后缺少)")
    compound_statement()


# 程序
def program():
    global index, token, error
    print("<程序>-><声明语句>main()<复合语句><函数块>")
    infer.append("<程序>-><声明语句>main()<复合语句><函数块>")
    declaration_statement()
    if token[index][1] == "main":
        gencode("main", "", "", "")
        index += 1
    else:
        error += 1
        wrong.append("ERROR! 程序开头缺少main")
    if token[index][1] == "(":
        index += 1
    else:
        error += 1
        wrong.append("ERROR! main后缺少(")
    if token[index][1] == ")":
        index += 1
    else:
        error += 1
        wrong.append("ERROR! main缺少)")
    compound_statement()
    gencode("sys", "", "", "")
    function_block()


def start(t):
    global token, index, error, wrong, four_formula, NXQ, nti, variate_na, variate_di, infer
    infer = []
    index = 0
    error = 0
    wrong = []
    four_formula = []
    NXQ = 0
    nti = 1
    variate_na = []
    variate_di = {}
    token = t
    token.append([0, " "])
    program()

    # print(variate_di)
    # print(variate_na)
    wrong.append("\n语法分析结束！ --%d error" % error)
    return wrong, four_formula, variate_di, variate_na, infer
#
# a=[['102','int','2'],
# ['700','a','2'],
# ['219','=','2'],
# ['400','1','2'],
# ['303',',','2']]
# start(a)

if __name__ == '__main__':
    d = """
 //while语句测试，求1到10的数字之和
main(){
  int x;
  int sum = 0;

  x = 1;
  while (x <= 10){
    sum = sum + x;
    x = x + 1;
  }
  write(x);
  write(sum);
}
    """

    m = auto_Lexer()
    m.build()  # Build the lexer
    m.test(d)

    token = []
    # Tokenize
    for tok in m.lexer:
        token.append([int(tok.type), tok.value])
        # print(tok)

    # for i in m.errors:
    #     print(i)
    start(token)
    print('----------------------------------')
    print(wrong)
    print('----------------------------------')
    print(four_formula)
    print('----------------------------------')
    print(variate_di)
    print('----------------------------------')
    print(variate_na)
    print('----------------------------------')
    print(infer)
