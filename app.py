__author__ = 'aleung@juniper.net'


#
# Copyright (c) 2008 - 2015 
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#

from flask import Flask, render_template, request, redirect, url_for, jsonify
from jnpr.junos import Device
from jnpr.junos.exception import ConnectAuthError, ConnectTimeoutError, ConnectError 
from lxml import etree
import json
import pymongo
import re
from jnpr.junos.utils.scp import SCP
from scp import SCPException
from bson.son import SON
from pprint import pprint as pp

app = Flask(__name__)
app.secret_key = "juniper"
connection_string = "mongodb://localhost"
connection = pymongo.MongoClient(connection_string)
database = connection.srx
device = {}

# route for handling the SRX login 
@app.route('/', methods=['GET','POST'])
@app.route('/login', methods=['GET','POST'])
def login():
    # For vSRX we create a logfile 'weblog', which stores under /cf/var/log dir
    # For branch or highend srx, the log file location can be different.
    filename = 'weblog' 
    ff = '/cf/var/log/'+filename
    error = None
    if request.method == 'POST':
    	hostname = request.form['hostname'] 
        username = request.form['username'] 
        password = request.form['password']
        #
        # Retrieve device information
        #
        dev = Device(hostname,user=username,password=password)

        try:
            dev.open()

        except ConnectAuthError:
            error = 'Wrong Credentials. Please try again.'
            return render_template('login.html',error=error)

        except ConnectTimeoutError:
            error = 'Timeout. Host not reachable?'
            return render_template('login.html',error=error)

        except ConnectError:
            error = 'Huh... something wrong. Try again?'
            return render_template('login.html',error=error)

        print "Login success"
        #  Print device info
        global device
        device = dev.facts
 
        # Drop the previous db collection "websession" if exists
        # Read the content of logfile and store in MongoDB
        database.websessions.drop()
        with SCP(dev) as scp:
             try:
                scp.get(ff,filename)
             except SCPException:
                error = 'No such files. Please try again.'
                return render_template('login.html',error=error)
        print "Got file!"
        fd = open(filename,'rU')
        for line in fd:
           ##
           ## match URL=xxx.yyy.com, and x.x.x.x()y.y.y.y()
           ##
           match1 = re.search(r'(URL)=(\S+\.\S+\.\S+)',line)
           match23 = re.search(r'(\d+\.\d+\.\d+\.\d+)\S+->(\d+\.\d+\.\d+\.\d+)',line)
           match4 = re.search(r'(CATEGORY)=\"(\S+)\"',line)
           if match1 and match23 and match4:
               url = match1.group(2)
               source = match23.group(1)
               destination = match23.group(2)
               category = match4.group(2)
               flow = {
                   "url": url,
                   "source": source,
                   "destination": destination,
                   "category": category
                   }
               database.websessions.insert(flow)
        dev.close()
        return redirect(url_for('get_device'))
    return render_template('login.html', error=error)

@app.route('/device_info')
def get_device():
    data = device
    return render_template('device.html', data=data)

@app.route('/URLs')
def url_report():
   pipeline = [{"$group":{"_id":"$url","count":{"$sum":1}}},{"$sort":SON([("count",-1)])},{"$project":{"_id":0,"url":"$_id","count":1}},{"$limit":10}]  
   print "Top N URLs"
   ### Uncomment these 2 lines for MAC
   ### Debug: pp(database.websessions.aggregate(pipeline)['result'])                                   
   data = database.websessions.aggregate(pipeline)['result']                                   
   ###
   ### Uncomment this line for Ubuntu
   ###data = list(database.websessions.aggregate(pipeline))

   return render_template('report.html', 
        title = "Top 10 URLs", data=data, labels=[{'x':'count'},{'y':'url'}])                                  

@app.route('/url_details')
def url_details():
   pipeline = [{"$group":{"_id":"$url","count":{"$sum":1}}},{"$sort":SON([("count",-1)])},{"$project":{"_id":0,"url":"$_id","count":1}}]  
   print "Top N URLs"
   ### Uncomment these 2 lines for MAC
   ### Debug: pp(database.websessions.aggregate(pipeline)['result'])                                   
   data = database.websessions.aggregate(pipeline)['result']                                   
   ###
   ### Uncomment this line for Ubuntu
   ###data = list(database.websessions.aggregate(pipeline))

   return render_template('details.html', title = "URL details", index="url", data=data) 

@app.route('/Categories')
def categories_report():
   pipeline = [{"$group":{"_id":"$category","count":{"$sum":1}}},{"$sort":SON([("count",-1)])},{"$project":{"_id":0,"category":"$_id","count":1}},{"$limit":10}]  
   print "Top N Categories"
   ### Uncomment these 2 lines for MAC
   ### pp(database.websessions.aggregate(pipeline)['result'])                                   
   data = database.websessions.aggregate(pipeline)['result']                                   
   ###
   ### Uncomment this line for Ubuntu
   ###data = list(database.websessions.aggregate(pipeline))

   return render_template('report.html', 
        title = "Top Categories", data=data, labels=[{'x':'count'},{'y':'category'}])                                  

@app.route('/category_details')
def category_details():
   pipeline = [{"$group":{"_id":"$category","count":{"$sum":1}}},{"$sort":SON([("count",-1)])},{"$project":{"_id":0,"category":"$_id","count":1}}]  
   print "Top N Categories"
   ### Uncomment these 2 lines for MAC
   ### pp(database.websessions.aggregate(pipeline)['result'])                                   
   data = database.websessions.aggregate(pipeline)['result']                                   
   ###
   ### Uncomment this line for Ubuntu
   ###data = list(database.websessions.aggregate(pipeline))
   return render_template('details.html', title = "Category details", index='category', data=data) 

@app.route('/Talkers')
def talkers_report():
   pipeline = [{"$group":{"_id":"$source","count":{"$sum":1}}},{"$sort":SON([("count",-1)])},{"$project":{"_id":0,"source":"$_id","count":1}},{"$limit":10}]  
   print "Top N Talkers"
   ### Uncomment these 2 lines for MAC
   ### pp(database.websessions.aggregate(pipeline)['result'])                                   
   data = database.websessions.aggregate(pipeline)['result']                                   
   ###
   ### Uncomment this line for Ubuntu
   ###data = list(database.websessions.aggregate(pipeline))

   return render_template('report.html', 
        title = "Top Talkers", data=data, labels=[{'x':'count'},{'y':'source'}])                                  

@app.route('/talker_details')
def talker_details():
   pipeline = [{"$group":{"_id":"$source","count":{"$sum":1}}},{"$sort":SON([("count",-1)])},{"$project":{"_id":0,"source":"$_id","count":1}}]  
   print "Top N Categories"
   ### Uncomment these 2 lines for MAC
   ### pp(database.websessions.aggregate(pipeline)['result'])                                   
   data = database.websessions.aggregate(pipeline)['result']                                   
   ###
   ### Uncomment this line for Ubuntu
   ###data = list(database.websessions.aggregate(pipeline))
   return render_template('details.html', title = "Talkers", index='source', data=data) 

if __name__ == '__main__':
	app.run( host='0.0.0.0', port=5000, debug=True)



