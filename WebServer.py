from flask import Flask, render_template, redirect, url_for, flash,request , jsonify, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

import Sensors
import Actuators
import ControlA
import pigpio
import os
import glob
import time
import random
from threading import Thread
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
co = 0
k = 0
y=0
p=0
f=0
w = 0


#start serial conection with arduino
ser = serial.Serial('/dev/ttyACM0', 9600)
TUR_level=0
betWait = 1 #wait before sending second string cant go lower than 1 because of arduino StringRead timeout
sleepTime = 3 #wait before sending next batch of info


#SQL INITIAL SETUP
####################################################################
# Variables for MySQL
db = MySQLdb.connect(host="localhost", user="root",passwd="root", db="RV_Aquarium")
cur = db.cursor()
####################################################################







s = URLSafeTimedSerializer('Thisisasecret!')
app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/RV_Aquarium'
app.config['CSRF_ENABLED'] = True 
app.config['USER_ENABLE_EMAIL'] = True 
app.config.from_pyfile('config.cfg')
mail = Mail(app)
Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    confirmed_at = db.Column(db.DateTime())

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])

class PasswordReset(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])

class PasswordResetToken(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])


class ChangePassword(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    Oldpass = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    Newpass = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])




@app.route('/')
def index():
    return render_template('Findex.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error= None
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))

        error =  'Invalid username or password'
        #return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'

    return render_template('login.html', form=form , error = error )

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    global new_user
    error = None
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        email = User.query.filter_by(email=form.email.data).first()
        if user is None and email is None:

            email = form.email.data
            token = s.dumps(email, salt='email-confirm')

            msg = Message('Confirm Email', sender='anthony@prettyprinted.com', recipients=[email])

            link = url_for('confirm_email', token=token, _external=True)

            msg.body = 'Your link is {}'.format(link)

            mail.send(msg)
            
            hashed_password = generate_password_hash(form.password.data, method='sha256')
            new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)

            return render_template('signupE.html',form = form)

            
        
#            hashed_password = generate_password_hash(form.password.data, method='sha256')
#            new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
#            db.session.add(new_user)
#            db.session.commit()
        else:
            #
            error = 'Username of password has been taken. Try another'
            #return redirect(url_for('signup'))

        #return '<h1>New user has been created!</h1>'
        #return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

    return render_template('signup.html', form=form, error = error)


@app.route('/confirm_email/<token>')
def confirm_email(token):
    global new_user
    form = RegisterForm()
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
    except SignatureExpired:
        return '<h1>The token is expired!</h1>'

#    hashed_password = generate_password_hash(form.password.data, method='sha256')
#    new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    #return redirect(url_for('login'))
    return render_template('loginE.html',form = form)


@app.route('/reset', methods=['GET', 'POST'])
def reset():
    form = PasswordReset()
    global newPass
    global emailChange
    error =None
    if form.validate_on_submit():
        
        user = User.query.filter_by(username=form.username.data).first()
        email = User.query.filter_by(email=form.email.data).first()
        if user is not None:
             
            emailChange = form.email.data
            newPass = form.password.data
            token = s.dumps(emailChange, salt='recovery-key')

            msg = Message('Password Reset', sender='raashvaqua@gmail.com', recipients=[emailChange])

            link = url_for('reset_with_token', token=token, _external=True)

            msg.body = 'Your link is {}'.format(link)

            mail.send(msg)
            
           # hashed_password = generate_password_hash(form.password.data, method='sha256')
            #passchange = User(username=form.username.data, email=form.email.data, password=hashed_password)
             
            #return '<h1>A message been send to you email. Please copy paste the token to you browser to reset and change the password</h1>' 
            return render_template('resetE.html', form=form) 

        else:
             error = 'User not found in database. Please sign up first'
             
     
    return render_template('reset.html', form=form, error = error)
         
         
 
@app.route('/reset_with_token/<token>')
def reset_with_token(token):
    
    global newPass
    global emailChange
    form = PasswordResetToken()
    
    try:
        email = s.loads(token, salt='recovery-key', max_age=3600)
    
    except SignatureExpired:
        return '<h1>The token is expired!</h1>'



    
    user = User.query.filter_by(email=emailChange).first()

    user.password = generate_password_hash(newPass, method='sha256')

    db.session.add(user)
    db.session.commit()

    return redirect(url_for('login'))



