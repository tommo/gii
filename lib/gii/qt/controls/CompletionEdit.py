import sys
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QApplication, QCompleter, QLineEdit, QStringListModel

def get_data(model):
    model.setStringList(["completion", "data", "goes", "here"])

if __name__ == "__main__":

    app = QApplication(sys.argv)
    edit = QLineEdit()
    completer = QCompleter()
    edit.setCompleter(completer)

    model = QStringListModel()
    completer.setModel(model)
    get_data(model)

    edit.show()
    sys.exit(app.exec_())