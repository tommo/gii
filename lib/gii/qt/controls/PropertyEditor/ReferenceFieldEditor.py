from gii.core import *
from gii.core.model import *

from PropertyEditor import FieldEditor, registerFieldEditor
from SearchFieldEditor import SearchFieldEditorBase

##----------------------------------------------------------------##
class ReferenceFieldEditor( SearchFieldEditorBase ):	
	def getSearchContext( self ):
		return "scene"

	def gotoObject( self ):
		signals.emit( 'selection.hint', self.target )

##----------------------------------------------------------------##

registerFieldEditor( ReferenceType, ReferenceFieldEditor )
