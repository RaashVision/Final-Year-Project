import RPi.GPIO as GPIO
import time

#GPIO SETUP UP 
#-------------------------------------------------
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#----------------------------
#Assign Pin for Stepper Motor
#----------------------------
A = 5
B = 6
C = 13
D = 19
#----------------------------

#-------------------------------------------------
#-------------------------------------------------
GPIO.setup(14,GPIO.OUT) #Relay IN4 for Ligth
GPIO.setup(15,GPIO.OUT) #Relay IN3 for Pump_1
GPIO.setup(7,GPIO.OUT)  #Relay IN2 for Pump_2
GPIO.setup(25,GPIO.OUT)  #Relay IN1 for Cooler_Fan
#-------------------------------------------------
GPIO.setup(A, GPIO.OUT) #
GPIO.setup(B, GPIO.OUT) #For Stepper Motor
GPIO.setup(C, GPIO.OUT) #
GPIO.setup(D, GPIO.OUT) #
#-------------------------------------------------

#-------------------------------------------------
#For Ligth,Pump_1,Pump_2,Cooler_Fan
#-------------------------------------------------
def Ligth_On():
      GPIO.output(14,GPIO.LOW)      

def Ligth_Off():
      GPIO.output(14,GPIO.HIGH)

def Pump1_On():
      GPIO.output(15,GPIO.LOW)
      
def Pump1_Off():
      GPIO.output(15,GPIO.HIGH)
      

def Pump2_On():
      GPIO.output(7,GPIO.LOW)
      
      
def Pump2_Off():
      GPIO.output(7,GPIO.HIGH)     

def CoolerFan_On():
      GPIO.output(25,GPIO.LOW)
      
def CoolerFan_Off():
      GPIO.output(25,GPIO.HIGH)
      
def stopAll():
      GPIO.output(14,GPIO.HIGH)
      GPIO.output(15,GPIO.HIGH)
      GPIO.output(7,GPIO.HIGH)
      GPIO.output(25,GPIO.HIGH)
#--------------------------------------------------------
#For Stepper Motor
#--------------------------------------------------------
def GPIO_SETUP(a,b,c,d):
    GPIO.output(A, a)
    GPIO.output(B, b)
    GPIO.output(C, c)
    GPIO.output(D, d)
    time.sleep(0.001)

def Fish_Feeder_RTURN(deg):

    full_circle = 510.0
    degree = full_circle/360*deg
    GPIO_SETUP(0,0,0,0)

    while degree > 0.0:
        GPIO_SETUP(1,0,0,0)
        GPIO_SETUP(1,1,0,0)
        GPIO_SETUP(0,1,0,0)
        GPIO_SETUP(0,1,1,0)
        GPIO_SETUP(0,0,1,0)
        GPIO_SETUP(0,0,1,1)
        GPIO_SETUP(0,0,0,1)
        GPIO_SETUP(1,0,0,1)
        degree -= 1
    GPIO_SETUP(0,0,0,0)

def Fish_Feeder_LTURN(deg):

    full_circle = 510.0
    degree = full_circle/360*deg
    GPIO_SETUP(0,0,0,0)

    while degree > 0.0:
        GPIO_SETUP(1,0,0,1)
        GPIO_SETUP(0,0,0,1)
        GPIO_SETUP(0,0,1,1)
        GPIO_SETUP(0,0,1,0)
        GPIO_SETUP(0,1,1,0)
        GPIO_SETUP(0,1,0,0)
        GPIO_SETUP(1,1,0,0)
        GPIO_SETUP(1,0,0,0)
        degree -= 1
    GPIO_SETUP(0,0,0,0)

#------------------------------------------------------
