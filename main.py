# ----------- import statements  ------------

from flask import Flask,flash, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime 
import win32api

# ------------ app initialisation -------------------

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']= "sqlite:///flashcard.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
db=SQLAlchemy(app)


#----------------- MODELS ---------------------------------

class Login(db.Model):
    _tablename_="login"
    login_id = db.Column(db.Integer, primary_key=True,unique=True)
    user_name =db.Column(db.String,unique=True)
    password=db.Column(db.String,unique=True) 
    name=db.Column(db.String)
    phone=db.Column(db.String)
    gender=db.Column(db.String)
    type=db.Column(db.String)  

    def __repr__(self) -> str:
        return f" {self.login_id }-{self.user_name}-{self.password}-{self.name}-{self.phone}-{self.gender}-{self.type}"        

class Section(db.Model):
    _tablename_="section"
    section_id = db.Column(db.Integer,primary_key=True,unique=True)
    section_name=db.Column(db.String,unique=True) 
    login_id = db.Column(db.Integer, db.ForeignKey(Login.login_id)) 

    def __repr__(self) -> str:
        return f" {self.section_id }-{self.section_name}-{self.login_id}"

class Decks(db.Model):
    _tablename_="decks"
    deck_id = db.Column(db.Integer,primary_key=True,unique=True)
    deck_name=db.Column(db.String) 
    score=db.Column(db.Integer) 
    section_id = db.Column(db.Integer, db.ForeignKey(Section.section_id)) 

    def __repr__(self) -> str:
        return f" {self.deck_id }-{self.deck_name}-{self.score}-{self.section_id}"        

class Flashcard(db.Model):
    _tablename_="flashcard"
    card_id = db.Column(db.Integer,primary_key=True,unique=True)
    question=db.Column(db.String) 
    answer=db.Column(db.String) 
    marks=db.Column(db.Integer)
    deck_id = db.Column(db.Integer, db.ForeignKey(Decks.deck_id)) 

    def __repr__(self) -> str:
        return f" {self.card_id }-{self.question}-{self.answer}-{self.marks}-{self.deck_id}"        

class Teacher(db.Model):
    _tablename_="teacher"
    teacher_id = db.Column(db.Integer, db.ForeignKey(Login.login_id),primary_key=True) 
    

    def __repr__(self) -> str:
        return f" {self.teacher_id }"        

class Student(db.Model):
    _tablename_="student"
    student_id = db.Column(db.Integer, db.ForeignKey(Login.login_id),primary_key=True) 
    
    def __repr__(self) -> str:
        return f" {self.student_id }"

class Student_Teacher(db.Model):
    _tablename_="student_teacher"
    st_id = db.Column(db.Integer,primary_key=True,unique=True)
    student_id = db.Column(db.Integer, db.ForeignKey(Student.student_id)) 
    teacher_id = db.Column(db.Integer, db.ForeignKey(Teacher.teacher_id)) 
        
    def __repr__(self) -> str:
        return f" {self.student_id }-{self.teacher_id}"


#-------------- Controllers ------------------------------

@app.route("/")
def index():
    return render_template('login.html')

#----------------------Account---------------------------    


@app.route('/render_login', methods=['GET', 'POST'])
def render_login(): 
     return render_template('login.html')

@app.route('/create', methods=['GET', 'POST'])
def create(): 
     name=request.form['name']
     user_name=request.form['username']
     password=request.form['password']
     phone=request.form['phone']
     gender=request.form['gender']
     type=request.form['type']
     f1=Login.query.all()
     for f in f1:
        if user_name==f.user_name:
            return render_template('register_error.html')
     l=Login(user_name=user_name, password=password,name=name,phone=phone,gender=gender, type=type)
     db.session.add(l)
     db.session.commit()

     if(type=="t"):
         f= Login.query.filter_by(user_name=user_name).first()
         LI=f.login_id
         l=Teacher(login_id=LI)
         db.session.add(l)
         db.session.commit()   
     page="render_login"
     msg="Registration Successfull" 
     return render_template('popup.html',msg=msg,page=page)

@app.route('/login', methods=['GET', 'POST'])
def login():
    user_name=request.form['username']
    password=request.form['password']
    
    f1=Login.query.all()
    for f in f1:
        if user_name==f.user_name and password==f.password:
            f_all=Section.query.filter_by(login_id=f.login_id).all()
            type=f.type
            LI=f.login_id
            if(type=="t"):
                st_all=Student_Teacher.query.all()
                return render_template('dashboard.html',LI=LI, f_all=f_all,type=type,st_all=st_all)
            return render_template('dashboard.html',LI=LI, f_all=f_all,type=type)
    return render_template('login_error.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')