@app.route('/profile', methods=['GET', 'POST'])
def profile():
    form = ChangePassword()
    global oldpass
    global newpass
    global email1
    error =None
    if form.validate_on_submit():
        user = User.query.filter_by(username=current_user.username).first()
        check_password_hash(user.password, form.password.data)
        print "This is email:",email
        if user:
            newpass = form.Newpass.data
            if check_password_hash(user.password,form.Oldpass.data):
                
                token = s.dumps(user.email, salt='recovery-key')

                msg = Message('Change Password', sender='raashvaqua@gmail.com', recipients=[user.email])

                link = url_for('reset_with_token', token=token, _external=True)

                msg.body = 'Your link is {}'.format(link)

                mail.send(msg)
                
               # hashed_password = generate_password_hash(form.password.data, method='sha256')
                #passchange = User(username=form.username.data, email=form.email.data, password=hashed_password)
                 
                #return '<h1>A message been send to you email. Please copy paste the token to you browser to reset and change the password</h1>' 
                return render_template('resetE.html', form=form)
            else:
                print "incorrect"

        else:
             error = 'User not found in database. Please sign up first'
             
     
    return render_template('Profile.html', form=form, error = error)
         

















@app.route('/dashboard')
@login_required
def dashboard():
    return render_template("DamFinalDash.html", name=current_user.username)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
 
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'
 


 
def serialClear():
	ser.write("00clr")
	
def serialWrite(Line1, Line2):
	serialClear();
	time.sleep(betWait)
	ser.write("00"+Line1)
	time.sleep(betWait)
	ser.write("01"+Line2)
	

def alertFlash(e, t):
    while not e.isSet():
        pi.set_PWM_dutycycle(27, 255)
        time.sleep(0.2)
        pi.set_PWM_dutycycle(27, 0)
        time.sleep(0.2)
        event_is_set = e.wait(t)
        if event_is_set:
            pi.set_PWM_dutycycle(27, 0)
        else:
            pi.set_PWM_dutycycle(27, 255)
            time.sleep(0.2)
            pi.set_PWM_dutycycle(27, 0)
            time.sleep(0.2)



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
        temp_cA = float(temp_string) / 1000.0
        temp_f = temp_cA * 9.0 / 5.0 + 32.0
        return temp_cA

@app.route("/_temp" ,methods = ['GET'])
def temp():
    temp_a = read_temp()
    print(temp_a)
    return jsonify(temp_a = temp_a)



@app.route("/_tur" ,methods = ['GET'])
def tur():
    level = 0
    for x in range(0,10):
          tur = Sensors.ReadChannel(Sensors.Turbidity_channel)
          level = level + tur
    level = level/10
    print(tur)
    return jsonify(tur = int(level))


@app.route("/_level" ,methods = ['GET'])
def level():
   # level = 0
    #for x in range(0,10):
             
    val = Sensors.read_AquaWaterLevel()
    #     level = level +  val
    #level = level/10
   
    return jsonify(level = int(val))


# ajax GET call this function to set led state
# depeding on the GET parameter sent
@app.route("/_Light")
def _Light():
    state = request.args.get('state')
    if state=="on":
        db = MySQLdb.connect(user="root", passwd="root", db="RV_Aquarium", host="localhost")
        c=db.cursor()
        c.execute("UPDATE Global SET mode = 0 WHERE id= 11")
        db.commit()
        Actuators.Ligth_On()    
    else:
        db = MySQLdb.connect(user="root", passwd="root", db="RV_Aquarium", host="localhost")
        c=db.cursor()
        c.execute("UPDATE Global SET mode = 1 WHERE id= 11")
        db.commit()
        Actuators.Ligth_Off()
    return ""

@app.route("/_PumpFill")
def _PumpFill():
    state = request.args.get('state')
    if state=="on":
        db = MySQLdb.connect(user="root", passwd="root", db="RV_Aquarium", host="localhost")
        c=db.cursor()
        c.execute("UPDATE Global SET mode = 0 WHERE id= 12")
        db.commit()
        Actuators.Pump1_On()
    else:
        db = MySQLdb.connect(user="root", passwd="root", db="RV_Aquarium", host="localhost")
        c=db.cursor()
        c.execute("UPDATE Global SET mode = 1 WHERE id= 12")
        db.commit()    
        Actuators.Pump1_Off()

    return ""

