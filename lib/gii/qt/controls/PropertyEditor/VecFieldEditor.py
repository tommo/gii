from PropertyEditor import FieldEditor, registerFieldEditor

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt


##----------------------------------------------------------------##
class VecFieldEdtior( FieldEditor ):
	"""docstring for VecFieldEdtior"""
	def __init__(self, arg):
		super(VecFieldEdtior, self).__init__()
		self.arg = arg


registerFieldEditor( dataType, clas )
