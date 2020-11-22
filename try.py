from flask import Flask, render_template, request, Response
from neo4j import GraphDatabase
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io

uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri,auth=("neo4j","saswath"))

location = ""
states =["Andhra Pradesh","Arunachal Pradesh ","Assam","Bihar","Chhattisgarh","Goa","Gujarat","Haryana","Himachal Pradesh","Jammu and Kashmir","Jharkhand","Karnataka","Kerala","Madhya Pradesh","Maharashtra","Manipur","Meghalaya","Mizoram","Nagaland","Odisha","Punjab","Rajasthan","Sikkim","Tamil Nadu","Telangana","Tripura","Uttar Pradesh","Uttarakhand","West Bengal","Andaman and Nicobar Islands","Chandigarh","Dadra and Nagar Haveli","Daman and Diu","Lakshadweep","National Capital Territory of Delhi","Puducherry"]

details ={0 : "id", 1:"age",2:"city",3:"diagnosed_date",4:"district",5:"status"}

def getPersonsforState(tx, name):
    l = []
    for record in tx.run("MATCH (l:Location)-[]->(p) "
                         "WHERE l.id = {name} "
                         "RETURN p.id", name=name):
        l.append(record)
    return l
def getPersonsforSource(tx,name):
    l = []
    for record in tx.run("MATCH (p:Person)-[]->(s) "
                         "WHERE s.id = {name} "
                         "RETURN p", name=name):
        l.append(record)
    return l
def getPerson(tx,name):
    for record in tx.run("match(p:Person)" "where p.id = {name}" "return p ",name = name):
        return record
    
def getSource(tx):
    l=[]
    for record in tx.run("match(s:Source) return s.id"):
        l.append(record["s.id"])
    return l
    
def getSourceRecords():
    d={}
    source = session.read_transaction(getSource)
    for i in source:
        d[i] = session.read_transaction(getPersonsforSource, i)
    return d
global hu    
def getStateData():
    d={}
    for i in states:
        d[i] = session.read_transaction(getPersonsforState, i)
    for i,j in d.items():
        #print("jjjjj",j)
        for k in range(len(j)):
            print("kkkkk",j[k])
            hu = j[k]
            j[k] = j[k]["p.id"]
    print(d)        
    return d
    
def find_hotspot():
    d = {}
    d = getStateData()
    hotspot = {}
    for i in d.keys():
        hotspot[i] = len(d[i])
            
    sort = {}
    for w in sorted(hotspot, key=hotspot.get, reverse=True):
        if hotspot[w]>0:
            sort[w] =hotspot[w]
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
    fig = plt.figure(figsize=(15, 10))

    plt.barh(ypos,values,align='center',alpha=0.5)
    plt.yticks(ypos,objects)
    plt.xlabel("Number of confirmed cases")
    plt.title("Hotspots in India")
    plt.show()
    return fig

def getSourceData():
    d={}
     
    source = session.read_transaction(getSource)
    for i in source:
        d[i] = session.read_transaction(getPersonsforSource, i)
   
    for i,j in d.items():
        for k in range(len(j)):
            j[k] = j[k]["p.id"]
    return d
    
def sourceStats():
    d = getSourceData()
    hotspot = {}
    for i in d.keys():
        hotspot[i] = len(d[i])
            
    sort = {}
    for w in sorted(hotspot, key=hotspot.get, reverse=True):
        if hotspot[w]>0:
            sort[w] =hotspot[w]
    return sort
    
def getPersonDetails(n):
    result = session.run("MATCH (p:Person) RETURN p.id, p.age, p.city, p.diagnosed_date, p.district, p.status")
    for record in result:
        if record["p.id"] == n:
            return record
    return -1
            
   
def plotSourceStats(name):
    d = getSourceRecords()
    l = d[name]
    region = {}
    for record in l:
        unique = record
        c = unique[0]["city"]
        if c!= None:
            if c not in region.keys():
                region[c] = 1
            else:
                region[c] += 1
    print(region)       
    objects = ()
    for i in region.keys():
        objects += (i,)
    
    values=[]
    for i in region.values():
        values.append(int(i))
    
    
    fig = plt.figure(figsize=(15, 10))
    

    ax = fig.add_subplot(1,1,1)
    ax.bar(objects,values, width = 0.25)
    try:
        plt.title("Distribution of patients who were in contact with {}".format(int(name)))
        key = session.read_transaction(getPerson, name)
        print(key)
#        textstr = ""
#        for i in details.keys():
#            textstr += details[i]
#            textstr += ":"
#            textstr += key[i]
#            textstr += "\n"
#            plt.xlim(2002, 2008)
#            plt.ylim(0, 4500)
#            
#        plt.text(2000, 2000, textstr, fontsize=14)
    except:
        plt.title("Distribution of patients with travel history to {}".format(name))
    plt.xticks(rotation=90)
    plt.xlabel("City Names")
    plt.ylabel("Number of Cases")
    plt.show()
    return fig
    
#==============================================================================
# after this goes the logic for front-end
#==============================================================================
    
app = Flask(__name__)

@app.route('/')
def home():  
    return render_template('homepage.html')

@app.route('/get_started',methods=['GET','POST'])
def get_started():
    global stack  
    stack = []
    source1 = session.read_transaction(getSource)    
#    if request.method == 'POST':
#        selected = request.form['source']
#        print("WTFFFFF",selected)
#        stack.append(selected)
#        print(stack)
#        fig = plotSourceStats(selected)
#        output = io.BytesIO()
#        FigureCanvas(fig).print_png(output)
            
    return render_template('source.html',options=source1)
    
@app.route('/plot1',methods=['GET','POST'])
def plot1():
    if request.method == 'POST':
        selected = request.form['source']
        print("Here",selected)
        fig = plotSourceStats(selected)
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return Response(output.getvalue(), mimetype='image/png')
    return -1
    #return render_template('plot1.html')
    
@app.route('/hotspot')
def hotspot():
    fig = barPlotHotspots()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')
    
    

if __name__ == '__main__':
    with driver.session() as session:  
        app.run(use_reloader=False)
    driver.close()

    
    

    