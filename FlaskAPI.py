#!/usr/bin/env python3
import os
import sys
import wcommon as wc
from werkzeug.utils import secure_filename
import json
import re
import skinny
import cablemedic
import velocity
import flask
import Mongo; # shared_libs
flaskIP = wc.cleanLine(wc.grep('10.88', wc.exec2('ifconfig')))[1]

# Mongo.TryDeleteDocuments(Mongo.runner)

def dictFlask(input1):
	# rebuild flask.request objects as dict -- ugly but works
	out = {}
	if input1 == None: return(out)
	for k in input1.keys():
		out[k] = input1[k]
	return(out)

def vagent_getter():
	response = {}
	args = dictFlask(flask.request.args)
	if args == {}: objects = Mongo.MONGO._GETJSON(Mongo.runner)
	else: objects = Mongo.MONGO._GETJSON(Mongo.runner, criteria=args)
	fake = 1
	for deviceObj in objects:
		if 'runId' not in deviceObj.keys():
			deviceObj['runId'] = str(fake)
			fake = fake + 1
		response[deviceObj['runId']] = deviceObj
	return(response)

def flask_RDU():
	@Mongo.MONGO.app.route('/rdu', methods=['GET'])
	def rdu():
		# return(flask.jsonify(Mongo.rduModem.objects()))
		return(flask.jsonify(Mongo.MONGO._GETJSON(Mongo.rduModem)))

def flask_downloader():
	@Mongo.MONGO.app.route('/download', methods=['GET'])
	def downloadFile():
		#For windows you need to use drive name [ex: F:/Example.pdf]
		# /download?fname=adrian_test.csv
		fname = flask.request.args['fname']
		return(flask.send_file('./' + fname, as_attachment=True))


def flask_uploader():
	@Mongo.MONGO.app.route('/upload', methods = ['POST'])
	def upload_file():
		args = dictFlask(flask.request.args)
		payload = dictFlask(flask.request.get_json())
		wc.jd(args)
		wc.jd(payload)
		Mongo.MONGO.app.config['UPLOAD_FOLDER'] = './'
		f = flask.request.files['file']
		f.save(secure_filename(f.filename))
		return('file uploaded successfully')
  

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
	@Mongo.MONGO.app.route('/jenkins/runPipe', methods=['POST'])
	def pipeline():
		args = dictFlask(flask.request.args)
		wc.jd(args)
# J = JENKINS(wc.argv_dict['IP'], wc.argv_dict['user'], wc.env_dict['JEN_TOKEN'])
# param = {'Playbook':'ARC_GetFactsMultivendor','sendmail':'adrian.krygowski'}
# param['dryrun'] = 'dryrun'
# J.RunPipeline(wc.argv_dict['Pipe'], param)
# curl -X POST http://jenkinUser:jenkinAPIToken@yourJenkinsURl.com/job/theJob/[11-1717]/doDelete


		# create jenkins class
		# connect to jenkins
		# run 
		pass

def flask_runtimelogger():
	@Mongo.MONGO.app.route('/runner', methods = ['POST', 'GET', 'PUT'])
	def run():
		wc.pairprint('method', flask.request.method)
		if flask.request.method != 'GET':
			args = dictFlask(flask.request.args)
			payload = dictFlask(flask.request.get_json())
			wc.jd(args)
			wc.jd(payload)
			try:
				Mongo.MONGO._UPDATE(Mongo.runner, args, payload)
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
	flask_uploader()
	flask_downloader()
	flask_AIS(); # /ais
	flask_runtimelogger(); # /runner
	if 'port' in wc.argv_dict.keys():
		Mongo.MONGO.app.run(debug=True, host=flaskIP, port=int(wc.argv_dict['port']))
	else: Mongo.MONGO.app.run(debug=True, host=flaskIP)

