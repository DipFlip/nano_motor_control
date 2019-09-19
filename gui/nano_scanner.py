import nano_control as nc
import subprocess, time, signal
import os
import sys
from datetime import datetime #TODO write time for each scan position in log file
import time
import psutil #to check if EFU is running
from tqdm import tqdm # for fancy terminal progress bar
import glob # to check if file exists

class Scanner():
    """class for scanning MAPMT in the nano chamber in the micro-beam hall"""
    def __init__(self, laser_setup = True, nano_setup = False):
        self.path_to_libraries = '/home/erofors/LaserScan'
        self.output_directory = '/home/erofors/data'
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
            if not check_if_process_is_running('testwise'):
                print('testwise wasnt running..')
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
        if self.nano_setup:
            self.motor_zero_x = motor_x - mapmt_x*self.steps_per_mm # for nano motors
        if self.laser_setup:
            self.motor_zero_x = motor_x + mapmt_x*self.steps_per_mm #for LTF motors
        self.motor_zero_y = motor_y + mapmt_y*self.steps_per_mm
        print(f"motor zero x:{self.motor_zero_x}, y:{self.motor_zero_y}")
    def to_MAPMT_xy(self, motor_x, motor_y):
        """takes motor coordinates and returns MAPMT x,y coordinates (string)"""
        if self.nano_setup:
            x = 0 - (motor_x - self.motor_zero_x) / self.steps_per_mm
            y = 0 - (motor_y - self.motor_zero_y) / self.steps_per_mm
        if self.laser_setup:
            x = 0 - (self.motor_zero_x - motor_x) / self.steps_per_mm
            y = 0 - (self.motor_zero_y - motor_y) / self.steps_per_mm
        return "{0:.2f}".format(x), "{0:.2f}".format(y)
    def to_motor_xy(self, mapmt_x, mapmt_y):
        """takes MAPMT coordinates and returns motor absolute x,y positions"""
        if self.nano_setup:
            motor_x = int(self.motor_zero_x + mapmt_x * self.steps_per_mm)
            motor_y = int(self.motor_zero_y + mapmt_y * self.steps_per_mm)
        if self.laser_setup:
            motor_x = self.motor_zero_x - mapmt_x * self.steps_per_mm
            motor_y = self.motor_zero_y - mapmt_y * self.steps_per_mm
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
        print(f"Moving to X:{x} (motor:{motor_x})")
        subprocess.call([self.path_to_libraries + f"/work", "M", "1", f"{motor_x}"])
        time.sleep(6)
        print(f"Moving to Y:{y} (motor:{motor_y})")
        subprocess.call([self.path_to_libraries + f"/work", "M", "2", f"{motor_y}"])
        time.sleep(6)
    def scan(self, x_positions = range(10,20), y_positions = range(10,20), runname='runname', 
            num_events = 10000, time_per_pos = None, VME_daq = True, EFU_daq = False):
        """performs a scan, defaults to VME readout at LTF with laser motors"""
        dir_to_make = f"{self.output_directory}/{runname}"
        filename = 'file not set yet'
        print('scan about to start')
        if not os.path.exists(dir_to_make):
            os.mkdir(dir_to_make)
        else:
            print(f"Error: Directory {dir_to_make} already exists! Not performing scan!")
            return 1
        for x in x_positions:
            for y in y_positions:
                filename = f"{self.output_directory}/{runname}/X{x}Y{y}_scan"
                if self.laser_setup:
                    self.move_laser_motors(x, y)
                elif self.nano_setup:
                    self.move_nano_motors(x, y)
                print("Starting DAQ")
                if EFU_daq:
                    proc = subprocess.Popen(['./efu_dump_start.sh', filename],
                        cwd="/home/erofors/essdaq/efu")
                    if time_per_pos is not None:
                        print(f"Measuring pos x:{x}, y:{y} for {time_per_pos} seconds.")
                        for i in tqdm(range(int(time_per_pos))):
                            time.sleep(1)
                            if glob.glob(f"{filename}*_2.csv"):
                                print("got 100 MB of data at this point. Breaking early to move on.")
                                break
                        subprocess.call('./efu_stop.sh', cwd="/home/erofors/essdaq/efu")
                        time.sleep(1)
                if VME_daq:
                    proc = subprocess.Popen([('./readout', f"{self.path_to_libraries}/readout.cfg",
                        f"--daq=1", f"--events={num_events}", f"--prefix={filename}.bin.gz")], cwd=self.path_to_libraries)
                    proc.communicate() #should wait until the process is done
                print(f"Position x:{x}, y:{y} done")
        print(f"Scan done, last filename was {filename}")
        return 0
def check_if_process_is_running(process_name):
    for pid in psutil.pids():
        p = psutil.Process(pid)
        if process_name in p.name():
            print (f"{p.name} is running with pid {pid} !")
            return True
    return False

# convert files from binary to root
#for j in $(cat $RUNLIST) ; do
#:  $PATHTOBINARIES/bin2many $j
#done
# or mabe
# ./bin2many --Sparse-- --v792 2 $daqfileout
