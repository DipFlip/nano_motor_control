import nano_control as nc
import subprocess, time, signal
import os
import sys
from datetime import datetime #TODO write time for each scan position in log file
import time
import psutil #to check if EFU is running


class Scanner():
    """class for scanning MAPMT in the nano chamber in the micro-beam hall"""
    def __init__(self):
        self.path_to_libraries = '/home/seian/LaserScan'
        self.output_directory = '/media/emil/NTFS_partition/IFE_june_2018/data'
        self.runname = "S11"
        self.dir_to_make = f"{output_directory}/{runname}"
        if not os.path.exists(dir_to_make):
            os.mkdir(dir_to_make)
        else:
            print(f"Error: Directory {self.,dir_to_make} already exists! Exiting")
            sys.exit()


path_to_libraries = '/home/seian/LaserScan'
output_directory = '/media/emil/NTFS_partition/IFE_june_2018/data'
runname = "S11"
dir_to_make = f"{output_directory}/{runname}"
if not os.path.exists(dir_to_make):
    os.mkdir(dir_to_make)
else:
    print(f"Error: Directory {dir_to_make} already exists! Exiting")
    sys.exit()

#  Enter the motor and corresponding MAPMT positions for some position
#  and absolute motor positions for MAPMT (0,0) will be calculated.
#  Don't consider the 0.25 mm extra of the edge pixels.
steps_per_mm = 117647 # TODO confirm real number here
motor_somewhere_x = 1341234
motor_somewhere_y = 1341234
mapmt_somewhere_x = 20
mapmt_somewhere_y = 30
motor_zero_x = motor_somewhere_x - mapmt_somewhere_x*steps_per_mm
motor_zero_y = motor_somewhere_y + mapmt_somewhere_y*steps_per_mm

def to_MAPMT_xy(motor_x, motor_y):
    ### takes motor coordinates and returns MAPMT x,y coordinates (string) ###
    x = 0 - (motor_x - motor_zero_x) / steps_per_mm
    y = 0 - (motor_y - motor_zero_y) / steps_per_mm
    return "{0:.2f}".format(x), "{0:.2f}".format(y)

def to_motor_xy(mapmt_x, mapmt_y):
    ### takes MAPMT coordinates and returns motor absolute x,y positions ###
    motor_x = int(motor_zero_x + mapmt_x * steps_per_mm)
    motor_y = int(motor_zero_y + mapmt_y * steps_per_mm)
    return motor_x, motor_y

def measure_pedestals():
    ### TODO implement ###
    return 0

def scan(VME_daq = True, EFU_daq = False):
    ### performs a scan ###
    nc.configure_motor_parameters()
    nc.home_all()
    # TODO move Z to correct position or don't home it at all
    x_positions = range(10,20)
    y_positions = range(10,20)
    for x in x_positions:
        for y in y_positions:
            filename = f"{output_directory}/{runname}/X{x}Y{y}_scan"
            motor_x, motor_y = to_motor_xy(x,y)
            print(f"Moving to X:{x}")
            nc.select_motor('x')
            nc.command(f"MA{motor_x}")
            time.sleep(5)
            print(f"Moving to Y:{y}")
            nc.select_motor('y')
            nc.command(f"MA{motor_y}")
            time.sleep(5)
            print("Starting DAQ")
            if EFU_run:
                proc = subprocess.Popen(['./bin/efu',
                    '-d', 'modules/sonde', '-p', '50011', '--dumptofile', filename],
                    cwd="/home/emil/essdaq/event-formation-unit/build")
                # when enough data is taken use proc.send_signal(signal.SIGINT)
            if VME_daq:
                proc = subprocess.Popen([(f"./readout {config_file} "
                    f"--daq=1 --events={num_events} --prefix={filename}.bin.gz"), cwd=path_to_libraries])
                proc.communicate() #should wait until the process is done
            print("Closing DAQ")
    return 0


# convert files from binary to root
#for j in $(cat $RUNLIST) ; do
#:  $PATHTOBINARIES/bin2many $j
#done
# or mabe
# ./bin2many --Sparse-- --v792 2 $daqfileout