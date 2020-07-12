# -*- coding: utf-8 -*-
"""
Created on Tue Jun 30 13:22:16 2020

@author: PAVA
"""

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required,logout_user, current_user

#database info
server="LAPTOP-IR2NIHTL"
database="rtls"
driver="ODBC Driver 17 for SQL Server"

app = Flask(__name__)
app.secret_key = "Secret_key"

#MySql
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:''@localhost/rtls'

#MS Sql
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql://@{}/{}?driver={}'.format(server,database,driver)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

class users(UserMixin, db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(50),unique=True)
    
@login_manager.user_loader
def load_user(user_id):
    return user.query.get(int(user_id))
     
class rtls_control(db.Model):
    row_no = db.Column(db.Integer,primary_key=True)
    tag_id=db.Column(db.String(50))
    object_id=db.Column(db.String(50))
    edited_by=db.Column(db.String(50))
    
    def __init__(self,tag_id,object_id):
        self.tag_id=tag_id
        self.object_id=object_id


@app.route('/login',methods=['GET','POST'])   
def login():
    
    if request.method =='POST':
        username = request.form['username']
        password = request.form['password']
        login_user(username)
        return redirect(url_for('Index'))
    
    return render_template('login.html')
        
@app.route('/logout')  
@login_required
def logout():
    logout_user()
    
   
@app.route('/')
def Index() :
    all_data = rtls_control.query.all()
    return render_template('index.html', paired_tags= all_data)


@app.route('/insert',methods=['POST'])
def insert ():
    if request.method == 'POST':
        tag_id = request.form['tag_id']
        object_id = request.form['object_id']
        
        
        if len(tag_id) and len(object_id)  >1: 
            my_data = rtls_control(tag_id,object_id)
            db.session.add(my_data)
            db.session.commit()   
            flash("Tag paired sucesfully")
            return redirect(url_for('Index'))
            
        else:
            return redirect(url_for('Index'))
        

@app.route('/delete/<tag_id>/', methods = ['GET','POST'])
def delete(tag_id):
    my_data= db.session.query(rtls_control).filter_by(tag_id=tag_id).first()
    db.session.delete(my_data)
    print(my_data)
    db.session.commit()
    flash("Tag {} unpaired".format(tag_id))
    return redirect(url_for('Index'))

@app.route('/unpair',methods=['POST'])    
def unpair():
    tag_id = request.form['tag_id']
    my_data= db.session.query(rtls_control).filter_by(tag_id=tag_id).first()
    db.session.delete(my_data)
    print(my_data)
    db.session.commit()
    flash("Tag {} unpaired".format(tag_id))
    return redirect(url_for('Index'))
    

    
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)