import sys
import lex
import copy
import asm
from PIL import Image
from io import BytesIO
from graphviz import Digraph
import regulertoNFA
import NFA_determinism
import DFA_minimization
from anytree import Node, RenderTree
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QWidget, QVBoxLayout,
    QSplitter, QPushButton, QFileDialog, QHBoxLayout, QToolBar, QLabel, QDialog, QGridLayout,QLineEdit
)
from PyQt5.QtGui import QFont, QPainter, QPixmap
from PyQt5.QtCore import Qt, QSize, QRect, QPoint
from io import BytesIO
import Grammar_analysis as Gn
from Auto_LexicalAnalysis import auto_Lexer   #自动词法
from Intermediate_code import yufa_and_zhongjian
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QWidget, QVBoxLayout,
    QSplitter, QPushButton, QFileDialog, QHBoxLayout, QToolBar
)
from PyQt5.QtGui import QFont, QPainter
from PyQt5.QtCore import Qt, QSize, QRect, QPoint
def visualize_nfa(nfa, name_list):
    dot = Digraph()
    print('开始构建节点')
    # 创建所有状态的节点
    states = set()
    def add_states(state):
        if state not in states:
            states.add(state)
            label_name = str(1000 - name_list.pop())
            shape = 'doublecircle' if state.isEnd else 'circle'
            # 在这里设置节点的大小
            dot.node(str(id(state)), label=str(state.id-10), shape=shape, width='0.5', height='0.5')
            for symbol, next_states in state.transition.items():
                for next_state in next_states:
                    add_states(next_state)
                    dot.edge(str(id(state)), str(id(next_state)), label=symbol)
            for next_state in state.epsilonTransitions:
                add_states(next_state)
                dot.edge(str(id(state)), str(id(next_state)), label='ε')

    add_states(nfa.start)
    print('结束构建节点')
    # 使用BytesIO对象来存储生成的图像数据
    dot_file = BytesIO(dot.pipe(format='png'))

    return dot_file

def visualize_dfa(dfa_states, name_list):
    dot = Digraph()
    for state in dfa_states.values():
        if state.is_end:
            dot.node(str(id(dfa_states[state])), label=str(1000 - name_list.pop()), shape='doublecircle', width='0.5', height='0.5')
        else:
            dot.node(str(id(dfa_states[state])), label=str(1000 - name_list.pop()), shape='circle', width='0.5', height='0.5')
        # 添加状态转移的边
        for symbol, next_state in state.transitions.items():
            dot.edge(str(id(dfa_states[state])), str(id(dfa_states[next_state])), label=symbol)

    # 将图形数据转换为PNG格式
    dot_file = BytesIO(dot.pipe(format='png'))
    return dot_file

def visualize_mindfa(mindfa, name_list):
    dot = Digraph()
    for state in mindfa.values():
        if state.is_end:
            dot.node(str(id(mindfa[state])), label=str(1000 - name_list.pop()), shape='doublecircle', width='0.5', height='0.5')
        else:
            dot.node(str(id(mindfa[state])), label=str(1000 - name_list.pop()), shape='circle', width='0.5', height='0.5')
        # 添加状态转移的边
        for symbol, next_state in state.transitions.items():
            dot.edge(str(id(mindfa[state])), str(id(mindfa[next_state])), label=symbol)

    # 将图形数据转换为PNG格式
    dot_file = BytesIO(dot.pipe(format='png'))
    return dot_file



