from gii.qt.controls.GLWidget import GLWidget
from gii.core import signals

def GLContextInit():
	GLWidget.getSharedWidget().makeCurrent()

signals.connect( 'moai.context.init', GLContextInit )
