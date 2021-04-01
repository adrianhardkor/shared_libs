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
import Mongo; # shared_libs
flaskIP = wc.argv_dict['flaskIP']

def flask_RDU():
	@Mongo.MONGO.app.route('/rdu', methods=['GET'])
	def rdu():
		# return(flask.jsonify(Mongo.rduModem.objects()))
		return(flask.jsonify(Mongo.MONGO._GETJSON(Mongo.rduModem)))

def flask_AIS():
	@Mongo.MONGO.app.route('/ais', methods=['GET'])
	def ais():
		AIS = {}
		for router in Mongo.MONGO._GETJSON(Mongo.Router):
			# list per mongo, choose top-id
			AIS[router['name']] = router
		return(flask.jsonify(AIS))

def flask_RunJenkinsPipeline():
	@Mongo.MONGO.app.route('/runJenkinsPipeline', methods=['POST'])
	def pipeline():
		# create jenkins class
		# connect to jenkins
		# run 
		pass

# FLASK WEB-API
def flask_default():
	@Mongo.MONGO.app.route('/', methods=['GET'])
	def home():
		return "<h1>DFEAULT</h1><p>Got default, but is working</p>"

if  __name__ == "__main__":
	# Executables
	flask_default()
	flask_RDU(); # /rdu
	flask_AIS(); # /ais
	Mongo.MONGO.app.run(debug=True, host=flaskIP)
