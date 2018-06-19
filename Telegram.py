import Sensors
import Actuators
import ControlA
#import LCDandRGB
import Newwebserver
import datetime
import time
from ubidots import ApiClient
import telepot
import serial
from datetime import datetime
import threading
import sys
import pigpio
import time
import os
import MySQLdb
from time import strftime
pi = pigpio.pi()

set = 3

def handle(msg):
    global chat_id
    chat_id = msg['chat']['id']
    print chat_id
    command = msg['text']
    print 'Got command: %s' % command
    db = MySQLdb.connect(user="root", passwd="root", db="RV_Aquarium", host="localhost")
    c=db.cursor()
    c.execute("SELECT mode from Global where id = 3")
    mode = c.fetchone()
    if mode[0] == 0:
        if command.lower() == '/start':
             bot.sendMessage(chat_id,'Welcome to RaashVAqua Aquarium Monitoring System. How I can help you?')
             
        if command.lower() == 'aoff':
            Actuators.stopAll()
            pi.set_PWM_dutycycle(27, 0)
            pi.set_PWM_dutycycle(22, 0)
            pi.set_PWM_dutycycle(17, 0)
           # bot.sendMessage(chat_id,'Actuator is off.')
            serialWrite("Actuator","is off..")
            time.sleep(2)
            serialClear()

        if command.lower() == 'who are you?':
            bot.sendMessage(chat_id,'I am a bot, programmed in the Raspberry Pi')
            
        if command.lower() == 'how old are you?':
            age = datetime.now() - datetime(2017, 1, 1)
            bot.sendMessage(chat_id,'My age is %d days and %d seconds'%(age.days,age.seconds))

        if command.lower() == 'who is your father?' or command.lower() == 'who is your mother?':
            bot.sendMessage(chat_id,'My father and mother is Thiyraash s/o David, a Computer Engineering student from University Tuanku Abdul Rahman')

        if command.lower() == 'what is your function?' or command.lower() == 'your function?':
            bot.sendMessage(chat_id,'My function is to monitor the Aquarium such as its temperature, turbidity,water level  and inform them to the client ')

        if command.lower() == 'red':
              pi.set_PWM_dutycycle(27, 255)
              pi.set_PWM_dutycycle(22, 0) 
              pi.set_PWM_dutycycle(17, 0)
              
        if command.lower() == 'green':
              pi.set_PWM_dutycycle(27, 0)
              pi.set_PWM_dutycycle(22, 255) 
              pi.set_PWM_dutycycle(17, 0)
        if command.lower() == 'blue':
              pi.set_PWM_dutycycle(27, 0)
              pi.set_PWM_dutycycle(22, 0) 
              pi.set_PWM_dutycycle(17, 255)
        if command.lower() == 'yellow':
              pi.set_PWM_dutycycle(27, 255)
              pi.set_PWM_dutycycle(22, 128) 
              pi.set_PWM_dutycycle(17, 0)
        if command.lower() == 'purple':
              pi.set_PWM_dutycycle(27, 255)
              pi.set_PWM_dutycycle(22, 128) 
              pi.set_PWM_dutycycle(17, 128)
        if command.lower() == 'offrgb':
              pi.set_PWM_dutycycle(27, 0)
              pi.set_PWM_dutycycle(22, 0) 
              pi.set_PWM_dutycycle(17, 0)


        
        if command.lower() == 'auto':
            #global set
            db = MySQLdb.connect(user="root", passwd="root", db="RV_Aquarium", host="localhost")
            c=db.cursor()
            c.execute("UPDATE Global SET mode = 0 WHERE id= 1")
            db.commit()
            bot.sendMessage(chat_id,'Auto mode Activated')
            #set = 0
            Actuators.b = 0
            #serialWrite("Auto mode","Activated")
            time.sleep(2)
            
            serialClear()
        if command.lower() == 'manual' :
            #global set
            db = MySQLdb.connect(user="root", passwd="root", db="RV_Aquarium", host="localhost")
            c=db.cursor()
            c.execute("UPDATE Global SET mode = 1 WHERE id= 1")
            db.commit()
            bot.sendMessage(chat_id,'Manual mode Activated')
            #set = 1
            Actuators.b = 1
            #serialWrite("Manual mode","Activated")
            time.sleep(2)
            #serialClear()
            
        if command.lower() == 'lighton':
            db = MySQLdb.connect(user="root", passwd="root", db="RV_Aquarium", host="localhost")
            c=db.cursor()
            c.execute("UPDATE Global SET mode = 0 WHERE id= 11")
            db.commit()
            bot.sendMessage(chat_id,'Ligth is on')
            Actuators.Ligth_On()
            #serialWrite("Light is","Switch On")
            time.sleep(3)
            
            #serialClear()
            
        elif command.lower() == 'lightoff':
            db = MySQLdb.connect(user="root", passwd="root", db="RV_Aquarium", host="localhost")
            c=db.cursor()
            c.execute("UPDATE Global SET mode = 1 WHERE id= 11")
            db.commit()
            bot.sendMessage(chat_id, 'Ligth is off')
            Actuators.Ligth_Off()
            #serialWrite("Light is","Switch Off")
            time.sleep(2)
            #serialClear()
            
        elif command.lower() == 'emptytank':
            bot.sendMessage(chat_id, 'Emptying the Tank')
            ControlA.TankEmpty()
            #serialWrite("Emptying","the tank")
            time.sleep(2)
            #serialClear()

            
        elif command.lower() == 'filltank':
            db = MySQLdb.connect(user="root", passwd="root", db="RV_Aquarium", host="localhost")
            c=db.cursor()
            c.execute("UPDATE Global SET mode = 0 WHERE id= 12")
            db.commit()
            bot.sendMessage(chat_id, 'Filling the tank')
            ControlA.TankFill()
            #serialWrite("Tank is","fiiling")
            time.sleep(2)
            #serialClear()
            
        elif command.lower() == 'fanon':
            global p
            global f
            p=1
            if f ==1:
                     bot.sendMessage(chat_id, 'Switch off the pumps first before turn on the cooling fan')
                     pi.set_PWM_dutycycle(27, 255)
            else:
                    db = MySQLdb.connect(user="root", passwd="root", db="RV_Aquarium", host="localhost")
                    c=db.cursor()
                    c.execute("UPDATE Global SET mode = 0 WHERE id= 14")
                    db.commit()
                    bot.sendMessage(chat_id, 'Cooling Fan is on')
                    pi.set_PWM_dutycycle(27, 0)
                    Actuators.CoolerFan_On()
                   # serialWrite("Cooling Fan is","Switch On")
                    time.sleep(2)
            
                    serialClear()
                    
                    
            
            
        elif command.lower() == 'fanoff':
            global p
            p=0
            db = MySQLdb.connect(user="root", passwd="root", db="RV_Aquarium", host="localhost")
            c=db.cursor()
            c.execute("UPDATE Global SET mode = 1 WHERE id= 14")
            db.commit()
            bot.sendMessage(chat_id, 'Cooling Fan is off')
            pi.set_PWM_dutycycle(27, 0)
            Actuators. CoolerFan_Off()
            #serialWrite("Cooling Fan is","Switch Off")
            time.sleep(2)
            
            serialClear()
        elif command.lower() == 'pump1on':
            global p
            global f
            f=1
            if p == 1:
                    bot.sendMessage(chat_id, 'Switch off the Cooling Fan first before turn on the pump')
                    pi.set_PWM_dutycycle(27, 255)
            else:
                    db = MySQLdb.connect(user="root", passwd="root", db="RV_Aquarium", host="localhost")
                    c=db.cursor()
                    c.execute("UPDATE Global SET mode = 0 WHERE id= 12")
                    db.commit()
                    bot.sendMessage(chat_id, 'Pump 1 is on')
                    pi.set_PWM_dutycycle(27, 0)
                    Actuators.Pump1_On()
             #       serialWrite("Pump 1 is","Switch On")
                    time.sleep(2)
            
            #        serialClear()
      
            
        elif command.lower() == 'pump1off':
            global f
            f=0
            db = MySQLdb.connect(user="root", passwd="root", db="RV_Aquarium", host="localhost")
            c=db.cursor()
            c.execute("UPDATE Global SET mode = 1 WHERE id= 12")
            db.commit()    
            bot.sendMessage(chat_id, 'Pump 1 is off')
            Actuators.Pump1_Off()
            #serialWrite("Pump 1 is","Switch Off")
            time.sleep(2)
            
           # serialClear()

        elif command.lower() == 'pump2on':
            global p
            global f
            f=1
            if p == 1:
                 bot.sendMessage(chat_id, 'Switch off the Cooling Fan first before turn on the pump')
                 pi.set_PWM_dutycycle(27, 255)
                 
            else:
                     db = MySQLdb.connect(user="root", passwd="root", db="RV_Aquarium", host="localhost")
                     c=db.cursor()
                     c.execute("UPDATE Global SET mode = 0 WHERE id= 13")
                     db.commit()  
                     bot.sendMessage(chat_id, 'Pump 2 is on')
                     Actuators.Pump2_On()
             #        serialWrite("Pump 2 is","Switch On")
                     time.sleep(2)
            
              #       serialClear()
                    
           
            
        elif command.lower() == 'pump2off':
            global f
            f=0
            db = MySQLdb.connect(user="root", passwd="root", db="RV_Aquarium", host="localhost")
            c=db.cursor()
            c.execute("UPDATE Global SET mode = 1 WHERE id= 13")
            db.commit()
            bot.sendMessage(chat_id, 'Pump 2 is off')
            Actuators.Pump2_Off()
            #serialWrite("Pump 2 is","Switch Off")
            time.sleep(2)
            
           # serialClear()



            
        elif command.lower() == 'feed':
            bot.sendMessage(chat_id, 'Feeding')
            #serialWrite("Feeding the","Fish")
            Actuators.Fish_Feeder_RTURN(360)
            time.sleep(2)
            
            serialClear()
        elif command.lower() == 'temp' or command.lower() == 'temperature':
            W_temp=Sensors.read_temp()
            #W_temp=str(W_temp)
            bot.sendMessage(chat_id, 'The Temperature of water :%s C'%W_temp)


        elif command.lower() == 'tur' or command.lower() == 'turbidity':
              TUR_level = Sensors.ReadChannel(Sensors.Turbidity_channel)
              if TUR_level >=ControlA.Out_TurB1 and TUR_level<ControlA.Out_TurB1:
                w = "Sensor is out off water"
          
              elif TUR_level >= ControlA.CLO_TurB1 and TUR_level <ControlA.CLO_TurB2:
                w = "WAter is dirty"
                
              elif TUR_level >=ControlA.C_TurB1 :
               w = "WAter is clear"
          
              else:
                w =  "Opague object detected between the sensor"
                
              bot.sendMessage(chat_id,'The Turbidity :%s' %w)


            
        elif command.lower() == 'summary':
            bot.sendMessage(chat_id, 'The Temperature of water is (C):')
            W_temp=Sensors.read_temp()
            bot.sendMessage(chat_id, W_temp)
            bot.sendMessage(chat_id, 'The Turbidity of water is :')
            TUR_level = Sensors.ReadChannel(Sensors.Turbidity_channel)
            bot.sendMessage(chat_id,TUR_level)
            
        elif command.lower() == 'auto' or command.lower() == 'manual' or command.lower() == 'your function?' or command.lower() == 'how old are you?' or command.lower() == 'who are you?'or command.lower() == 'who is your father?' or command.lower() == 'who is your mother?' or command.lower() == '/start' or command.lower() == 'shutdown' or command.lower() == 'bootup':
            #bot.sendMessage(chat_id, '.............')
            ko=2
        else:
            #bot.sendMessage(chat_id, 'The command not in my database.Please check my command list')
            bot.sendMessage(chat_id, ' ')
    else:
        bot.sendMessage(chat_id,'Telegram Control have been deactivate. Please reactivate them through the website.')

bot = telepot.Bot('363410815:AAFuoziE2ipHiuINs95y6oAIIAE0XIG-RSw')
bot.message_loop(handle)
print 'I am listening ...'

