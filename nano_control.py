"""
 List of commands:
 AB  Abort: Stop motion abruptly
 AB1 Abort: Stop motion smoothly with programmed deceleration
 BF  Set brake OFF
 BN  Set brake ON
 CA  Pulse output for PZT stages, channel A
 CB  Pulse output for PZT stages, channel B
 CF  Channel OFF
 CN  Channel ON
 CP  Channel pattern
 CS  Report checksum
 DD  Define d-term (derivative gain)
 DH  Define home
 DI  Define i-term (integral gain)
 DL  Define integration limit
 DP  Define p-term (proportional gain)
 EF  Set Echo OFF
 EM  Execute Macro
 EN  Set Echo ON
 FE  Find edge (find origin position )
 GD  Get d-term
 GH  Go home
 GI  Get i-term
 GL  Get integration limit
 GP  Get p-term
 LF  Limit switch operation OFF
 LH  Limit switches active high
 LL  Limits switches active low
 LN  Limit switch operation ON
 MA  Move absolute
 MD  Macro definition
 MF  Motor off
 MN  Motor on
 MR  Move relative
 RM  Reset (erase) macro
 RP  Repeat from beginning of line
 RT  Reset (like power-on reset)
 SA  Set Acceleration
 SC  Select controller
 SM  Set maximum following error
 ST  Stop motion smoothly and move back
 SV  Set Velocity
 TA  Tell analog input value
 TB  Tell board address
 TC  Tell channel (digital input)
 TD  Tell dynamic target
 TE  Tell error (distance from target)
 TF  Tell profile following error
 TI  Tell iteration number
 TL  Tell programmed acceleration
 TM  Tell macro contents
 TP  Tell position
 TS  Tell status
 TT  Tell target position
 TV  Tell actual velocity
 TY  Tell programmed velocity
 TZ  Tell Macro Zero
 UD  Update flash
 VE  Display version number
 WA  Wait absolute time
 WF  Wait channel OFF
 WN  Wait channel ON
 WS  Wait stop
 XF  Execute if channel OFF
 XN  Execute if channel ON
 '   Single Character Command: TP (Tell Position)
 #   Single Character Command: TC (Tell Channel)
 %   Single Character Command: TS (Tell Status)
 ?   Single Character Command: TE (Tell Position Error)
 (   Single Character Command: TF (Tell Profile Error)
 /   Single Character Command: (Tell LM629 status)
 !   Single Character Command: Halt for all members
"""

import serial
import time

#connect
ser = serial.Serial(port='/dev/ttyUSB0',baudrate=9600, 
    bytesize=8, stopbits=1, parity=serial.PARITY_NONE, timeout=1, xonxoff=0, rtscts=0, dsrdtr=0)

def select_motor(motor_address):
    """write the character 0x01 followed by the motor address number without /r to select that motor"""
    if motor_address = 'x':
        motor_address = 4
    if motor_address = 'y':
        motor_address = 3
    ser.write(b'\x01' + str(motor_address).encode())

def command(command_string):
    """Sends the command followed by \r then prints and returns the response """
    ser.write(command_string.encode() + b'\r')
    response = ser.readline()#.strip('\r\n'+chr(0x03))  #the controller's replies 
                                                        #end with '\n\r'+ETX (end-of-text, 0x03),
                                                        #which should be removed.
    print(response)
    return response

def configure_motor_parameters():
    """ Configures motor parameters for X (4), Y(3) and Z(2) motors and turns them on """
    def write_parameters(SA, SV, DP, DI, DD, DL):
        command('SA' + str(SA))
        command('SV' + str(SV))
        command('DP' + str(DP))
        command('DI' + str(DI))
        command('DD' + str(DD))
        command('DL' + str(DL))
        command('EF') #Set Echo OFF
        command('LH') #Limit switches active high
        command('LN') #Limit switch operation ON
        command('BF') #Set brake OFF
        command('MN') #Turn motor ON
    
    select_motor(4) #X motor
    write_parameters(SA = 500000, SV = 120000, DP = 130, DI = 20, DD = 320, DL = 2000)
    select_motor(3) #Y motor
    write_parameters(SA = 750000, SV = 175000, DP = 250, DI = 12, DD = 250, DL = 2000)
    select_motor(2) #Z motor
    write_parameters(SA = 750000, SV = 175000, DP = 250, DI = 12, DD = 250, DL = 2000)

def home_all():
        """ 
        moves X and Y motors to lowest positions and defines that as home
        TODO decide if Z motor should be part of this 
        """
        for a in ['x','y']:
                select_motor(a)
                print(f"Moving motor {a}...")
                command('MR-5000000')
                time.sleep(5)
                command('DH') # define home
        print("All motors homed.")

def abort_all():
    """ Sends 'AB' to all motors to stop them """
    for a in [2,3,4]:
        select_motor(a)
        command('AB')

def reset_all():
    """ Sends 'RT' to all motors to stop them, this also powers them off I think """
    for a in [2,3,4]:
        select_motor(a)
        command('RT')

# ser.close() #when done

#Y motor (3): 1000000 steps is 6 mm down, total range is 1 cm
#X motor (4): -2000000 steps is 17 mm beam right, total range is 1 cm 
#Z motor (2): negative relative steps is towards the beam