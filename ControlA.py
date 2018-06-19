import Sensors
import Actuators
import datetime
import time
import ActuatorsLogSQL

#--------------------------------------------------------------------------------
#On Ligth from 7pm to 7am
#--------------------------------------------------------------------------------


L_S_HourN=18
L_E_HourN=24
L_S_HourD=1
L_E_HourD=7
L_S_Minute=00
LigthState=0

AquariumHeigth = 22 #18.80
OptimumWaterLevel =6.40   #AquariumHeigth /(100/18)
HalfWaterLevel =   10.5     #AquariumHeigth /(100/30)

Out_TurB2=380
Out_TurB1=290
C_TurB1=420
C_TurB2=440
CLO_TurB1=380
CLO_TurB2=418

W_temp=0.0
Maximum_T=30
Minumum_T=23

count = 3
H_M_T=3
F_S_HourN1=15
F_S_HourN2=18
F_S_HourD1=4
F_S_HourD2=9
F_S_HourD3=12
F_S_Minute=35



leak = 0

def ControlLigth():
 
 CurrentT=datetime.datetime.now()

 if CurrentT >= ActuatorsLogSQL.Light1 and CurrentT < ActuatorsLogSQL.Light2:
      Actuators.Ligth_On()
      print "Ligth On"
 elif CurrentT >= ActuatorsLogSQL.Light3 and CurrentT< ActuatorsLogSQL.Light4:
     Actuators.Ligth_On()
     print "Ligth On"
 else:
     Actuators.Ligth_Off()
     print "Ligth Off"
     
 if LigthState == 1:
     Actuators.Ligth_On()
     print "Ligth On BY USER"

def ControlWaterLevel():
    
 result = Sensors.read_AquaWaterLevel()
 print "Distance: ",result, "cm"

 if result >= OptimumWaterLevel and result < HalfWaterLevel:
       print "Water level is in Optimum Level "
       Actuators.Pump1_Off()
       Actuators.Pump2_Off()
 elif  result >= HalfWaterLevel and result < AquariumHeigth:
       print "Water level very low. Pump 2 is on to fill the tank"
       Actuators.Pump2_On()
       #Actuators.Pump1_Off()
 elif result < OptimumWaterLevel:
       print "Water level too high. Pump 1 is on to reduce the tank"
       #Actuators.Pump1_On()
       #Actuators.Pump2_Off()

 elif result > AquariumHeigth:
       print "out of range"
       Actuators.Pump1_Off()
       Actuators.Pump2_Off()
 else :
    print "something wrong"


def TankEmpty():
    while True:
          Actuators.Pump1_On()
          print "pump 1 on"
          result1 = Sensors.read_AquaWaterLevel()
          if result1 >= (AquariumHeigth-3) :
              print "Tank is empty"
              Actuators.Pump1_Off()
              break

def TankFill():
     while True:
          Actuators.Pump2_On()
          print "pump 2 on"
          result2 = Sensors.read_AquaWaterLevel()
          if result2 == OptimumWaterLevel  :
              print "Tank is full"
              Actuators.Pump2_Off()
              break


def ChangeTankWAter():
     print "WAter is dirty.Need to change water"
     TankEmpty()
     print "Tank fill process start"
     time.sleep(0.25)
     TankFill()
     time.sleep(0.25)

   
def ControlTurbidity():
  TUR_level = Sensors.ReadChannel(Sensors.Turbidity_channel)
  TUR_volts = Sensors.ConvertVolts(TUR_level,2)
  print TUR_level
  if TUR_level >=Out_TurB1 and TUR_level<Out_TurB2:
      print "Sensor is out off water"
      
  elif TUR_level >= CLO_TurB1 and TUR_level <CLO_TurB2:
      print "WAter is dirty"
      ChangeTankWAter()
  elif TUR_level >=C_TurB1 :
      print "WAter is clear"
      
  else:
      print "Opague object detected between the sensor"


def ControlW_Temperature():
    
  W_temp=Sensors.read_temp()
  print "Water Temperature :",W_temp

  if W_temp > Maximum_T:
    Actuators.CoolerFan_On()
    print "Cooler fan is On"
  elif W_temp <Minumum_T:
    print "Heater is On"
    Actuators.CoolerFan_Off()
  elif W_temp >=Minumum_T and W_temp < Maximum_T:
    print "Water Temperature is Optimum"
    Actuators.CoolerFan_Off()
    
def ControlFishFeeder():
   Current_T=datetime.datetime.now()
   global count
   global H_M_T
   
   if Current_T == ActuatorsLogSQL.Feed_Time1 and count <  H_M_T:
       Actuators.Fish_Feeder_RTURN(360)
       count+=1
       print "FEEDING"
       
   elif Current_T == ActuatorsLogSQL.Feed_Time1:
       print "Feed two times dy"
       
   elif Current_T == ActuatorsLogSQL.Feed_Time2 and count <  H_M_T:
       Actuators.Fish_Feeder_RTURN(360)
       count+=1
       print "FEEDING"
       
   elif Current_T == ActuatorsLogSQL.Feed_Time2:
       print "Feed two times dy"
       
   elif  Current_T == ActuatorsLogSQL.Feed_Time3 and count <  H_M_T:
       Actuators.Fish_Feeder_RTURN(360)
       count+=1
       print "FEEDING"
       
   elif Current_T == ActuatorsLogSQL.Feed_Time3 :
       print "Feed two times dy"
       
   elif Current_T == ActuatorsLogSQL.Feed_Time4 and count <  H_M_T:
       Actuators.Fish_Feeder_RTURN(360)
       count+=1
       print "FEEDING"
       
   elif Current_T == ActuatorsLogSQL.Feed_Time4 :
       print "Feed two times dy"


   elif Current_T == ActuatorsLogSQL.Feed_Time4 and count <  H_M_T:
       Actuators.Fish_Feeder_RTURN(360)
       count+=1
       print "FEEDING"
       
   elif Current_T == ActuatorsLogSQL.Feed_Time5 :
       print "Feed two times dy"

   else:
       count=0;
        
#   print str(ActuatorsLogSQL.Feed_Time1)
#   print str(ActuatorsLogSQL.Feed_Time2)
#   print str(ActuatorsLogSQL.Feed_Time3)
#   print str(ActuatorsLogSQL.Feed_Time4)
#   print str(ActuatorsLogSQL.Feed_Time5)

     
#   print str(ActuatorsLogSQL.Light1)
#   print str(ActuatorsLogSQL.Light2)
#   print str(ActuatorsLogSQL.Light3)
#   print str(ActuatorsLogSQL.Light4)
   

    
def Water_Leak():
    state = Sensors.GPIO.input(26)
    if state == Sensors.GPIO.HIGH:
          global leak
          leak =1         
   
          
    else:
      global leak
      leak = 0
      

