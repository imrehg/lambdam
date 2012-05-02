LambdaM
=======

Lightweight wavemeter control and display environment.

Requirements
============

Server: node.js, download from http://nodejs.org/

Developement can be made easier by running it with ruby + foreman + rerun.

Usage
=====

First time
----------

Update node packages:

    npm install

This should install all necessary packages based on package.json.

Other times
-----------

Run the server with:

    node server.js

Or for development:

    rerun foreman start

Go to [http://localhost:5000](http://localhost:5000)

Test client
-----------

Example python client included, within the client directory, requires python 2.7 (maybe?)

    python testconn.py