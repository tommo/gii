from gii.core import *
from gii.core.model import *

from PropertyEditor import FieldEditor, registerSimpleFieldEditorFactory
from SearchFieldEditor import SearchFieldEditorBase

##----------------------------------------------------------------##
class ReferenceFieldEditor( SearchFieldEditorBase ):	
	def getSearchContext( self ):
		return "scene"

	def gotoObject( self ):
		signals.emit( 'selection.hint', self.target )

##----------------------------------------------------------------##

registerSimpleFieldEditorFactory( ReferenceType, ReferenceFieldEditor )
