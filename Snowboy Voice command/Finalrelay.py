import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(14,GPIO.OUT) #Relay IN4 for Ligth
GPIO.setup(15,GPIO.OUT) #Relay IN3 for Pump_1
GPIO.setup(8,GPIO.OUT)  #Relay IN2 for Pump_2
GPIO.setup(7,GPIO.OUT)  #Relay IN1 for Cooler_Fan


def Ligth_On():
      GPIO.output(14,GPIO.LOW)
      

def Ligth_Off():
      GPIO.output(14,GPIO.HIGH)

def Pump1_On():
      GPIO.output(15,GPIO.LOW)
      
def Pump1_Off():
      GPIO.output(15,GPIO.HIGH)

def Pump2_On():
      GPIO.output(8,GPIO.LOW)
      
def Pump2_Off():
      GPIO.output(8,GPIO.HIGH)     

def CoolerFan_On():
      GPIO.output(7,GPIO.LOW)
      
def CoolerFan_Off():
      GPIO.output(7,GPIO.HIGH)
      


