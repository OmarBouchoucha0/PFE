from flask import Flask, render_template, url_for, request, redirect,session
from flask_sqlalchemy import SQLAlchemy
from datetime import  datetime,timedelta






NOW_in_hours = datetime.now().strftime('%H:%M:%S')
NOW_in_days = datetime.now().strftime('%d-%m-%y')
Number_OF_INTERVALES=[]

# Create flask app 
app = Flask(__name__) 
app.secret_key = "KHHJH546DFSHSSDFHmljmkfj5619"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Database/database.db'
app.config ['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app) 

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=False, nullable=False)
    password = db.Column(db.String(20), unique=False, nullable=False)
    position = db.Column(db.String(20), unique=False, nullable=False)
    url = db.Column(db.String(100),unique=False, nullable=False)
    messages = db.relationship("message_db",backref = "user")
    reports = db.relationship("reports_db",backref = "user")
    
 

class Input(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temp = db.Column(db.Integer, unique=False, nullable=False)
    duration = db.Column(db.Integer, unique=False, nullable=False)
    date = db.Column(db.String(20), unique=False, nullable=False)
    time = db.Column(db.String(20), unique=False, nullable=False)


class capt_Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temp = db.Column(db.Integer, unique=False, nullable=False)
    humidity = db.Column(db.Integer, unique=False, nullable=False)
    weight = db.Column(db.Integer, unique=False, nullable=False)
    date = db.Column(db.String(20), unique=False, nullable=False)
    time = db.Column(db.String(20), unique=False, nullable=False)


class message_db(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(30),unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id') )

class reports_db(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    report = db.Column(db.String(100))
    date = db.Column(db.String(20), unique=False, nullable=False)
    time = db.Column(db.String(20), unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id') )

class fruit_db(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=False, nullable=False)
    temperature = db.relationship("temperature_db",backref = "fruit")
    duration = db.relationship("duration_db",backref = "fruit")

class temperature_db(db.Model):
    id  = db.Column(db.Integer, primary_key=True)
    values = db.Column(db.Integer,unique=False, nullable=False)
    fruit_id = db.Column(db.Integer, db.ForeignKey('fruit_db.id'))

class duration_db(db.Model):
    id  = db.Column(db.Integer, primary_key=True)
    values = db.Column(db.Integer, unique=False, nullable=False)
    fruit_id = db.Column(db.Integer, db.ForeignKey('fruit_db.id'))

db.create_all()  

@app.route("/")        
@app.route("/login",methods=["GET",'POST'])
def login():
    msg=""
    if request.method =="POST":
        name = request.form["name"]
        password = request.form["pass"]
        session["name"] = name
        session["password"] = password
        if User:
            found_user = User.query.filter_by(name=name,password=password).first()
            if found_user:           
                pos = found_user.position
                session["pos"] = pos
                return redirect(url_for("index"))
            else:
                msg = "Account not Found"
                return render_template("login.html",msg=msg)
        else:
            redirect(url_for("signup"))
    else:
        session.pop("name", None)
        return render_template("login.html",msg=msg)

@app.route("/signup", methods=["POST", "GET"])
def singup():   
    msg=""
    if request.method =="POST":
        name = request.form["name"]
        password = request.form["pass"]
        pos = request.form["pos"]
        confpass = request.form["confpass"]
        users = User.query.all()
        if confpass != password:
            msg="Password doesnt match"
            return render_template("signup.html",msg=msg)
        if len(users)>0:
            if User.query.filter_by(name=name, password=password).first():
                msg="User already exists"
                return render_template("signup.html",msg=msg)
        user = User(name=name, password=password, position=pos,url = url_for('static', filename='images/Profile-pic.png'))
        db.session.add(user)
        db.session.commit()
        session["name"] = name
        session["password"] = password
        session["pos"]= pos
        return redirect(url_for("index"))
    else:
        return render_template("signup.html")

@app.route("/index",methods=["GET", "POST"])
def index():
    if 'name' in session:
        name = session["name"]
        password = session["password"]
        pos = session["pos"]
        reports = reports_db.query.all()
        reports_rev = reports[::-1]
        user = User.query.filter_by(name=name,password=password).first()
        messages = message_db.query.all()
        messages_rev = messages[::-1]
        data = capt_Data.query.all()
        if len(data) > 0: 
            last_data = data[-1]
        else:
            last_data = capt_Data(temp = 0, humidity = 0, weight = 0, date = NOW_in_hours,time = NOW_in_hours)
            db.session.add(last_data)
            db.session.commit()
        return render_template("index.html",name = name,pos = pos,reports = reports_rev ,messages = messages_rev,user=user,data = last_data)

    return redirect(url_for("singup"))
      
    
@app.route("/command",methods=["GET", "POST"])
def command():
    name = session["name"]
    password = session["password"]
    found_user = User.query.filter_by(name=name,password=password).first()
    pos = found_user.position
    if request.method =="POST":
        fruit = request.form["fruit"]
        session["fruit"] =fruit
        fruits = fruit_db.query.all()
        for i in range(len(fruits)):
            if fruits[i].name == fruit:            
                return redirect(url_for("drying"))
        new_fruit = fruit_db(name=fruit)
        db.session.add(new_fruit)
        db.session.commit()
        return redirect(url_for("drying"))
    messages = message_db.query.all()
    messages_rev = messages[::-1]
    

        
    return render_template("command.html",name = name,pos = pos,user = found_user ,messages = messages_rev)

@app.route("/analytics")
def analytics():
    name = session["name"]
    password = session["password"]
    found_user = User.query.filter_by(name=name,password=password).first()
    pos = found_user.position
    messages = message_db.query.all()
    messages_rev = messages[::-1]
    
    return render_template("analytics.html",name = name,pos = pos, user = found_user ,messages = messages_rev)

@app.route("/reports")
def reports():
    name = session["name"]
    password = session["password"]
    found_user = User.query.filter_by(name=name,password=password).first()
    pos = found_user.position
    reports = reports_db.query.all()
    reports_rev = reports[::-1]
    messages = message_db.query.all()
    messages_rev = messages[::-1]

    return render_template("reports.html",reports=reports_rev,name = name,pos = pos,user = found_user ,messages = messages_rev)

@app.route("/settings",methods=["GET", "POST"])
def settings():
    name = session["name"]
    password = session["password"]
    found_user = User.query.filter_by(name=name,password=password).first()
    pos = found_user.position
    messages = message_db.query.all()
    messages_rev = messages[::-1]
    
    
    return render_template("settings.html",name = name,pos = pos, user  = found_user ,messages = messages_rev)

@app.route("/logout")
def logout():
    session.clear()
    return  redirect(url_for("login"))

@app.route("/accdelete", methods=["GET", "POST"])
def deleteacc():
    if request.method =="POST":
        name = session["name"]
        password = session["password"] 
        User.query.filter_by(name=name,password=password).delete()
        db.session.commit()
        return redirect(url_for("logout"))
    return render_template("accdelete.html")

@app.route("/accountconfig", methods=["GET", "POST"])
def accountconfig():
    name1 = session["name"]
    password1 = session["password"] 
    found_user = User.query.filter_by(name=name1,password=password1).first()
    msg=""
    if request.method =="POST":
        name = request.form["name"]
        password = request.form["pass"]
        pos = request.form["pos"]
        if User.query.filter_by(name=name, password=password, position=pos).first():
            msg="User already exists"
            return render_template("accountconfig.html",msg=msg)    
        found_user.name = name
        found_user.password = password
        found_user.position = pos
        db.session.commit()
        session["name"] = name
        session["password"] = password
        session["pos"]= pos
        return redirect(url_for("settings"))
            
    return render_template("accountconfig.html",msg=msg)

@app.route("/picchanger",methods=["GET", "POST"])
def picchanger():
    if request.method =="POST":
        name = session["name"]
        password = session["password"] 
        found_user = User.query.filter_by(name=name,password=password).first()
        if found_user:
            pfp = request.form["pfp"]
            if pfp == "":
                return redirect(url_for("picchanger"))
            else:
                img_url = url_for('static', filename='images/'+pfp)
                found_user.url = img_url
                db.session.commit()
                return redirect(url_for("settings"))
    return render_template("picchanger.html")


@app.route("/messagesender",methods=["GET", "POST"])
def messagesender():
    if request.method =="POST":
        msg = request.form["message"]
        name = session["name"]
        found_user = User.query.filter_by(name=name).first()
        new_msg = message_db(message=msg, user=found_user)        
        db.session.add(new_msg)
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("messagesender.html")

@app.route("/numberofintervales",methods=["GET", "POST"])
def numberofintervales():
    if request.method =="POST":
        number = request.form["number"]
        Number_OF_INTERVALES.clear()
        for i in range(int(number)):
            Number_OF_INTERVALES.append(i+1)       
        return redirect(url_for("customintervales"))
    
    return render_template("numberofintervales.html")

@app.route("/customintervales",methods=["GET", "POST"])
def customintervales():
    if request.method =="POST":
        date = NOW_in_days
        time = NOW_in_hours
        Now=datetime.now()
        for i in Number_OF_INTERVALES:
            temp = request.form["tempature "+str(i)]
            duration = request.form["duration "+str(i)]
            duration_ = timedelta(minutes=int(duration))

            time_ = Now 
            t = str(time_)
            time = t[11:18]
            date = t[0:9]
            input = Input(temp=temp, duration=duration, date=date,time=time)
            db.session.add(input)
            db.session.commit()
            time_ = Now + duration_ 
        name = session["name"]
        found_user = User.query.filter_by(name=name).first()
        report = reports_db(report="Used custom values",date=date,time=time,user=found_user)
        db.session.add(report)
        db.session.commit()
        return redirect(url_for("command"))
    return render_template("customvalues.html",nbr = Number_OF_INTERVALES)

@app.route("/numberofintervalesforfruits",methods=["GET", "POST"])
def numberofintervalesforfruits():
    if request.method =="POST":
        number = request.form["number"]
        Number_OF_INTERVALES.clear()
        for i in range(int(number)):
            Number_OF_INTERVALES.append(i+1)       
        return redirect(url_for("customintervalesforfruits"))
    
    return render_template("numberofintervalesforfruites.html")

@app.route("/customintervalesforfruits",methods=["GET", "POST"])
def customintervalesforfruits():
    if request.method =="POST":
        date = NOW_in_days
        time = NOW_in_hours
        fruit = session["fruit"]
        fruit_instance = fruit_db.query.filter_by(name=fruit).first()
        tempatures = temperature_db.query.all()
        for i in range(len(tempatures)):
            if tempatures[i].fruit.name == fruit:
                id = fruit_instance.id
                temperature_db.query.filter_by(fruit_id=id).delete()
                duration_db.query.filter_by(fruit_id=id).delete()
                db.session.commit()
        for i in Number_OF_INTERVALES:
            tempature = request.form["tempature "+str(i)]
            duration = request.form["duration "+str(i)]
            
            t = temperature_db(values=int(tempature),fruit=fruit_instance)
            d = duration_db(values=int(duration),fruit=fruit_instance)
            db.session.add(t)
            db.session.add(d)
            db.session.commit()
        name = session["name"]
        found_user = User.query.filter_by(name=name).first()
        report = reports_db(report=f"Changed The {fruit} values",date=date,time=time,user=found_user)
        db.session.add(report)
        db.session.commit()
        return redirect(url_for("command"))
    return render_template("customvaluesforfruits.html",nbr = Number_OF_INTERVALES)

@app.route("/drying",methods=["GET", "POST"])
def drying():
    if request.method =="POST":
        tempatures = temperature_db.query.all()
        durations = duration_db.query.all()
        name = session["name"]
        fruit = session["fruit"]
        found_user = User.query.filter_by(name=name).first()  
        Now=datetime.now()
        found = False
        for i in range(len(tempatures)):
            if tempatures[i].fruit.name == fruit:
                temp = tempatures[i].values
                duration = durations[i].values
                duration_ = timedelta(minutes=duration)
                time_ = Now 
                t = str(time_)
                time = t[11:18]
                date = t[0:9]
                input = Input(temp=temp, duration=duration, date=date,time = time)
                db.session.add(input)
                time_ = Now + duration_ 
                found= True
        if not found:
            msg="Values Not Found"
            return render_template("drying.html",msg=msg)
        report = reports_db(report=f"Started drying a {fruit} ",date=date,time=time,user=found_user)
        db.session.add(report)  
        db.session.commit()
        return redirect(url_for("command"))
        
    return render_template("drying.html")
    

@app.route("/off",methods=["GET", "POST"])
def off():
    if request.method =="POST":
        name = session["name"]
        found_user = User.query.filter_by(name=name).first()
        report = reports_db(report="Truned OFF the Machine",date=NOW_in_days,time=NOW_in_hours,user=found_user)
        db.session.add(report)
        db.session.commit()
        inp = Input.query.all()
        for i in range(len(inp)):
            time = inp[-i].time
            date = inp[-i].date
            in_time = datetime.strptime(time, '%H:%M')
            in_date = datetime.strptime(date,'%d/%m/%y')
            if NOW_in_days >= in_date:
                if NOW_in_hours > in_time:
                    return redirect(url_for("command"))
            else:
                inp[-i].time = "canceled"
                inp[-i].date = "canceled"
        return redirect(url_for("command"))
    return render_template("off.html")

@app.route("/fruitgraph")
def fruitgraph():
    return render_template("fruitgraph.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)