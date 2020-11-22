from flask import Flask, render_template, request, Response, redirect,url_for
from neo4j import GraphDatabase
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io,os
from flask_uploads import UploadSet, configure_uploads, DOCUMENTS, IMAGES
import re
import pycountry as pc
from geotext import GeoText

uri = "bolt://localhost:5467"




location = ""
states =["Andhra Pradesh","Arunachal Pradesh ","Assam","Bihar","Chhattisgarh","Goa","Gujarat","Haryana","Himachal Pradesh","Jammu and Kashmir","Jharkhand","Karnataka","Kerala","Madhya Pradesh","Maharashtra","Manipur","Meghalaya","Mizoram","Nagaland","Odisha","Punjab","Rajasthan","Sikkim","Tamil Nadu","Telangana","Tripura","Uttar Pradesh","Uttarakhand","West Bengal","Andaman and Nicobar Islands","Chandigarh","Dadra and Nagar Haveli","Daman and Diu","Lakshadweep","National Capital Territory of Delhi","Puducherry"]

details ={0 : "id", 1:"age",2:"city",3:"diagnosed_date",4:"district",5:"status"}

def load_csv():
    df = pd.read_csv(r"./IndividualDetails.csv")
    return df


def modifyFile(filepath):
    df = pd.read_csv(filepath)
    l=[]
    for i in df['notes']:
        try:
            place = GeoText(i)
            flag = 0
            for j in place.cities:
                if j is not None:
                    l.append(j)
                    flag = 1
                    break
        
            if flag == 0:
                for j in place.countries:          
                    if j is not None:
                        l.append(j)
                        flag = 1
                        break
                    
                
            if flag == 0:
                #for j in i:
                try:
                    x = re.search(r"[pP][0-9]+",i)
                    if x.group() is not None:
                        y = re.search(r"[0-9]+",x.group())
                        l.append(y.group())
                        flag = 1
                except:
                    x = None
                
            if flag == 0:
                if i == "Details awaited":
                    l.append("Details awaited")
                else:
                    l.append("None")
        except:
            l.append("None")
    df['Relationship'] = l
    #df.to_csv(r"C:\Users\hp\.Neo4jDesktop\neo4jDatabases\database-f3fd89e4-0a4b-4473-941b-e8aee30cd975\installation-3.5.14\import\IndividualDetails1.csv")
    df.to_csv(r"./IndividualDetails.csv")

def getPersonsforState(name):
    df = load_csv()
    count = 0
    for i in df["detected_state"]:
        if i == name:
            count += 1
    return count
            
    
#==============================================================================
#     for record in tx.run("MATCH (l:Location)-[]->(p) "
#                          "WHERE l.id = {name} "
#                          "RETURN p.id", name=name):
#         l.append(record)
#==============================================================================


#==============================================================================
# def getPersonsforSource(tx,name):
#     l = []
#     for record in tx.run("MATCH (p:Person)-[]->(s) "
#                          "WHERE s.id = {name} "
#                          "RETURN p", name=name):
#         l.append(record)
#     return l
# def updateDB(tx):
#     tx.run("load csv with headers from 'file:///IndividualDetails1.csv' as row with toInteger(row.id) as id, row.Relationship as history, row.diagnosed_date as date, row.detected_district as district,row.detected_state as state, toInteger(row.age) as age, row.current_status as status, row.detected_city as city merge (p:Person {id:id}) on create set p.age = age, p.city = city, p.diagnosed_date = date, p.district = district, p.status = status merge(s:Source {id : history}) merge(l:Location {id:state}) merge(l)-[r1:CONTAINS] -> (p) merge(p)-[r2:SOURCE]->(s)")
#     
# def getSource(tx):
#     l=[]
#     for record in tx.run("match(s:Source) return s.id"):
#         l.append(record["s.id"])
#     return l
#     
# def getSourceRecords():
#     d={}
#     source = session.read_transaction(getSource)
#     for i in source:
#         d[i] = session.read_transaction(getPersonsforSource, i)
#     return d
#==============================================================================
    
def getStateData():
    d={}
    for i in states:
        
        d[i] = getPersonsforState(i)
#==============================================================================
#     for i,j in d.items():
#         for k in range(len(j)):
#             j[k] = j[k]["p.id"]
#==============================================================================
    return d
    
def find_hotspot():
    d = {}
    d = getStateData()
    print(d)
#==============================================================================
#     hotspot = {}
#     for i in d.keys():
#         hotspot[i] = len(d[i])
#     print(hotspot)        
#==============================================================================
    sort = {}
    for w in sorted(d, key=d.get, reverse=True):
        if d[w]>0:
            sort[w] =d[w]
    return sort