class LineNumPaint(QWidget):
    def __init__(self, q_edit):
        super().__init__(q_edit)
        self.q_edit_line_num = q_edit

    def sizeHint(self):
        return QSize(self.q_edit_line_num.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.q_edit_line_num.lineNumberAreaPaintEvent(event)
class QTextEditWithLineNum(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(QFont("Microsoft YaHei", 10, 1))
        self.setLineWrapMode(QTextEdit.NoWrap)  # 不自动换行
        self.lineNumberArea = LineNumPaint(self)
        self.document().blockCountChanged.connect(self.update_line_num_width)
        self.verticalScrollBar().valueChanged.connect(self.lineNumberArea.update)
        self.textChanged.connect(self.lineNumberArea.update)
        self.cursorPositionChanged.connect(self.lineNumberArea.update)
        self.update_line_num_width()

    def lineNumberAreaWidth(self):
        block_count = self.document().blockCount()
        max_value = max(1, block_count)
        d_count = len(str(max_value))
        _width = self.fontMetrics().width('9') * d_count + 5
        return _width

    def update_line_num_width(self):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), Qt.lightGray)
        first_visible_block_number = self.cursorForPosition(QPoint(0, 1)).blockNumber()
        blockNumber = first_visible_block_number
        block = self.document().findBlockByNumber(blockNumber)
        top = self.viewport().geometry().top()
        if blockNumber == 0:
            additional_margin = int(self.document().documentMargin() - 1 - self.verticalScrollBar().sliderPosition())
        else:
            prev_block = self.document().findBlockByNumber(blockNumber - 1)
            additional_margin = int(self.document().documentLayout().blockBoundingRect(prev_block).bottom()) - self.verticalScrollBar().sliderPosition()
        top += additional_margin
        bottom = top + int(self.document().documentLayout().blockBoundingRect(block).height())
        last_block_number = self.cursorForPosition(QPoint(0, self.height() - 1)).blockNumber()
        height = self.fontMetrics().height()
        while block.isValid() and (top <= event.rect().bottom()) and blockNumber <= last_block_number:
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(Qt.black)
                painter.drawText(0, top, self.lineNumberArea.width(), height, Qt.AlignCenter, number)
            block = block.next()
            top = bottom
            bottom = top + int(self.document().documentLayout().blockBoundingRect(block).height())
            blockNumber += 1

