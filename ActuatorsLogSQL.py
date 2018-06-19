import mysql.connector
import time
import datetime



now = datetime.datetime.now()
con = mysql.connector.connect(user='root',password='root',host='localhost',database='RV_Aquarium')
cur = con.cursor()
cur.execute("select Feed_Time,Light_Time from ActuatorLog  ")
results = cur.fetchall()
Feed1,Light1 = results[0]
Feed2,Light2 = results[1]
Feed3,Light3 = results[2]
Feed4,Light4 = results[3]
Feed5,Light5 = results[4]

     

Feed_Time1= datetime.datetime.strptime(str(Feed1), "%H:%M:%S")
Feed_Time1 = now.replace(hour=Feed_Time1.time().hour, minute=Feed_Time1.time().minute, second=Feed_Time1.time().second, microsecond=0)


Light1= datetime.datetime.strptime(str(Light1), "%H:%M:%S")
Light1 = now.replace(hour=Light1.time().hour, minute=Light1.time().minute, second=Light1.time().second, microsecond=0)

Feed_Time2= datetime.datetime.strptime(str(Feed2), "%H:%M:%S")
Feed_Time2 = now.replace(hour=Feed_Time2.time().hour, minute=Feed_Time2.time().minute, second=Feed_Time2.time().second, microsecond=0)


Light2= datetime.datetime.strptime(str(Light2), '%H:%M:%S')
Light2 = now.replace(hour=Light2.time().hour, minute=Light2.time().minute, second=Light2.time().second, microsecond=0)


Feed_Time3= datetime.datetime.strptime(str(Feed3), "%H:%M:%S")
Feed_Time3 = now.replace(hour=Feed_Time3.time().hour, minute=Feed_Time3.time().minute, second=Feed_Time3.time().second, microsecond=0)

Light3= datetime.datetime.strptime(str(Light3), "%H:%M:%S")
Light3 = now.replace(hour=Light3.time().hour, minute=Light3.time().minute, second=Light3.time().second, microsecond=0)


Feed_Time4= datetime.datetime.strptime(str(Feed4), "%H:%M:%S")
Feed_Time4 = now.replace(hour=Feed_Time4.time().hour, minute=Feed_Time4.time().minute, second=Feed_Time4.time().second, microsecond=0)

Light4= datetime.datetime.strptime(str(Light4), "%H:%M:%S")
Light4 = now.replace(hour=Light4.time().hour, minute=Light4.time().minute, second=Light4.time().second, microsecond=0)


Feed_Time5= datetime.datetime.strptime(str(Feed5), "%H:%M:%S")
Feed_Time5 = now.replace(hour=Feed_Time5.time().hour, minute=Feed_Time5.time().minute, second=Feed_Time5.time().second, microsecond=0)



   
cur.close()
