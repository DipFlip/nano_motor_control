import nano_control as nc
import subprocess, time, signal
import os
import sys
from datetime import datetime #TODO write time for each scan position in log file
import time
import psutil #to check if EFU is running


class Scanner():
    """class for scanning MAPMT in the nano chamber in the micro-beam hall"""
    def __init__(self, laser_setup = True, nano_setup = False):
        self.path_to_libraries = '/home/erofors/LaserScan'
        self.output_directory = '/home/data'
        if laser_setup:
            self.steps_per_mm = 1
        elif nano_setup:
            self.steps_per_mm = 117647
        self.laser_setup = laser_setup
        self.nano_setup = nano_setup
        self.motor_zero_x = 0
        self.motor_zero_y = 0
        if nano_setup:
            print('Initiating and homeing nano motors...')
            nc.connect()
            nc.configure_motor_parameters()
            nc.home_all()
        elif laser_setup:
            subprocess.call(['gnome-terminal', '-x', self.path_to_libraries+'/testwise'])
            print('Homeing laser motors...')
            # TODO check if Z motor needs to be moved to somewhere...
            time.sleep(5)
    def set_motor_translation(self, motor_x, motor_y, mapmt_x, mapmt_y):
        """
        Enter the motor and corresponding MAPMT positions for some position
        and absolute motor positions for MAPMT (0,0) will be calculated.
        Don't consider the 0.25 mm extra of the edge pixels.
        """
        self.motor_zero_x = motor_x - mapmt_x*self.steps_per_mm # for nano motors
        self.motor_zero_x = motor_x + mapmt_x*self.steps_per_mm #for LTF motors
        self.motor_zero_y = motor_y + mapmt_y*self.steps_per_mm
        print(f"motor zero x:{self.motor_zero_x}, y:{self.motor_zero_y}")
    def to_MAPMT_xy(self, motor_x, motor_y):
        """takes motor coordinates and returns MAPMT x,y coordinates (string)"""
        x = 0 - (motor_x - motor_zero_x) / self.steps_per_mm
        y = 0 - (motor_y - motor_zero_y) / self.steps_per_mm
        return "{0:.2f}".format(x), "{0:.2f}".format(y)
    def to_motor_xy(self, mapmt_x, mapmt_y):
        """takes MAPMT coordinates and returns motor absolute x,y positions"""
        if self.nano_setup:
            motor_x = int(self.motor_zero_x + mapmt_x * self.steps_per_mm)
            motor_y = int(self.motor_zero_y + mapmt_y * self.steps_per_mm)
        if self.laser_setup:
            motor_x = int(self.motor_zero_x - mapmt_x * self.steps_per_mm)
            motor_y = int(self.motor_zero_y - mapmt_y * self.steps_per_mm)
        return motor_x, motor_y
    def measure_pedestals(self):
        """ TODO implement """
        print("Not implemented!")
        return 0
    def move_nano_motors(self, x, y):
        """Takes MAPMT coordinates and moves accelerator beam to that position"""
        motor_x, motor_y = self.to_motor_xy(x,y)
        print(f"Moving to X:{x}")
        nc.select_motor('x')
        nc.command(f"MA{motor_x}")
        time.sleep(5)
        print(f"Moving to Y:{y}")
        nc.select_motor('y')
        nc.command(f"MA{motor_y}")
        time.sleep(5)
    def move_laser_motors(self, x, y):
        """Takes MAPMT coordinates and moves laser setup to that position"""
        motor_x, motor_y = self.to_motor_xy(x, y)
        print(f"Moving to X:{x} which is {motor_x}")
        subprocess.call([self.path_to_libraries + f"/work", "M", "1", f"{motor_x}"])
        time.sleep(1)
        print(f"Moving to Y:{y} which is {motor_y}")
        subprocess.call([self.path_to_libraries + f"/work", "M", "2", f"{motor_y}"])
        time.sleep(1)
    def scan(self, x_positions = range(10,20), y_positions = range(10,20), runname='runname', VME_daq = True, EFU_daq = False, laser_setup = True, nano_setup = False):
        """performs a scan """
        self.dir_to_make = f"{output_directory}/{runname}"
        if not os.path.exists(dir_to_make):
            os.mkdir(dir_to_make)
        else:
            print(f"Error: Directory {self.dir_to_make} already exists! Not performing scan!")
            return 1
        for x in x_positions:
            for y in y_positions:
                filename = f"{self.output_directory}/{self.runname}/X{x}Y{y}_scan"
                if laser_setup:
                    self.move_laser_motors(x, y)
                elif nano_setup:
                    self.move_nano_motors(x, y)
                print("Starting DAQ")
                if EFU_run:
                    proc = subprocess.Popen(['./bin/efu',
                        '-d', 'modules/sonde', '-p', '50011', '--dumptofile', filename],
                        cwd="/home/emil/essdaq/event-formation-unit/build")
                    # when enough data is taken use proc.send_signal(signal.SIGINT)
                if VME_daq:
                    proc = subprocess.Popen([('./readout', f"{config_file}",
                        f"--daq=1", f"--events={num_events}", f"--prefix={filename}.bin.gz")], cwd=self.path_to_libraries)
                    proc.communicate() #should wait until the process is done
                print("Closing DAQ")
        return 0


# convert files from binary to root
#for j in $(cat $RUNLIST) ; do
#:  $PATHTOBINARIES/bin2many $j
#done
# or mabe
# ./bin2many --Sparse-- --v792 2 $daqfileout
