
# This app build a URL reporting app for SRX using Flask, bootstrap template and PyEZ library. There must be a log file name "weblog" in the /cf/var/log/ directory. 

### Mac: 
----------------
```sh
	% mongod & 
	$ python app.py
```

### Ubuntu: 
------------------
```sh
	$ python app.py
```

## Manually build all the python libraries
1. Update ubuntu:
-----------------

```sh 

		$ sudo apt-get update
		$ sudo apt-get install python-pip
```

2. Install Mongodb:
-------------------

```sh 

		$ sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10

		$ echo "deb http://repo.mongodb.org/apt/ubuntu "$(lsb_release -sc)"/mongodb-org/3.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.0.list

		$ sudo apt-get update
		$ sudo apt-get install -y mongodb-org
``` 

3. Install Python Library:
--------------------------


```sh 
		$ sudo pip install pymongo
		$ sudo pip install flask
		$ sudo apt-get install git
```

4. A. Install Python lxml module:
---------------------------------

```sh
		$ sudo apt-get install libxml2-dev libxslt-dev python-dev
		$ sudo pip install pycrypto
		$ sudo apt-get install zlib1g-dev
		$ sudo pip install lxml 
```

4. B. Build junos-eznc:
-----------------------

```sh
		$ sudo pip install junos-eznc
```

5. Install wkhtmltopdf
----------------------

6. To run:  
------------------
```sh
		 % cd srx-weblog
		 % python app.py
```
