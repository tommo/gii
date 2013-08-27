# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ObjectContainer.ui'
#
# Created: Tue Aug 27 19:18:25 2013
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ObjectContainer(object):
    def setupUi(self, ObjectContainer):
        ObjectContainer.setObjectName(_fromUtf8("ObjectContainer"))
        ObjectContainer.resize(317, 426)
        self.verticalLayout = QtGui.QVBoxLayout(ObjectContainer)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(5, 5, 5, 0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.ObjectHeader = QtGui.QWidget(ObjectContainer)
        self.ObjectHeader.setObjectName(_fromUtf8("ObjectHeader"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.ObjectHeader)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.buttonFold = QtGui.QToolButton(self.ObjectHeader)
        self.buttonFold.setMaximumSize(QtCore.QSize(20, 20))
        self.buttonFold.setCheckable(False)
        self.buttonFold.setChecked(False)
        self.buttonFold.setObjectName(_fromUtf8("buttonFold"))
        self.horizontalLayout.addWidget(self.buttonFold)
        self.labelName = QtGui.QLabel(self.ObjectHeader)
        self.labelName.setObjectName(_fromUtf8("labelName"))
        self.horizontalLayout.addWidget(self.labelName)
        self.verticalLayout.addWidget(self.ObjectHeader)
        self.container = QtGui.QWidget(ObjectContainer)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.container.sizePolicy().hasHeightForWidth())
        self.container.setSizePolicy(sizePolicy)
        self.container.setObjectName(_fromUtf8("container"))
        self.verticalLayout.addWidget(self.container)

        self.retranslateUi(ObjectContainer)
        QtCore.QMetaObject.connectSlotsByName(ObjectContainer)

    def retranslateUi(self, ObjectContainer):
        ObjectContainer.setWindowTitle(QtGui.QApplication.translate("ObjectContainer", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonFold.setText(QtGui.QApplication.translate("ObjectContainer", "+", None, QtGui.QApplication.UnicodeUTF8))
        self.labelName.setText(QtGui.QApplication.translate("ObjectContainer", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))

