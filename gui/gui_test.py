from PyQt5 import QtCore, QtGui, QtWidgets, uic
import QT_resource_file_rc
import sys


qtCreatorFile = "motor_control_gui.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
 
class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.move_motor)
        self.mapmtMap.mousePressEvent = self.getPos
    def getPos(self , event):
        x = event.pos().x()
        y = event.pos().y() 
        x_global = event.globalPos().x()
        y_global = event.globalPos().y()
        x_screen = self.mapmtMap.mapToGlobal(event.pos()).x()
        y_screen = self.mapmtMap.mapToGlobal(event.pos()).y()
        xw = self.mapFromGlobal(event.globalPos()).x()-25
        yw = self.mapFromGlobal(event.globalPos()).y()-55
        rel_x = self.mapmtMap.mapFromGlobal(event.globalPos()).x()
        rel_y = self.mapmtMap.mapFromGlobal(event.globalPos()).y()
        self.setXBox.setValue(rel_x)
        self.setYBox.setValue(rel_y)
        self.position_x.move(xw, yw)
        print(f"x:{x}, y:{y}, gx:{x_global}, gy:{y_global}, sx:{x_screen}, sy:{y_screen}")
        # self.mapmt_map.mousePressEvent = self.map_clicked
    def move_motor(self, b):
        if self.relative_radio.isChecked():
            print("relative")
        if self.absolute_radio.isChecked():
            print("absolute")
        if self.mapmt_radio.isChecked():
            print("mapmt")

if __name__ == "__main__":
    # app = QtGui.QApplication(sys.argv)
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())