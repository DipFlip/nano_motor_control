from PyQt5 import QtCore, QtGui, QtWidgets, uic
import QT_resource_file_rc
import sys
import numpy as np
import random
import nano_scanner as ns
import nano_control as nc
from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
qtCreatorFile = "motor_control_gui.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
 
class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.move_motor_button.clicked.connect(self.move_motor)
        self.new_plot_button.clicked.connect(self.update_graph)
        self.start_scan_button.clicked.connect(self.perform_scan)
        self.scanstart_copy.clicked.connect(self.copy_start)
        self.calibrate_button.clicked.connect(self.calibrate)
        self.scanstop_copy.clicked.connect(self.copy_stop)
        self.initiate.clicked.connect(self.initiate_motors)
        self.mapmtMap.mousePressEvent = self.getPos
        self.setXBox.valueChanged.connect(self.move_marker)
        self.setYBox.valueChanged.connect(self.move_marker)
        self.scanner = None
    def initiate_motors(self, event):
        LTF = self.LTF_radio.isChecked()
        nano = self.nano_radio.isChecked()
        self.scanner = ns.Scanner(laser_setup=LTF, nano_setup=nano)
        self.xMotorIndicator.setPixmap(QtGui.QPixmap(':/bilder/on.png'))
        self.yMotorIndicator.setPixmap(QtGui.QPixmap(':/bilder/on.png'))
        self.zMotorIndicator.setPixmap(QtGui.QPixmap(':/bilder/on.png'))
    def calibrate(self):
        self.scanner.set_motor_translation(self.cal_motor_x.value(), self.cal_motor_y.value(), self.cal_mapmt_x.value(), self.cal_mapmt_y.value())
    def getPos(self , event):
        x = event.pos().x()
        y = event.pos().y() 
        rel_x, rel_y = wid_rel_to_mapmt_xy(x, y)
        self.setXBox.setValue(rel_x)
        self.setYBox.setValue(rel_y)
    def move_marker(self, event):
        rel_x, rel_y = mapmt_xy_to_wid_rel(self.setXBox.value(), self.setYBox.value())
        self.motor_marker_to_go.move(rel_x-5, rel_y-8)
    def copy_start(self, event):
        self.scanstart_x.setValue(self.setXBox.value())
        self.scanstart_y.setValue(self.setYBox.value())
    def copy_stop(self, event):
        self.scanstop_x.setValue(self.setXBox.value())
        self.scanstop_y.setValue(self.setYBox.value())
    def move_motor(self, b):
        x = self.setXBox.value()
        y = self.setYBox.value()
        if self.LTF_radio.isChecked():
            self.scanner.move_laser_motors_abs(x, y)
        if self.nano_radio.isChecked():
            self.scanner.move_nano_motors_abs(x, y)
        rel_x, rel_y = mapmt_xy_to_wid_rel(x, y)
        self.motor_marker_now.move(rel_x-5, rel_y-8)
        self.nowXBox.setValue(x)
        self.nowYBox.setValue(y)
    def update_graph(self):
        fs = 500
        f = random.randint(1, 100)
        ts = 1/fs
        length_of_signal = 100
        t = np.linspace(0,1,length_of_signal)
        cosinus_signal = np.cos(2*np.pi*f*t)
        sinus_signal = np.sin(2*np.pi*f*t)
        self.MplWidget.canvas.axes.clear()
        self.MplWidget.canvas.axes.plot(t, cosinus_signal)
        self.MplWidget.canvas.axes.plot(t, sinus_signal)
        self.MplWidget.canvas.axes.legend(('cosinus', 'sinus'),loc='upper right')
        self.MplWidget.canvas.axes.set_title('Cosinus - Sinus Signal')
        self.MplWidget.canvas.draw()
    def perform_scan(self):
        """performs a scan with set parameters"""
        step_size = self.step_size_box.value()
        x_positions = np.arange(self.scanstart_x.value(), self.scanstop_x.value()+step_size, step_size)
        y_positions = np.arange(self.scanstart_y.value(), self.scanstop_y.value()-step_size, -step_size)
        time_per_pos = self.time_per_pos_box.value()
        num_events = self.num_events_box.value()
        runname = self.runname_box.text()
        EFU_daq = self.EFU_readout_radio.isChecked()
        VME_daq = self.VME_readout_radio.isChecked()
        print("Sending command to start scan...")
        self.scanner.scan(x_positions = x_positions, y_positions = y_positions, runname=runname, 
            num_events = num_events, time_per_pos = time_per_pos, VME_daq = VME_daq, EFU_daq = EFU_daq)
            
            

def wid_rel_to_mapmt_xy(rel_x, rel_y):
    x = rel_x*48.5/249-2.7
    y = 51.2-rel_y*48.5/249
    return x, y

def mapmt_xy_to_wid_rel(mapmt_x, mapmt_y):
    x = (mapmt_x+2.7)*249/48.5
    y = (51.2-mapmt_y)*249/48.5
    return x, y

if __name__ == "__main__":
    # app = QtGui.QApplication(sys.argv)
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
