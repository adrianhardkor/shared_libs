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

def dictFlask(input1):
	# rebuild flask.request objects as dict -- ugly but works
	out = {}
	for k in input1.keys():
		out[k] = input1[k]
	return(out)

def vagent_getter():
	response = {}
	args = dictFlask(flask.request.args)
	if args == {}: objects = Mongo.MONGO._GETJSON(Mongo.vAgent)
	else: objects = Mongo.MONGO._GETJSON(Mongo.vAgent, criteria=args)
	for deviceObj in objects:
		if 'reportId' not in deviceObj.keys(): deviceObj['reportId'] = 'missing'
		response[deviceObj['reportId']] = deviceObj
	return(response)

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
	@Mongo.MONGO.app.route('/vAgent', methods = ['POST', 'GET'])
	def vAgent():
		wc.pairprint('method', flask.request.method)
		if flask.request.method == 'POST':
			args = dictFlask(flask.request.args)
			payload = dictFlask(flask.request.get_json())
			wc.jd(args)
			wc.jd(payload)
			try:
				Mongo.MONGO._UPDATE(Mongo.vAgent, args, payload)
				return(flask.jsonify(vagent_getter()))
			except Exception as err:
				return(json.dumps({'err':str(err)}))
		else: return(flask.jsonify(vagent_getter())); # [GET]

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