class Example(QMainWindow):
    def __init__(self):
        super().__init__()

        self.textedit1 = QTextEditWithLineNum()
        self.textedit2 = QTextEditWithLineNum()
        self.textedit3 = QTextEditWithLineNum()
        self.filename = ''
        self.text = ''
        self.token=[]

        self.token_my=[]
        self.initUI()

    def initUI(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        buttons = [
            ('打开文件', self.openFile),
            ('刷新', self.refreshContent),
            ('NFA-DFAmin', self.nfa_dfa_min),
            ('词法分析', self.lexical_analysis),
            ('语法分析', self.syntax_analysis),
            ('中间代码', self.intermediate_code),
            ('目标代码', self.target_code)
        ]

        for name, func in buttons:
            button = QPushButton(name)
            button.clicked.connect(func)
            toolbar.addWidget(button)

        hsplitter = QSplitter(Qt.Horizontal, self)

        vbox1 = QVBoxLayout()
        self.textedit1.setStyleSheet("background-color: lightblue;")
        vbox1.addWidget(self.textedit1)

        widget1 = QWidget()
        widget1.setLayout(vbox1)

        vsplitter = QSplitter(Qt.Vertical, self)
        self.textedit2.setStyleSheet("background-color: lightgreen;")
        self.textedit3.setStyleSheet("background-color: lightyellow;")
        vsplitter.addWidget(self.textedit2)
        vsplitter.addWidget(self.textedit3)

        hsplitter.addWidget(widget1)
        hsplitter.addWidget(vsplitter)

        self.setCentralWidget(hsplitter)

        self.setGeometry(100, 100, 1000, 800)
        self.setWindowTitle('QSplitter 示例')
        self.show()

    def openFile(self):
        options = QFileDialog.Options()
        self.filename, _ = QFileDialog.getOpenFileName(self, "Open Text File", "", "Text Files (*.txt);;All Files (*)", options=options)
        print(self.filename)
        if self.filename:
            with open(self.filename, 'r', encoding='utf-8') as f:
                content = f.read()
                self.text = ''.join(content)
        self.displayContent1(self.text)

    def refreshContent(self):
        self.text = self.textedit1.toPlainText()


    def nfa_dfa_min(self):
        self.nfa_dfa_dialog = NfaDfaMinDialog()
        self.nfa_dfa_dialog.show()

    def lexical_analysis(self):
        copied_txt = copy.deepcopy(self.text)
        finall = lex.lex_analysis(copied_txt)
        self.token_my=finall
        formatted_string = ''
        for lst in finall:
            formatted_string += f'{lst[0]}   {lst[1]}   {lst[2]}\n'
        m = auto_Lexer()
        m.build()
        m.test(copy.deepcopy(self.text))
        token = []
        with open("min_LexToken.txt", "w+", encoding="utf-8") as f:
            for tok in m.lexer:
                f.write("[" + str(tok.type) + "," + str(tok.value) + "," + str(tok.lineno) + "]" + "\n")
                token.append([int(tok.type), tok.value])
        self.token=token

        self.displayContent2(formatted_string)



    def syntax_analysis(self):
        error, self.Quaternion, self.symbol_table_dict, self.symbol_table_name, s = Gn.start(self.token)
        print('他的四元式')
        print(self.Quaternion)
        ROOT,self.siyuan=yufa_and_zhongjian(self.token_my)

        # print(siyuan)
        self.displayContent3(ROOT)


    def intermediate_code(self):
        txt=""
        j=0
        for i in self.siyuan:
            txt+=f'{j}  [{i[0]}   {i[1]}   {i[2]}   {i[3]}]\n'
            j+=1

        self.displayContent2(txt)

    def target_code(self):
        self.code = asm.get_asm(self.Quaternion, self.symbol_table_name, self.symbol_table_dict)

        self.displayContent2(self.code)

    def displayContent1(self, content):
        self.textedit1.clear()
        self.textedit1.setText(content)

    def displayContent2(self, content):
        self.textedit2.clear()
        self.textedit2.setText(content)

    def display_tree_structure(self, node, level=0):
        "展示树形状"
        # print(level)
        text = ""
        if node is not None:
            text += "-" * level*5 + str(node.name) + "\n"
            for child in node.children:
                text += self.display_tree_structure(child, level + 1)
        return text
    def displayContent3(self, ROOT):
        self.textedit3.clear()
        tree_text = self.display_tree_structure(ROOT)
        self.textedit3.setText(tree_text)
class NfaDfaMinDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('NFA-DFA Minimization')
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        # 图形展示区域
        self.image_label = QLabel(self)
        layout.addWidget(self.image_label)

        # 按钮区域
        button_layout = QHBoxLayout()
        visualize_nfa_button = QPushButton('Visualize NFA')
        convert_dfa_button = QPushButton('Convert to DFA and Visualize')
        minimize_dfa_button = QPushButton('Minimize DFA')

        button_layout.addWidget(visualize_nfa_button)
        button_layout.addWidget(convert_dfa_button)
        button_layout.addWidget(minimize_dfa_button)

        visualize_nfa_button.clicked.connect(self.visualize_nfa)
        convert_dfa_button.clicked.connect(self.convert_to_dfa_and_visualize)
        minimize_dfa_button.clicked.connect(self.minimize_dfa)

        self.regex_input = QLineEdit(self)
        self.regex_input.setPlaceholderText('Enter your regex here...')
        layout.addWidget(self.regex_input)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def visualize_nfa(self):
        regex = self.regex_input.text()
        print('输入的正规式为：', regex)
        nfa = regulertoNFA.regex_to_nfa(regex)

        nfa_image_data = visualize_nfa(nfa, [i + 1 for i in range(1000)])
        self.display_image(nfa_image_data)

    def convert_to_dfa_and_visualize(self):
        regex = self.regex_input.text()
        print('输入的正规式为：', regex)
        nfa = regulertoNFA.regex_to_nfa(regex)
        dfa = NFA_determinism.nfa_to_dfa(nfa.start)
        dfa_image_data = visualize_dfa(dfa, [i + 1 for i in range(1000)])
        self.display_image(dfa_image_data)

    def minimize_dfa(self):
        regex = self.regex_input.text()
        print('输入的正规式为：', regex)
        nfa = regulertoNFA.regex_to_nfa(regex)
        dfa = NFA_determinism.nfa_to_dfa(nfa.start)
        min_dfa = DFA_minimization.minimize_dfa(dfa)
        dfa_image_data = visualize_mindfa(min_dfa, [i + 1 for i in range(1000)])
        self.display_image(dfa_image_data)

    def display_image(self, image_data):
        pixmap = QPixmap()
        pixmap.loadFromData(image_data.getvalue())
        # 获取标签的大小
        label_size = self.image_label.size()
        # 缩放pixmap以适应标签的大小
        scaled_pixmap = pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.resize(scaled_pixmap.width(), scaled_pixmap.height())
# a.c.d|a*.b
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
