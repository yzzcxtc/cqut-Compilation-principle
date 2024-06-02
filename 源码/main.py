import Grammar_analysis as Gn
from Auto_LexicalAnalysis import auto_Lexer   #自动词法

m = auto_Lexer()
m.build()  # Build the lexer
m.test(d)
token = []
with open("min_LexToken.txt", "w+", encoding="utf-8") as f:
    for tok in m.lexer:
        f.write("[" + str(tok.type) + "," + str(tok.value) + "," + str(tok.lineno) + "]" + "\n")
        token.append([int(tok.type), tok.value])
self.token = token
with open("min_LexToken.txt", "r", encoding="utf-8") as file:
    token = file.read()
    self.text1.setText(token)

with open("min_LexErrors.txt", "w+", encoding="utf-8") as f:
    for i in m.errors:
        f.write(str(i) + "\n")
with open("min_LexErrors.txt", "r", encoding="utf-8") as file:
    error = file.read()
if error == "":
    self.text2.setText("No")
else:
    self.text2.setText(error)
self.Quaternion, self.symbol_table_dict, self.symbol_table_name, s = Gn.start(self.token)


import lex
import Recursive_descent
from anytree import Node, RenderTree
import re
import sys
from PyQt5.QtGui import QPainter, QFont
from PyQt5.QtWidgets import (QMainWindow, QApplication, QSplitter, QTextEdit, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QFileDialog, QAction, qApp, QMenuBar)
from PyQt5.QtCore import Qt, QRect, QPoint, QSize
from lex import lex_analysis
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QTreeView
from PyQt5.QtGui import QStandardItemModel, QStandardItem

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
        # 获取首个可见文本块
        first_visible_block_number = self.cursorForPosition(QPoint(0, 1)).blockNumber()
        # 从首个文本块开始处理
        blockNumber = first_visible_block_number
        block = self.document().findBlockByNumber(blockNumber)
        top = self.viewport().geometry().top()
        if blockNumber == 0:
            additional_margin = int(
                self.document().documentMargin() - 1 - self.verticalScrollBar().sliderPosition())
        else:
            prev_block = self.document().findBlockByNumber(blockNumber - 1)
            additional_margin = int(self.document().documentLayout().blockBoundingRect(
                prev_block).bottom()) - self.verticalScrollBar().sliderPosition()
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

        # 初始化三个文本编辑区域
        self.textedit1 = QTextEditWithLineNum()
        self.textedit2 = QTextEditWithLineNum()
        self.textedit3 = QTextEditWithLineNum()
        self.filename = ''
        self.text=''
        self.initUI()

    def initUI(self):
        # 创建一个水平分割器
        hsplitter = QSplitter(Qt.Horizontal, self)

        # 创建第一个区域的垂直布局
        vbox1 = QVBoxLayout()
        self.textedit1.setStyleSheet("background-color: lightblue;")
        openButton = QPushButton('打开文件')
        openButton.clicked.connect(self.openFile)
        vbox1.addWidget(openButton)
        vbox1.addWidget(self.textedit1)

        # 创建包含布局的QWidget作为第一个区域
        widget1 = QWidget()
        widget1.setLayout(vbox1)

        # 创建第二个和第三个文本编辑区域的垂直分割器
        vsplitter = QSplitter(Qt.Vertical, self)
        self.textedit2.setStyleSheet("background-color: lightgreen;")
        self.textedit3.setStyleSheet("background-color: lightyellow;")
        vsplitter.addWidget(self.textedit2)
        vsplitter.addWidget(self.textedit3)

        # 将区域添加到水平分割器
        hsplitter.addWidget(widget1)
        hsplitter.addWidget(vsplitter)

        # 设置布局
        self.setCentralWidget(hsplitter)

        # 添加菜单栏
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('文件')

        # 添加退出动作
        exitAction = QAction('退出', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(qApp.quit)
        fileMenu.addAction(exitAction)

        # 添加刷新动作
        refreshAction = QAction('刷新', self)
        refreshAction.triggered.connect(self.refreshContent)  # 假设已经实现了 refreshContent 方法
        fileMenu.addAction(refreshAction)

        self.ROOT=Node("占一个位，不用管")

        # 设置窗口的位置和大小
        self.setGeometry(100, 100, 1000, 800)
        self.setWindowTitle('QSplitter 示例')
        self.show()





    def openFile(self):
        options = QFileDialog.Options()
        self.filename, _ = QFileDialog.getOpenFileName(self,
            "Open Text File", "",
            "Text Files (*.txt);;All Files (*)", options=options)
        if self.filename:
            with open(self.filename, 'r', encoding='utf-8') as f:
                content = f.readlines()
                txt = ''.join(content)
                txt2=''.join(content)
                self.text = ''.join(content)
                fin_list=self.processContent(txt)
                self.displayContent(txt2,fin_list)

    def get_text_area_contents(self):
        content1 = self.textedit1.toPlainText()
        # content2 = self.textedit2.toPlainText()
        # content3 = self.textedit3.toPlainText()

        return content1,content1

    def refreshContent(self):
        # 在这里实现刷新内容的逻辑
        contents,con2 = self.get_text_area_contents()
        # print(contents)
        list = self.processContent(contents)
        # print(list)
        self.displayContent2(list)
        pass

    def extract_and_format(self,listss):
        formatted_string = ''
        for lst in listss:
            for item in lst:
                # 假设 item[0] 和 item[1] 都是字符串，我们要确保每个元素填充至长度一样
                formatted_string += '{:<10} {:<10} {:<10}\n'.format(item[0][:10], item[1],item[2])
        return formatted_string

    def displayContent2(self,con2):
        self.textedit2.setText(con2)

    #对树结构，规整化
    def display_tree_structure(self, node, level=0):
        text = ""
        if node is not None:
            text += "-" * level*5 + str(node.name) + "\n"
            for child in node.children:
                text += self.display_tree_structure(child, level + 1)
        return text

    def processContent(self, content):
        # print(content)
        finall = lex_analysis(content)
        # print(keyword)
        self.ROOT=Recursive_descent.recursion(finall)

        formatted_output = self.extract_and_format([finall])
        # print(formatted_output)
        return formatted_output

    def displayContent(self, content1,con2):

        self.textedit1.setText(content1)
        self.textedit2.setText(con2)
        tree_text = self.display_tree_structure(self.ROOT)
        self.textedit3.setText(tree_text)

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