@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    return render_template('forgot.html')    


#----------------------Dashboard---------------------------    

    
@app.route('/dashboard/<int:LI>', methods=['GET', 'POST'])
def dashboard(LI):
    f_all=Section.query.filter_by(login_id=LI).all()
    return render_template('dashboard.html',LI=LI, f_all=f_all)



#----------------------Section---------------------------    

    

@app.route('/section/<int:SI>/<int:LI>', methods=['GET', 'POST'])
def section(SI,LI):
    f_all=Decks.query.filter_by(section_id=SI).all()
    return render_template('section.html',SI=SI,LI=LI,f_all=f_all)

    
@app.route('/add_section/<int:LI>', methods=['GET', 'POST'])
def add_section(LI):
    section_name=request.form['name']
    f1=Section.query.all()
    for f in f1:
        if section_name==f.section_name and LI==f.login_id:
            page="dashboard"
            msg=section_name+" already exist"
            return render_template('popup.html',page=page,ID=LI,msg=msg)
    l=Section( section_name=section_name,login_id=LI)
    db.session.add(l)
    db.session.commit()
    f_all=Section.query.filter_by(login_id=LI).all()
    return render_template('dashboard.html',LI=LI, f_all=f_all)

@app.route('/delete_section/<int:LI>', methods=['GET', 'POST'])
def delete_section(LI):
    section_name=request.form['name']
    f1=Section.query.all()
    for f in f1:
        if section_name==f.section_name:
            SI=f.section_id
            #decks to delete
            f2=Decks.query.filter_by(section_id=SI).all()
            DIs=[f.deck_id for f in f2 ]
            #cards to delete
            f3=Flashcard.query.filter(Flashcard.deck_id.in_(DIs))
            CIs=[f.card_id for f in f3]
            #query to delete
            for i in CIs:
                flashd=Flashcard.query.get(i)
                db.session.delete(flashd)
                db.session.commit()
            for i in DIs:
                d=Decks.query.get(i)
                db.session.delete(d)
                db.session.commit()

            s=Section.query.get(SI)
            db.session.delete(s)
            db.session.commit()
            f_all=Section.query.filter_by(login_id=LI).all()
            return render_template('dashboard.html',LI=LI, f_all=f_all)
    page="dashboard"
    msg=section_name+" does not exist"
    return render_template('popup.html',page=page,ID=LI,msg=msg)
    


#----------------------Deck---------------------------    



@app.route('/deck/<int:DI>/<int:SI>/<int:LI>', methods=['GET', 'POST'])
def deck(DI,SI,LI):
    f_all=Flashcard.query.filter_by(deck_id=DI).all()
    return render_template('deck.html',DI=DI,SI=SI,LI=LI, f_all=f_all)

@app.route('/add_deck/<int:SI>/<int:LI>', methods=['GET', 'POST'])
def add_deck(SI,LI):
    deck_name=request.form['name']
    f1=Decks.query.all()
    for f in f1:
        if deck_name==f.deck_name and SI==f.section_id:
            page="section"
            msg=deck_name+" already exist"
            return render_template('popup.html',page=page,ID=SI,LI=LI,msg=msg)
    l=Decks( deck_name=deck_name,section_id=SI)
    db.session.add(l)
    db.session.commit()
    f_all=Decks.query.filter_by(section_id=SI).all()
    return render_template('section.html',SI=SI,LI=LI, f_all=f_all)  

@app.route('/delete_deck/<int:SI>/<int:LI>', methods=['GET', 'POST'])
def delete_deck(SI,LI):
    deck_name=request.form['name']
    f1=Decks.query.all()
    for f in f1:
        if deck_name==f.deck_name and SI==f.section_id:
            DI=f.deck_id
            #cards to delete
            f2=Flashcard.query.filter_by(deck_id=DI).all()
            CIs=[f.card_id for f in f2]
            #query to detete
            for i in CIs:
                flashd=Flashcard.query.get(i)
                db.session.delete(flashd)
                db.session.commit()
            d=Decks.query.get(DI)
            db.session.delete(d)
            db.session.commit()

            f_all=Decks.query.filter_by(section_id=SI).all()
            return render_template('section.html',SI=SI,LI=LI, f_all=f_all)
    page="section"
    msg=deck_name+" does not exist"
    return render_template('popup.html',page=page,ID=SI,LI=LI,msg=msg)    


