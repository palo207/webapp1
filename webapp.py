# -*- coding: utf-8 -*-
"""
Created on Tue Jun 30 13:22:16 2020

@author: PAVA
"""

from flask import (
    Flask, 
    render_template, 
    request, 
    redirect, 
    url_for, 
    flash
)
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user
)
from flask_sqlalchemy import SQLAlchemy

# Database info
server="LAPTOP-IR2NIHTL"
database="rtls"
driver="ODBC Driver 17 for SQL Server"

# Global vars
rtls_tag_identifier = "rtls_"

# Init of flask object
app = Flask(__name__)
app.secret_key = "Secret_key"

# MySql
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:''@localhost/rtls'

# MS Sql
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql://@{}/{}?driver={}'.format(server,database,driver)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


class users(UserMixin, db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(50),unique=True)
    password = db.Column(db.String(50))


class rtls_control(db.Model):
    row_no = db.Column(db.Integer,primary_key=True)
    tag_id=db.Column(db.String(50))
    object_id=db.Column(db.String(50))
    edited_by=db.Column(db.String(50))
    
    def __init__(self,tag_id,object_id,edited_by):
        self.tag_id=tag_id
        self.object_id=object_id
        self.edited_by=edited_by
        
    
@login_manager.user_loader
def load_user(user_id):
    return users.query.get(int(user_id))

# Login page        
@app.route('/',methods=['GET','POST'])   
def login():
    if request.method =='POST':
        username = request.form['username']
        password = request.form['password']
        user = users.query.filter_by(username=username,password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('Index'))
    return render_template('login.html')

# Logout button      
@app.route('/logout')  
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# RTLS Control page      
@app.route('/rtls_control')
@login_required
def Index():
    # Get all paired tags and render page with them
    all_data = rtls_control.query.all()
    return render_template('index.html', paired_tags= all_data)

# Pair tag form
@app.route('/insert',methods=['POST'])
def insert():
    if request.method == 'POST':
        tag_id = request.form['tag_id']
        object_id = request.form['object_id']
        # One of barcodes has to start with RTLS identifier
        condition1 = tag_id.startswith(rtls_tag_identifier)
        condition2 = object_id.startswith(rtls_tag_identifier)
        
        # If fields are not blank and conditions are met
        if (tag_id 
            and object_id 
            and (condition1 + condition2 == 1)
            ):
            
            # If tag id(barcode 1) is id of rtls tag
            if condition1:
                my_data = rtls_control(tag_id,object_id,user.username)
            # If object_id(barcode 2) is id of rtls tag
            else:
                my_data = rtls_control(object_id,tag_id,user.username)
            # Write ids and username into database
            db.session.add(my_data)
            db.session.commit()   
            flash("Tag paired sucesfully")
            return redirect(url_for('Index'))
        else:
            flash("Wrong input data", "error")
            return redirect(url_for('Index'))

# Unpair tag button next to pair tag button
@app.route('/unpair',methods=['POST'])    
def unpair():
    tag_id = request.form['tag_id']
    # Delete tag and material pair
    my_data= db.session.query(rtls_control).filter_by(tag_id=tag_id).first()   
    if my_data is not None:   
        db.session.delete(my_data)
        print(my_data)
        db.session.commit()
        flash("Tag {} unpaired sucesfully".format(tag_id))
        return redirect(url_for('Index'))
    else:
        flash("Tag {} is not paired".format(tag_id),"error")
        return redirect(url_for('Index'))

# Unpair button
@app.route('/delete/<tag_id>/', methods = ['GET','POST'])
def delete(tag_id):
    my_data= db.session.query(rtls_control).filter_by(tag_id=tag_id).first()
    if my_data is not None:
        db.session.delete(my_data)
        print(my_data)
        db.session.commit()
        flash("Tag {} unpaired sucesfully".format(tag_id))
        return redirect(url_for('Index'))
    else:
        flash("Tag {} is not paired".format(tag_id),"error")
        return redirect(url_for('Index'))
        
# Run function if main  
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)