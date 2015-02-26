import sip
sip.setapi("QString", 2)
sip.setapi('QVariant', 2)

from QtSupport import QtSupport, QtGlobalModule
from QtEditorModule import QtEditorModule
from TopEditorModule import TopEditorModule, SubEditorModule
