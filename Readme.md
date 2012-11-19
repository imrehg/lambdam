LambdaM
=======

Lightweight wavemeter control and display environment.

Requirements
============

**Server**:

 * node.js, download from http://nodejs.org/

**Client**:

 * Python (2.7.x), download from http://www.python.org/download/
 * pySerial (the latest one, eg. 2.5 at the time of this writing), download from http://sourceforge.net/projects/pyserial/files/pyserial/ for Windows

Usage
=====

First time
----------

Update node packages (in the command line, or using `cmd.exe` in Windows) inside the project directory (where `package.json` is):

    npm install

This should install all necessary packages. If you already have the `node_packages` directory there (copied the project), then might not need to do it.

Other times
-----------

Run the server with the included batch scripts (`startweb.bat` for webserver and `startwave.bat` wavemeter logger) or directly run using the command line, from within the project's root directory:

    node server.js

and in the client directory

    C:\Python27\python.exe client\wavemeter.py

on Windows

Go to [http://localhost:5000](http://localhost:5000)

Test client
-----------

Example python client included, within the client directory, requires python 2.7 (maybe?)

    python testconn.py
