import spidev
import time
import os
import glob
import RPi.GPIO as GPIO

#----------------------------
#Assign Pin for Ultrasonic
#----------------------------
TRIG = 23 
ECHO = 24
#-----------------------------

#-------------------------------------------------
#GPIO SETUP UP 
#-------------------------------------------------
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(16,GPIO.OUT) #
GPIO.setup(26, GPIO.IN) #For water leak
GPIO.setup(TRIG,GPIO.OUT)#
GPIO.setup(ECHO,GPIO.IN) #For Water Level_1
#-------------------------------------------------


#---------------------------------------------------
#Intial setup for analog SEnsor
#---------------------------------------------------
# Define sensor channels
Turbidity_channel = 0

# Define delay between readings
delay = 5

#Define variables
result=0.0
pulse_start=0.0
pulse_start=0.0
pulse_duration=0.0




#---------------------------------------------------


#------------------------------------------------------
#Intial setup for Temperature Sensor DS18B20
#------------------------------------------------------
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
 
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

#------------------------------------------------------


#------------------------------------------------------
#To read Analog Sensors Turbidity
#------------------------------------------------------
# Open SPI bus
spi = spidev.SpiDev()
spi.open(0,0)
 
# Function to read SPI data from MCP3008 chip
# Channel must be an integer 0-7
def ReadChannel(channel):
  adc = spi.xfer2([1,(8+channel)<<4,0])
  data = ((adc[1]&3) << 8) + adc[2]
  return data
 
# Function to convert data to voltage level,
# rounded to specified number of decimal places.
def ConvertVolts(data,places):
  volts = (data * 3.3) / float(1023)
  volts = round(volts,places)
  return volts

# Function to calculate temperature from8
# TMP36 data, rounded to specified
# number of decimal places.
def ConvertTemp(data,places):
 
  # ADC Value
  # (approx)  Temp  Volts
  #    0      -50    0.00
  #   78      -25    0.25
  #  155        0    0.50
  #  233       25    0.75
  #  310       50    1.00
  #  465      100    1.50
  #  775      200    2.50
  # 1023      280    3.30
 
  temp = ((data * 330)/float(1023))-50
  temp = round(temp,places)
  return temp

#----------------------------------------------

#------------------------------------------------------
#To read Temperature Sensor DS18B20
#------------------------------------------------------
def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
 
def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c #,temp_f

#-------------------------------------------------------

#-------------------------------------------------------
#To read Aquarium WAter Level
#-------------------------------------------------------
def read_AquaWaterLevel():
    global pulse_duration
    global pulse_start
    global pulse_end
    GPIO.output(TRIG, False)
    #print "Waiting For Sensor To Settle"
    time.sleep(0.5)

    
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)


    
    while GPIO.input(ECHO)==0:
      pulse_start = time.time()

    while GPIO.input(ECHO)==1:
      pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start

    distance = pulse_duration * 17150

    distance = round(distance, 2)
      

    #print "Distance:",distance,"cm"
    return distance

#-------------------------------------------------------