@app.route("/_PumpUnFill")
def _PumpUnFill():
    state = request.args.get('state')
    if state=="on":
          db = MySQLdb.connect(user="root", passwd="root", db="RV_Aquarium", host="localhost")
          c=db.cursor()
          c.execute("UPDATE Global SET mode = 0 WHERE id= 13")
          db.commit()  
          Actuators.Pump2_On()
    else:
          db = MySQLdb.connect(user="root", passwd="root", db="RV_Aquarium", host="localhost")
          c=db.cursor()
          c.execute("UPDATE Global SET mode = 1 WHERE id= 13")
          db.commit()
          Actuators.Pump2_Off()
    return ""

@app.route("/_CoolerFan")
def _CoolerFan():
    state = request.args.get('state')
    if state=="on":
        db = MySQLdb.connect(user="root", passwd="root", db="RV_Aquarium", host="localhost")
        c=db.cursor()
        c.execute("UPDATE Global SET mode = 0 WHERE id= 14")
        db.commit()
        Actuators.CoolerFan_On()
    else:
        db = MySQLdb.connect(user="root", passwd="root", db="RV_Aquarium", host="localhost")
        c=db.cursor()
        c.execute("UPDATE Global SET mode = 1 WHERE id= 14")
        db.commit()
        Actuators.CoolerFan_Off()
    return ""


@app.route("/_Feed")
def _Feed():
       state = request.args.get('state')
       if state =="feed":
               Actuators.Fish_Feeder_RTURN(360)

@app.route("/_CLight")
def _CLight():
       global CL
       state = request.args.get('state')
       if state =="on":
                db = MySQLdb.connect(user="root", passwd="root", db="RV_Aquarium", host="localhost")
                c=db.cursor()
                c.execute("UPDATE Global SET mode = 0 WHERE id= 5")
                db.commit()
       else:
                db = MySQLdb.connect(user="root", passwd="root", db="RV_Aquarium", host="localhost")
                c=db.cursor()
                c.execute("UPDATE Global SET mode = 1 WHERE id= 5")
                db.commit()



@app.route("/_CFeed")
def _CFeed():
       global CF
       state = request.args.get('state')
       if state =="on":
                db = MySQLdb.connect(user="root", passwd="root", db="RV_Aquarium", host="localhost")
                c=db.cursor()
                c.execute("UPDATE Global SET mode = 0 WHERE id= 6")
                db.commit()
       else:
                db = MySQLdb.connect(user="root", passwd="root", db="RV_Aquarium", host="localhost")
                c=db.cursor()
                c.execute("UPDATE Global SET mode = 1 WHERE id= 6")
                db.commit()


@app.route("/_CLeak")
def _CLeak():
       global CLE
       state = request.args.get('state')
       if state =="on":
                db = MySQLdb.connect(user="root", passwd="root", db="RV_Aquarium", host="localhost")
                c=db.cursor()
                c.execute("UPDATE Global SET mode = 0 WHERE id= 7")
                db.commit()
       else:
                db = MySQLdb.connect(user="root", passwd="root", db="RV_Aquarium", host="localhost")
                c=db.cursor()
                c.execute("UPDATE Global SET mode = 1 WHERE id= 7")
                db.commit()
               
@app.route("/_CTur")
def _CTur():
       global CTU
       state = request.args.get('state')
       if state =="on":
                db = MySQLdb.connect(user="root", passwd="root", db="RV_Aquarium", host="localhost")
                c=db.cursor()
                c.execute("UPDATE Global SET mode = 0 WHERE id= 8")
                db.commit()
       else:
                db = MySQLdb.connect(user="root", passwd="root", db="RV_Aquarium", host="localhost")
                c=db.cursor()
                c.execute("UPDATE Global SET mode = 1 WHERE id= 8")
                db.commit()

               
