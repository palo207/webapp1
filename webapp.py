# -*- coding: utf-8 -*-
"""
Created on Tue Jun 30 13:22:16 2020

@author: PAVA
"""
import cv2
import os

from flask import (
    Flask, 
    render_template, 
    request, 
    redirect, 
    url_for, 
    flash,
    make_response,
    session
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
    
class rtls_tags(db.Model):
    row_no = db.Column(db.Integer,primary_key=True)
    tag_id=db.Column(db.String(50))
    address=db.Column(db.String(50))
    PosX=db.Column(db.Float())
    PosY=db.Column(db.Float())
    zone_id=db.Column(db.String(50))
    zone_type=db.Column(db.String(50))
    zone_name=db.Column(db.String(50))
    zone_enter=db.Column(db.DateTime())
    paired=db.Column(db.Integer)
    paired_id=db.Column(db.String(50))
    
    def __init__(self,tag_id,object_id,edited_by):
        self.row_no=row_no
        self.tag_id=tag_id
        self.address=address
        self.PosX=PosX
        self.PosY=PosY
        self.zone_id=zone_id
        self.zone_type=zone_type
        self.zone_name=zone_name
        self.zone_enter=zone_enter
        self.paired=paired
        self.paired_id=paired_id

class logs(db.Model):
    row_no = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(50))
    type_of_change = db.Column(db.String(50))
    tag_id=db.Column(db.String(50))
    object_id=db.Column(db.String(50))

    def __init__(self,username,type_of_change,tag_id,object_id):
        self.username=username
        self.type_of_change=type_of_change
        self.tag_id=tag_id
        self.object_id=object_id
        
class tag_location(db.Model):
    row_no = db.Column(db.Integer,primary_key=True)
    tag_id=db.Column(db.String(50))
    x=db.Column(db.Integer)
    y=db.Column(db.Integer)

    def __init__(self,username,type_of_change,tag_id,object_id):
        self.tag_id=tag_id
        self.object_id=object_id
    
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
    try:
        i=request.args['i']
        
    except: 
        i = 0
    try:    
        code1=request.args['code1']
        code2=request.args['code2']
    except:   
        code1 = 0
        code2 = 0
        
    if current_user.username=="user":
        dsb="disabled"
    else:
        dsb=""
        
    if 'my_data' in session:
        print('tu som')
        mydata = session.get('my_data')
        print(mydata)
    else: 
        mydata=0
        
    return render_template('index.html', 
                           user= current_user.username,
                           dsb=dsb,i=int(i),
                           code1=code1,
                           code2=code2,
                           mydata=mydata)
    
      
# Pair tag form
@app.route('/insert',methods=['POST'])
def insert():
    if request.method == 'POST':
        tag_id = request.form['tag_id']
        object_id = request.form['object_id']
        tags =[]
        # One of barcodes has to start with RTLS identifier
        condition1 = tag_id.startswith(rtls_tag_identifier)
        condition2 = object_id.startswith(rtls_tag_identifier)
        if condition1:
            tags=[tag_id,object_id]
        elif condition2 :
            tags=[object_id,tag_id]
       
        # If fields are blank or conditions are not met
        if not (tag_id 
            and object_id 
            and (condition1 + condition2 == 1)
            ): 
            flash("Nesprávne zadané vstupné dáta", "error")
            return redirect(url_for('Index'))
        
        # Condition 3 tag exists in database and is not paired
        condition3 = db.session.query(rtls_tags.paired).filter_by(tag_id=tags[0]).first()
        # Condition 4 object is not paired with tag
        condition4 = db.session.query(rtls_tags.paired_id).filter_by(paired_id=tags[1]).first()
        
        # If return is not none the tag does not exist in db
        if condition3 is None:
            flash("Tag sa v databáze nenachádza" , "error")
            return redirect(url_for('Index'))
        # If tag is paired
        if condition3[0]:
            flash("Tag je už spárovaný" , "error")
            return redirect(url_for('Index',i=1,code1=tags[0],code2=tags[1]))
        # If material is paired
        if condition4 is not None:
            flash("Výrobný príkaz už je spárovaný" , "error")
            return redirect(url_for('Index',i=1,code2=tags[1],code1=tags[0]))
                        
        # Getting the object from database
        tag=db.session.query(rtls_tags).filter_by(tag_id=tag_id).first()
        # Pair tags
        tag.paired=1
        tag.paired_id=tags[1]
        log = logs(current_user.username,"pair",tags[0],tags[1])
        # Write ids and username into database
        db.session.commit()
        db.session.add(log)
        db.session.commit()  
  
        flash("Tag úspešne spárovaný")
        return redirect(url_for('Index'))
                 

