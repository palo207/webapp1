

# -*- coding: utf-8 -*-
"""
Created on Tue Jun 30 13:22:16 2020

@author: PAVA
"""

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
import pandas as pd

# credentials
server="LAPTOP-IR2NIHTL"
database="rtls"
driver="ODBC Driver 17 for SQL Server"

#connect db
database_conn = 'mssql://@{}/{}?driver={}'.format(server,database,driver)
engine = create_engine(database_conn)
conn = engine.connect()


#creating app object
app = Flask(__name__)
   
@app.route('/')
def Index() :
    select = pd.read_sql_query('SELECT row_no,tag_id,object_id FROM [dbo].[rtls_control]',conn)
    select = list(select.values)
    n_rows = len(select)
    return render_template('index.html', paired_tags= select,n_rows=n_rows)


@app.route('/insert',methods=['POST'])
def insert ():
    if request.method == 'POST':
        tag_id = request.form['tag_id']
        object_id = request.form['object_id']
        
        
        if (len(tag_id) and len(object_id)  >1) : 
            insert = pd.read_sql_query('INSERT INTO [dbo].[rtls_control] ( tag_id,object_id ) Values ({},{}) '.format(tag_id,object_id),conn)  
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