@app.route("/_CTemp")
def _CTemp():
       global CT
       state = request.args.get('state')
       if state =="on":
                db = MySQLdb.connect(user="root", passwd="root", db="RV_Aquarium", host="localhost")
                c=db.cursor()
                c.execute("UPDATE Global SET mode = 0 WHERE id= 9")
                db.commit()
       else:
                db = MySQLdb.connect(user="root", passwd="root", db="RV_Aquarium", host="localhost")
                c=db.cursor()
                c.execute("UPDATE Global SET mode = 1 WHERE id= 9")
                db.commit()

               
@app.route("/_CLevel")
def _CLevel():
       global CWL
       state = request.args.get('state')
       if state =="on":
                db = MySQLdb.connect(user="root", passwd="root", db="RV_Aquarium", host="localhost")
                c=db.cursor()
                c.execute("UPDATE Global SET mode = 0 WHERE id= 10")
                db.commit()
       else:
                db = MySQLdb.connect(user="root", passwd="root", db="RV_Aquarium", host="localhost")
                c=db.cursor()
                c.execute("UPDATE Global SET mode = 1 WHERE id= 10")
                db.commit()


               
@app.route("/_Tele")
def _Tele():    
       state = request.args.get('state')
       if state =="on":
            db = MySQLdb.connect(user="root", passwd="root", db="RV_Aquarium", host="localhost")
            c=db.cursor()
            c.execute("UPDATE Global SET mode = 0 WHERE id= 3")
            db.commit()

       else:
            db = MySQLdb.connect(user="root", passwd="root", db="RV_Aquarium", host="localhost")
            c=db.cursor()
            c.execute("UPDATE Global SET mode = 1 WHERE id= 3")
            db.commit()


@app.route("/_Telegram")
def _Telegram():
        return render_template("TeleBot.html",name=current_user.username)                



               
@app.route("/_Voice")
def _Voice():    
       state = request.args.get('state')
       if state =="on":
            db = MySQLdb.connect(user="root", passwd="root", db="RV_Aquarium", host="localhost")
            c=db.cursor()
            c.execute("UPDATE Global SET mode = 0 WHERE id= 4")
            db.commit()

       else:
            db = MySQLdb.connect(user="root", passwd="root", db="RV_Aquarium", host="localhost")
            c=db.cursor()
            c.execute("UPDATE Global SET mode = 1 WHERE id= 4")
            db.commit()


@app.route("/_VoiceControl")
def _VoiceControl():
        return render_template("Snowboy.html",name=current_user.username)                






@app.route("/_Mode")
def _Mode():
    state = request.args.get('state')
    global set
    if state=="auto":
        db = MySQLdb.connect(user="root", passwd="root", db="RV_Aquarium", host="localhost")
        c=db.cursor()
        c.execute("UPDATE Global SET mode = 0 WHERE id= 1")
        db.commit()
        c.execute("SELECT mode from Global where id = 1")
        mode = c.fetchone()
        #global set
        print "from mode loop"
        print mode[0]

        #global a
        #FullFinalCodeWithSQLTELEGRAMUNIDOTSLCD.set = 0;
        #print 'From server'
        set = 0
        #print (FullFinalCodeWithSQLTELEGRAMUNIDOTSLCD.set)
    else:
        db = MySQLdb.connect(user="root", passwd="root", db="RV_Aquarium", host="localhost")
        c1=db.cursor()
        c1.execute("UPDATE Global SET mode = 1 WHERE id = 1")
        db.commit()
        #global a
        #FullFinalCodeWithSQLTELEGRAMUNIDOTSLCD.set=1;
        #print 'From server'
        set = 1
        #print (FullFinalCodeWithSQLTELEGRAMUNIDOTSLCD.set)
    return ""



