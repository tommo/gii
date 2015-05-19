"""
Provides widget classes and functions.

.. warning:: All PyQt4/PySide gui classes are exposed but when you use
    PyQt5, those classes are not available. Therefore, you should treat/use
    this package as if it was ``PyQt5.QtWidgets`` module.
"""
import os
from pyqode.qt import QT_API
from pyqode.qt import PYQT5_API
from pyqode.qt import PYQT4_API
from pyqode.qt import PYSIDE_API

if os.environ[QT_API] in PYQT5_API:
    from PyQt5.QtWidgets import *
elif os.environ[QT_API] in PYQT4_API:
    from PyQt4.QtGui import *
    from PyQt4.QtGui import QFileDialog as OldFileDialog

    class QFileDialog(OldFileDialog):

        @staticmethod
        def getOpenFileName(parent=None, caption='', directory='',
                            filter='', selectedFilter='',
                            options=OldFileDialog.Options()):
            return OldFileDialog.getOpenFileNameAndFilter(
                parent, caption, directory, filter, selectedFilter,
                options)

        @staticmethod
        def getOpenFileNames(parent=None, caption='', directory='',
                             filter='', selectedFilter='',
                             options=OldFileDialog.Options()):
            return OldFileDialog.getOpenFileNamesAndFilter(
                parent, caption, directory, filter, selectedFilter,
                options)

        @staticmethod
        def getSaveFileName(parent=None, caption='', directory='',
                            filter='', selectedFilter='',
                            options=OldFileDialog.Options()):
            return OldFileDialog.getSaveFileNameAndFilter(
                parent, caption, directory, filter, selectedFilter,
                options)
elif os.environ[QT_API] in PYSIDE_API:
    from PySide.QtGui import *