def barPlotHotspots():
    d = find_hotspot()
    
    objects = ()
    for i in d.keys():
        objects += (i,)
    print(objects)
    ypos = np.arange(len(objects))
    values=[]
    for i in d.values():
        values.append(i)
    fig = plt.figure(figsize=(20, 15))
    plt.barh(ypos,values,align='center',alpha=0.5)
    plt.yticks(ypos,objects)
    plt.xlabel("Number of confirmed cases")
    plt.title("Hotspots in India")
    plt.show()
    return fig


#==============================================================================
# def getSourceData():
#     d={}
#     source = session.read_transaction(getSource)
#     for i in source:
#         d[i] = session.read_transaction(getPersonsforSource, i)
#     for i,j in d.items():
#         for k in range(len(j)):
#             j[k] = j[k]["p.id"]
#     return d
#     
# def sourceStats():
#     d = getSourceData()
#     hotspot = {}
#     for i in d.keys():
#         hotspot[i] = len(d[i])
#             
#     sort = {}
#     for w in sorted(hotspot, key=hotspot.get, reverse=True):
#         if hotspot[w]>0:
#             sort[w] =hotspot[w]
#     return sort
#     
# def getPersonDetails(n):
#     result = session.run("MATCH (p:Person) RETURN p.id, p.age, p.city, p.diagnosed_date, p.district, p.status")
#     for record in result:
#         if record["p.id"] == n:
#             return record
#     return -1
#==============================================================================
            
   
#==============================================================================
# def plotSourceStats(name):
#     d = getSourceRecords()
#     l = d[name]
#     region = {}
#     for record in l:
#         unique = record
#         c = unique[0]["city"]
#         if c!= None:
#             if c not in region.keys():
#                 region[c] = 1
#             else:
#                 region[c] += 1
#     print(region)       
#     objects = ()
#     for i in region.keys():
#         objects += (i,)
#     
#     values=[]
#     for i in region.values():
#         values.append(int(i))
#     
#     
#     fig = plt.figure(figsize=(20, 15))
#     ax = fig.add_subplot(1,1,1)
#     ax.bar(objects,values, width = 0.25)
#     try:
#         plt.title("Distribution of patients who were in contact with {}".format(int(name)))
#     except:
#         plt.title("Distribution of patients with travel history to {}".format(name))
#     plt.xticks(rotation=90)
#     plt.xlabel("City Names")
#     plt.ylabel("Number of Cases")
#     plt.show()
#     return fig
#==============================================================================
    
#==============================================================================
# after this goes the logic for front-end
#==============================================================================
    
app = Flask(__name__)
#docs = UploadSet('datafiles', DOCUMENTS)
#app.config['UPLOADED_DATAFILES_DEST'] = 'static/uploads'
#configure_uploads(app, docs)
UPLOAD_FOLDER = "static/uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():  
    return render_template('options.html')
@app.route('/homepage')
def homepage():  
    return render_template('homepage.html')


@app.route("/display_user_options")
def display_user_options():
    return render_template("user_option.html")

@app.route("/handle_user")
def handle_user():
    return render_template("options.html")



@app.route("/handle_admin")
def handle_admin():
    return render_template("login.html")

    
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('upload_file'))
    return render_template('login.html', error=error)

@app.route('/upload_file')
def upload_file():
    return render_template('input_file.html')

@app.route('/update_data', methods=['POST'])
def update_data():
    file = request.files['myfile']
    print(file)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    print(file.filename)
    modifyFile(os.path.join("static/uploads/",file.filename))
    
    return "The database has been successfully Updated!!"    
    
#==============================================================================
# @app.route('/get_started',methods=['GET','POST'])
# def get_started():
#     global stack
#     source1 = session.read_transaction(getSource)
#        
#     return render_template('source.html',options=source1)
#==============================================================================
#==============================================================================
#     
# @app.route('/plot1',methods=['GET','POST'])
# def plot1():
#     if request.method == 'POST':
#         selected = request.form['source']
#         fig = plotSourceStats(selected)
#         output = io.BytesIO()
#         FigureCanvas(fig).print_png(output)
#         return Response(output.getvalue(), mimetype='image/png')
#     return -1
#     #return render_template('plot1.html')
#==============================================================================
    
@app.route('/hotspot')
def hotspot():
    fig = barPlotHotspots()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')
    

if __name__ == '__main__':
    app.run(use_reloader=False)


    
    

    