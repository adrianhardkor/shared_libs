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
flaskIP = wc.cleanLine(wc.grep('10.88', wc.exec2('ifconfig')))[1]


def flask_RDU():
	@Mongo.MONGO.app.route('/rdu', methods=['GET'])
	def rdu():
		# return(flask.jsonify(Mongo.rduModem.objects()))
		return(flask.jsonify(Mongo.MONGO._GETJSON(Mongo.rduModem)))

def flask_AIS():
	@Mongo.MONGO.app.route('/ais', methods=['GET'])
	def ais():
		AIS = {}
		if flask.request.args == {}:
			routers = Mongo.MONGO._GETJSON(Mongo.Router)
			servers = Mongo.MONGO._GETJSON(Mongo.Server)
			CMTSs = Mongo.MONGO._GETJSON(Mongo.CMTS)
			modems = Mongo.MONGO._GETJSON(Mongo.Modem)
			SGs = Mongo.MONGO._GETJSON(Mongo.SG)
		else:
			routers = Mongo.MONGO._GETJSON(Mongo.Router, criteria=flask.request.args)
			servers = Mongo.MONGO._GETJSON(Mongo.Server, criteria=flask.request.args)
			CMTSs = Mongo.MONGO._GETJSON(Mongo.CMTS, criteria=flask.request.args)
			modems = Mongo.MONGO._GETJSON(Mongo.Modem, criteria=flask.request.args)
			SGs = Mongo.MONGO._GETJSON(Mongo.SG, criteria=flask.request.args)
			wc.jd(flask.request.args)
		for deviceTypeObj in [routers, servers, CMTSs, modems, SGs]:
			for deviceObject in deviceTypeObj:
				if 'name' not in deviceObject.keys(): return(flask.jsonify(deviceObject))
				AIS[deviceObject['name']] = deviceObject
		return(flask.jsonify(AIS))

def flask_RunJenkinsPipeline():
	@Mongo.MONGO.app.route('/runJenkinsPipeline', methods=['POST'])
	def pipeline():
		# create jenkins class
		# connect to jenkins
		# run 
		pass

def flask_vAGENT():
	@Mongo.MONGO.app.route('/vAgent', methods = ['POST, GET'])
	if flask.request.method == 'POST':
		wc.jd(flask.request.form)
		user = flask.request.form['nm']
		return redirect(flask.url_for('success',name = user))
	else:
		response = {}
		for deviceObj in Mongo.MONGO._GETJSON(Mongo.vAGENT, criteria=flask.request.args):
			response[deviceObj['reportId']] = deviceObj
		return(flask.jsonify(response))

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
	flask_vAGENT(); # /vAgent
	Mongo.MONGO.app.run(debug=True, host=flaskIP)