@app.route('/edit_deck/<int:SI>/<int:LI>', methods=['GET', 'POST'])
def edit_deck(SI,LI):
    deck_name=request.form['name']
    f1=Decks.query.all()
    for f in f1:
        if deck_name==f.deck_name and SI==f.section_id:
            DI=f.deck_id
            f_all=Flashcard.query.filter_by(deck_id=DI).all()
            return render_template('deck.html',DI=DI,SI=SI,LI=LI, f_all=f_all)
    page="section"
    msg=deck_name+" does not exist"
    return render_template('popup.html',page=page,ID=SI,LI=LI,msg=msg)



#----------------------cards---------------------------    



@app.route('/card/<int:DI>/<int:i>/<int:SI>/<int:LI>', methods=['GET', 'POST'])
def card(DI,i,SI,LI):
    f_all=Flashcard.query.filter_by(deck_id=DI).all()
    
    if len(f_all)==0:
        return render_template('noflash.html',DI=DI,SI=SI,LI=LI)
    f1=f_all[i]
    if f1==f_all[-1]:
        marks=request.form['score']
        CI=f_all[i-1].card_id
        card = Flashcard.query.filter_by(card_id=CI).first()
        card.marks = marks
        db.session.commit()
        return render_template('lastflash.html',f1=f1,DI=DI,SI=SI,LI=LI)
    elif f1==f_all[0]:
        return render_template('flashcard.html',f1=f_all[i],i=i+1,DI=DI,LI=LI,SI=SI)
    marks=request.form['score']            
    CI=f_all[i-1].card_id
    card = Flashcard.query.filter_by(card_id=CI).first()
    card.marks = marks
    db.session.commit()
    return render_template('flashcard.html',f1=f_all[i],i=i+1,DI=DI,LI=LI,SI=SI)   

@app.route('/add_card/<int:DI>/<int:SI>/<int:LI>', methods=['GET', 'POST'])
def add_card(DI,SI,LI):
    question=request.form['que']
    answer=request.form['ans']
    f1=Flashcard.query.all()
    for f in f1:
        if question==f.question:
            page="deck"
            msg="Question already exist"
            return render_template('popup.html',page=page,ID=DI,SI=SI,LI=LI,msg=msg)
    l=Flashcard( question=question,answer=answer,deck_id=DI)
    db.session.add(l)
    db.session.commit()
    f_all=Flashcard.query.filter_by(deck_id=DI).all()
    return render_template('deck.html',DI=DI,SI=SI,LI=LI, f_all=f_all) 

@app.route('/delete_card/<int:DI>/<int:SI>/<int:LI>', methods=['GET', 'POST'])
def delete_card(DI,SI,LI):
    question=request.form['que']
    f1=Flashcard.query.all()
    for f in f1:
        if question==f.question:
            l=Flashcard.query.get(f.card_id)
            db.session.delete(l)
            db.session.commit()
            f_all=Flashcard.query.filter_by(deck_id=DI).all()
            return render_template('deck.html',DI=DI,SI=SI,LI=LI, f_all=f_all)
    page="deck"
    msg="Question does not exist"
    return render_template('popup.html',page=page,ID=DI,SI=SI,LI=LI,msg=msg)    

#---------------------------------score----------------------
@app.route('/score/<int:DI>/<int:SI>/<int:LI>', methods=['GET', 'POST'])
def score(DI,SI,LI):
    sc=0
    marks=request.form['score']
    f_all=Flashcard.query.filter_by(deck_id=DI).all()
    f_all[-1].marks=marks
    total=len(f_all)*5
    for f in f_all:
        sc+=int(f.marks)
    card = Decks.query.filter_by(deck_id=DI).first()
    card.score = sc
    db.session.commit()  
    page="section"
    msg= "your score is "+str(card.score)+"/"+str(total) 
    return render_template('popup.html',page=page,ID=SI,LI=LI,msg=msg)


@app.route('/score_all/<int:LI>', methods=['GET', 'POST'])
def score_all(LI):
    f_all_s=Section.query.filter_by(login_id=LI).all()
    for f in f_all_s:
        SIs=[f.section_id for f in f_all_s]
    f_all_d=Decks.query.filter(Decks.section_id.in_(SIs))
    return render_template('score.html', f_all_s=f_all_s,f_all_d=f_all_d,LI=LI)

@app.route('/profile/<int:LI>', methods=['GET', 'POST'])
def profile(LI):
    f= Login.query.filter_by(login_id=LI).first()
    return render_template('profile.html',name=f.name,phone=f.phone,gender=f.gender,username=f.user_name,type=f.type,LI=LI)    

 #---------------- final application run ------------------

if __name__=="__main__":
    #app.run(debug=True)
    app.run(host='0.0.0.0',port=8080)    