# Unpair tag button next to pair tag button
@app.route('/unpair',methods=['POST'])    
def unpair():
    tag_id = request.form['tag_id']
    # Delete tag and material pair
    my_data= db.session.query(rtls_tags).filter_by(tag_id=tag_id).first()   
    if my_data is not None:   
        my_data.paired=0
        my_data.paired_id=""
        db.session.commit()
        log = logs(current_user.username,"unpair",tag_id,"")
        db.session.add(log)
        db.session.commit()  
        flash("Tag {} bol úspešne odpárovaný".format(tag_id))
        return redirect(url_for('Index'))
    else:
        flash("Tag {} nie je spárovaný".format(tag_id),"error")
        return redirect(url_for('Index'))

# Change pair
@app.route('/change_pair',methods=['POST'])
def change_pair():
    if request.method =='POST':
        codes = request.form['yes']
        if codes == "nie":
            return redirect(url_for('Index'))
        else:
            codes = (codes.split("$,$"))
            my_data= db.session.query(rtls_tags).filter_by(tag_id=codes[0]).first()     
            my_data.paired_id=codes[1]
            db.session.commit()
            return redirect(url_for('Index'))
    

# =============================================================================
# # # Unpair button
# # @app.route('/delete/<tag_id>/', methods = ['GET','POST'])
# # def delete(tag_id):
# #     my_data= db.session.query(rtls_control).filter_by(tag_id=tag_id).first()
# #     if my_data is not None:
# #         db.session.delete(my_data)
# #         print(my_data)
# #         db.session.commit()
# #         log = logs(current_user.username,"unpair",tag_id,"")
# #         db.session.add(log)
# #         db.session.commit()  
# #         flash("Tag {} unpaired sucesfully".format(tag_id))
# #         return redirect(url_for('Index'))
# #     else:
# #         flash("Tag {} is not paired".format(tag_id),"error")
# #         return redirect(url_for('Index'))
# =============================================================================


# Locate tag page        
@app.route ('/locate', methods = ['GET','POST'])
def locate():
    my_data_parsed=[]
    tag_id = request.form['tag_id']
    my_data= db.session.query(rtls_tags).filter_by(tag_id=tag_id).first() 
    if my_data is None:
        my_data= db.session.query(rtls_tags).filter_by(paired_id=tag_id).first()
    if my_data is None:
        flash("Tag {} sa v databáze nenacháadza".format(tag_id),"error")
        return redirect(url_for('Index'))
    else:
        if 'my_data' in session:
            session.pop('my_data', None)
            my_data_parsed.append( [my_data.tag_id,
                    my_data.zone_id,
                    my_data.zone_type,
                    my_data.zone_name,
                    my_data.zone_enter,
                    my_data.paired_id])
         
        session['my_data']=my_data_parsed
        print(session['my_data'],my_data_parsed)
        return redirect(url_for('Index',i=2))
                         
# Finishing the locate process
@app.route('/located', methods =['GET','POST'])
def located():
    return redirect(url_for('Index',))
    print('tu_som')
    
# =============================================================================
# # Tag location based on dropdown
# @app.route('/locate_tag/<tag_id>/', methods = ['GET','POST'])
# def locate_tag(tag_id):
#     
#     my_data = db.session.query(tag_location).filter_by(tag_id=tag_id).first()
#     if my_data is not None:
#         x = my_data.x
#         y = my_data.y
#         color=(0,0,255)
#         thickness=-1
#         radius = 20   
#         directory_path = os.path.dirname(__file__)
#         file_path = os.path.join(directory_path, "static/layout.jpg")
#         new_filepath = os.path.join(directory_path, "static/layout1.jpg")
#         img=cv2.imread(file_path)
#         img1=cv2.circle(img,(x,y),radius,color,thickness)
#         cv2.imwrite(new_filepath, img1)
#         all_data = rtls_control.query.all()
#         print("vybavene")
#         response= make_response(render_template('locate.html', 
#                                                 paired_tags=all_data, 
#                                                 img_path="layout1.jpg"))
#         response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, public, max-age=0'
#         response.headers["Expires"] = 0
#         response.headers['Pragma'] = 'no-cache'
#         return response  
#     else:
#        return redirect(url_for('locate'))
# =============================================================================
    
                    

# Run function if main  
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)