@app.route("/_Toggle" ,methods = ['GET'])
def Toggle():
    db = MySQLdb.connect(user="root", passwd="root", db="RV_Aquarium", host="localhost")
    c=db.cursor()
    c.execute("SELECT mode from Global where id = 1")
    mode = c.fetchone()
    c.execute("SELECT mode from Global where id = 5")
    light = c.fetchone()
    c.execute("SELECT mode from Global where id = 6")
    feed = c.fetchone()
    c.execute("SELECT mode from Global where id = 7")
    leak = c.fetchone()
    c.execute("SELECT mode from Global where id = 8")
    tur = c.fetchone()
    c.execute("SELECT mode from Global where id = 9")
    temp = c.fetchone()
    c.execute("SELECT mode from Global where id = 10")
    level = c.fetchone()
    c.execute("SELECT mode from Global where id = 11")
    light1 = c.fetchone()
    c.execute("SELECT mode from Global where id = 12")
    fill = c.fetchone()
    c.execute("SELECT mode from Global where id = 13")
    unfill = c.fetchone()
    c.execute("SELECT mode from Global where id = 14")
    fan = c.fetchone()
    return jsonify(AU = mode[0] , light = light[0] , feed = feed[0],leak = leak[0],tur = tur[0], temp=temp[0],level=level[0],light1 = light1[0] ,fill=fill[0],unfill=unfill[0] , fan=fan[0])










@app.route("/_Live")
def _LiveVideo():
        return render_template("LiveVideo.html",name=current_user.username) 


@app.route("/_Chart")
def _Chart():
        return render_template("SensorLiveChart.html",name=current_user.username)


@app.route('/sliderR')
def slide():
    a = request.args.get('a')
 
    pi.set_PWM_dutycycle(27, a)
 
@app.route('/sliderG')
def slideG():
    b = request.args.get('b')
 
    pi.set_PWM_dutycycle(22, b)
    
@app.route('/sliderBL')
def slideB():
    c = request.args.get('c')
    pi.set_PWM_dutycycle(17, c)
    

@app.route('/about')
def about():
        return render_template("AboutF.html")



@app.route('/search', methods=['GET', 'POST'])
def searchD():
    if request.method == "POST":
        db = MySQLdb.connect(user="root", passwd="root", db="RV_Aquarium", host="localhost")
        c=db.cursor()
        #cur = mysql.connection.cursor()
        input1 =''.join(request.form["search"],)
        input2 =''.join(request.form["search1"],)
        if not input1 or not input2:
            c.execute('''SELECT * from SensorsLog''')
        #c.executemany('''SELECT * from SensorsLog WHERE datetime = %s''', request.form['search'])
        else:
            c.execute("SELECT * from SensorsLog WHERE datetime BETWEEN %s AND %s",((request.form['search'],),(request.form['search1'],)))
        #cur.executemany('''SELECT * from SensorsLog WHERE datetime = %s''',request.form['search'])
        rows = [dict(text3=row[0], text=row[1] , text1=row[2] , text4=row[3]) for row in c.fetchall()]
        return render_template("DataQuery.html", name=current_user.username, rows=rows, fromD = input1, ToD = input2 )
    return render_template('DataQuery.html',name=current_user.username)




@app.route('/update', methods=['GET', 'POST'])
def updateD():
     db = MySQLdb.connect(user="root", passwd="root", db="RV_Aquarium", host="localhost")
     c=db.cursor()
     c.execute('''SELECT * from ActuatorLog''')
     rows = [dict(text3=row[0], text=row[1] , text1=row[2]) for row in c.fetchall()]
     
     if request.method == "POST":
                timeformat  = "%H:%M:%S"
                db = MySQLdb.connect(user="root", passwd="root", db="RV_Aquarium", host="localhost")
                c=db.cursor()
                        #cur = mysql.connection.cursor()
                input1 =''.join(request.form["ex1"],)
                input2 =''.join(request.form["ex2"],)
                try:
                        validtime = datetime.strptime(input2, timeformat)
                        c.execute("UPDATE ActuatorLog SET Feed_Time = %s WHERE id= %s",((request.form['ex2'],),(request.form['ex1'],)))
                        db.commit()
                        c.execute('''SELECT * from ActuatorLog''')
                        rows = [dict(text3=row[0], text=row[1] , text1=row[2]) for row in c.fetchall()]
                        return render_template("ASetting.html", name=current_user.username, rows=rows, fromD = input1, ToD = input2)
                except ValueError:
                        print ("kokoi")
     return render_template('ASetting.html',rows = rows ,name=current_user.username)







