# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'console.ui'
#
# Created: Mon Mar 25 21:31:17 2013
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ConsoleWindow(object):
    def setupUi(self, ConsoleWindow):
        ConsoleWindow.setObjectName(_fromUtf8("ConsoleWindow"))
        ConsoleWindow.resize(423, 346)
        self.verticalLayout = QtGui.QVBoxLayout(ConsoleWindow)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.textOutput = QtGui.QTextEdit(ConsoleWindow)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.textOutput.setFont(font)
        self.textOutput.setReadOnly(True)
        self.textOutput.setObjectName(_fromUtf8("textOutput"))
        self.verticalLayout.addWidget(self.textOutput)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(10, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.textInput = QtGui.QLineEdit(ConsoleWindow)
        self.textInput.setObjectName(_fromUtf8("textInput"))
        self.horizontalLayout.addWidget(self.textInput)
        self.buttonExec = QtGui.QPushButton(ConsoleWindow)
        self.buttonExec.setObjectName(_fromUtf8("buttonExec"))
        self.horizontalLayout.addWidget(self.buttonExec)
        self.buttonClear = QtGui.QPushButton(ConsoleWindow)
        self.buttonClear.setObjectName(_fromUtf8("buttonClear"))
        self.horizontalLayout.addWidget(self.buttonClear)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(ConsoleWindow)
        QtCore.QMetaObject.connectSlotsByName(ConsoleWindow)

    def retranslateUi(self, ConsoleWindow):
        ConsoleWindow.setWindowTitle(QtGui.QApplication.translate("ConsoleWindow", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonExec.setText(QtGui.QApplication.translate("ConsoleWindow", "exec", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonClear.setText(QtGui.QApplication.translate("ConsoleWindow", "clear", None, QtGui.QApplication.UnicodeUTF8))

