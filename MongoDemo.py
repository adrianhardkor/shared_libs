#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
import re
import skinny
import cablemedic
import velocity

import flask
import Mongo
flaskIP = wc.argv_dict['flaskIP']

def flask_RDU():
        @Mongo.MONGO.app.route('/rdu', methods=['GET'])
        def all():
                return(flask.jsonify(Mongo.rduModem.objects()))

# FLASK WEB-API
def flask_default():
        @Mongo.MONGO.app.route('/', methods=['GET'])
        def home():
                return "<h1>DFEAULT</h1><p>Got default, but is working</p>"

if  __name__ == "__main__":
        flask_default()
        flask_RDU()
        Mongo.MONGO.app.run(debug=True, host=flaskIP)