def Twhile():
        db = MySQLdb.connect(user="root", passwd="root", db="RV_Aquarium", host="localhost")
        c=db.cursor()    
        while True:   
          c.execute("SELECT mode from Global where id = 1")
          mode = c.fetchone()
          c.execute("SELECT mode from Global where id = 5")
          light = c.fetchone()
          c.execute("SELECT mode from Global where id = 6")
          feed = c.fetchone()
          c.execute("SELECT mode from Global where id = 7")
          leak = c.fetchone()
          c.execute("SELECT mode from Global where id = 8")
          tur = c.fetchone()
          c.execute("SELECT mode from Global where id = 9")
          temp = c.fetchone()
          c.execute("SELECT mode from Global where id = 10")
          level = c.fetchone()
          if (mode[0]==0):
             global co
             global leak
             chat_id = 340252170
             if (temp[0] == 0):
                     ControlA.ControlW_Temperature()
             if (tur[0] == 0):
                     ControlA.ControlTurbidity()
             if (light[0] == 0):   
                     ControlA.ControlLigth()
             if (level[0] == 0):
                     ControlA.ControlWaterLevel()
             if (feed[0] == 0):
                     ControlA.ControlFishFeeder()
             if (leak[0] == 0):
                     ControlA.Water_Leak()

             if ControlA.leak == 1:
                global k
                if co<5:     
                   # bot.sendMessage(chat_id, 'Water leak detected!! Please check the aquarium:')
                   print "water leak"
                co=co+1
                if k == 0:
                        global y
                        e = threading.Event()
                        t = threading.Thread(name='non-block', target=alertFlash, args=(e, 0.2))
                        t.start()
                        y=1
                k=k+1
                serialWrite("Water leak ","Detected!!!")
                time.sleep(2)
                serialClear()
             else:
                  global k
                  global t
                  if y ==1:
                    e.set()
                    k=0
                    y=0
                  co=0
          elif (mode[0]==1):
            print "  "
            
            
          elif(mode[0] == 4):
             Actuators.stopAll()
             pi.set_PWM_dutycycle(27, 0)
             pi.set_PWM_dutycycle(22, 0)
             pi.set_PWM_dutycycle(17, 0)
          else:
                  print " "
          
          result = Sensors.read_AquaWaterLevel()
          #result=str(result)
          #serialWrite("WaterLevel :",result)
          #time.sleep(2)
          #serialClear()
                
          TUR_level = Sensors.ReadChannel(Sensors.Turbidity_channel)
          #TUR_level=str(TUR_level)
          #serialWrite("Turbidity ",TUR_level)
          #time.sleep(2)
          #serialClear()
          
          W_temp=Sensors.read_temp()
          #W_temp=str(W_temp)
          #serialWrite("Temperature ",W_temp)
          #time.sleep(2)
          #serialClear()

          datetimeWrite = (time.strftime("%Y-%m-%d ") + time.strftime("%H:%M:%S"))
         # print datetimeWrite
          sql = ("""INSERT INTO SensorsLog(datetime,Water_Temperature, Water_Turbidity,Water_Level) VALUES (%s,%s,%s,%s)""",(datetimeWrite,W_temp,TUR_level ,result))
          try:
                #print "Writing to database..."
                # Execute the SQL command
                cur.execute(*sql)
                # Commit your changes in the database
                db.commit()
                #print "Write Complete"
         
          except:
                # Rollback in case there is any error
                db.rollback()
                print "Failed writing to database"
         



          

#          api.save_collection([
#            {'variable': '58c9993476254236fa9b9c5f', 'value': result}, 
#            {'variable': '58c9991b76254236fc59c41e', 'value': TUR_level},
#            {'variable': '58c9990a76254236fee6b9a2', 'value': W_temp}
#          ])
                                                                      



# ajax GET call this function periodically to read button state
# the state is sent back as json data
#@app.route("/_button")

def GetUptime():
    # get uptime from the linux terminal command
    from subprocess import check_output
    output = check_output(["uptime"])
    # return only uptime info
    uptime = output[output.find("up"):output.find("user")-5]
    return uptime






















if __name__ == '__main__':
    t1 = Thread(target = Twhile)
    #t2 = Thread(target = start_server)
    t1.setDaemon(True)
    #t2.setDaemon(True)
    t1.start() 
    app.run(debug = True, host='0.0.0.0', port=80)
