#!/usr/bin/env python3
import os
import sys
import wcommon as wc
if 'port' not in wc.argv_dict.keys(): wc.argv_dict['port'] = '5000'
from werkzeug.utils import secure_filename
import json
import re
import skinny
# import cablemedic
import velocity
import flask
import Mongo; # shared_libs
import time
import paramiko
import qrcode
from qrcode.image.pure import PymagingImage
import base64
from io import BytesIO

flaskIP = wc.cleanLine(wc.grep('10.88', wc.exec2('ifconfig')))[1]
# wc.jd(wc.wcheader)
# Mongo.TryDeleteDocuments(Mongo.runner)

def flaskArgsPayload():
	try:
		args = {k: v for k, v in flask.request.args.items()}
	except Exception:
		args = {}
	try:
		payload = {k: v for k, v in flask.request.get_json().items()}
	except Exception:
		payload = {}
	return(args,payload)

def vagent_getter():
	response = {}
	args,payload = flaskArgsPayload()
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
		args,payload = flaskArgsPayload()
		Mongo.MONGO.app.config['UPLOAD_FOLDER'] = './'
		_FNAME = str(flask.request.files['file']).split("'")[1]
		wc.pairprint(_FNAME, os.path.exists('./' + _FNAME)) 
		if os.path.exists('./' + str(flask.request.files['file'])) is False:
			wc.exec2('/usr/bin/touch ./' + _FNAME)
		f = flask.request.files['file']
		secure_f = secure_filename(f.filename)
		f.save(secure_f)
		print('\n\n\n')
		wc.pairprint(f.filename, secure_f)
		print('\n\n\n')
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
			Firewalls = Mongo.MONGO._GETJSON(Mongo.Firewall)
		else:
			routers = Mongo.MONGO._GETJSON(Mongo.Router, criteria=flask.request.args)
			servers = Mongo.MONGO._GETJSON(Mongo.Server, criteria=flask.request.args)
			CMTSs = Mongo.MONGO._GETJSON(Mongo.CMTS, criteria=flask.request.args)
			modems = Mongo.MONGO._GETJSON(Mongo.Modem, criteria=flask.request.args)
			SGs = Mongo.MONGO._GETJSON(Mongo.SG, criteria=flask.request.args)
			Firewalls = Mongo.MONGO._GETJSON(Mongo.Firewall, criteria=flask.request.args)
			wc.jd(flask.request.args)
		for deviceTypeObj in [routers, servers, CMTSs, modems, SGs]:
			for deviceObject in deviceTypeObj:
				if 'name' not in deviceObject.keys(): return(flask.jsonify(deviceObject))
				AIS[deviceObject['name']] = deviceObject
		return(flask.jsonify(AIS))

def flask_NewCall():
	@Mongo.MONGO.app.route('/new_call', methods=['GET'])
	def new():
		return(flask.jsonify({'got':'logs?'}))

def flask_RunJenkinsPipeline():
	@Mongo.MONGO.app.route('/jenkins/runPipe', methods=['POST'])
	def pipeline():
		args,body = flaskArgsPayload()
		import jenkins
		J = jenkins.JENKINS(body.pop('JEN_IP'), body.pop('username'), body.pop('token'))
		monitor = J.RunPipeline(body['Pipe'], body)
		wc.pairprint('monitor', monitor)
		return(flask.jsonify({'monitor':'http://10.88.48.21:' + str(wc.argv_dict['port']) + '/runner?runId=' + str(monitor)}))

def flask_validate():
	@Mongo.MONGO.app.route('/validate', methods = ['GET'])
	def validate():
		validate = wc.timer_index_start()
		args,payload = flaskArgsPayload()
		uuid = ''
		if 'uuid' in args.keys():  uuid = args['uuid']

		repos = wc.exec2('cd ../asset-data/; git checkout %s; git pull origin %s; find ./;' % (args['branch'],args['branch'])).split('\n')
		out = wc.lsearchAllInline('branch is', repos)
		out.append(wc.validateITSM(repos, uuid, directory='../asset-data/', CIDR='10.88.0.0/16'))
		out.append('runtime:' + str(wc.timer_index_since(validate)) + ' ms')
		return(flask.jsonify(wc.lunique(out)))

def flask_runtimelogger():
	@Mongo.MONGO.app.route('/runner', methods = ['POST', 'GET', 'PUT'])
	def run():
		wc.pairprint('runner:   method', flask.request.method)
		if str(flask.request.method) != 'GET':
			args,payload = flaskArgsPayload()
			try:
				Mongo.MONGO._UPDATE(Mongo.runner, args, payload)
				return(flask.jsonify(vagent_getter()))
			except Exception as err:
				return(json.dumps({'err':str(err)}))
		else:
			# wc.jd(vagent_getter())
			return(flask.jsonify(vagent_getter())); # [GET]

def GenQR_PNG(url):
	img = qrcode.make(url, image_factory=PymagingImage)
	buffered = BytesIO()
	img.save(buffered)
	return(base64.b64encode(buffered.getvalue()).decode())

def flask_qr():
	@Mongo.MONGO.app.route('/qrservice', methods = ['GET'])
	def qr():
		qr_fname = 'qr.png'
		# wc.rmf('templates/' + qr_fname)
		myUUID = wc.genUUID(); # if identifyer='' then random
		link = 'http://10.88.48.21:5000/ais?uuid=' + myUUID
		args,payload = flaskArgsPayload()
		if 'instructions' in args.keys():
			return(flask.render_template(args['instructions'] + '.html'))
		img_str = GenQR_PNG(link)
		result = flask.render_template('qr_page.html', adrian_test=str(args), img_str=img_str, link=link, myUUID=myUUID, dcim=wc.read_file('templates/dcim.yml').split("\n"), itsm=wc.read_file('templates/itsm.yml').split("\n"), cable=wc.read_file('templates/cable.yml').split("\n"))
		return(result)

def ParseSettingsYML(url):
	settings = json.loads(wc.REST_GET(url))['response.body']
	s = {}
	for line in settings.split('\n'):
		if line.startswith('  '):
			sline = line.split(':')
			index = sline.pop(0).strip()
			value = ':'.join(sline).strip()
			value = wc.mcsplit(value, ['"',"'"])
			try:
				value.pop(-1)
				value.pop(0)
			except Exception:
				pass
			value = ','.join(value)
			# if len(value) == 1: value = value[0]
			# else: value = value[1]
			s[path][index] = value
		else:
			path = line.strip(':')
			s[path] = {}
	return(s)

def PullCmds(args):
	result = []
	for a in sorted(wc.lsearchAllInline('cmd', list(args.keys()))):
		# &cmd1=blah&cmd2=blah
		result.append(args[a].replace('_',' '))
	return(result)

def flask_AIEngine():
	@Mongo.MONGO.app.route('/aie', methods = ['GET'])
	def engine():
		timer = int(time.time())
		paramiko_args = {}
		result = {}
		args,payload = flaskArgsPayload()
		# INVENTORY = RAW.INVENTORY.YML?
		settings = ParseSettingsYML('https://raw.githubusercontent.com/adrianhardkor/shared_libs/main/settings.yml')
		settings_name = args['settings']
		settings = settings[settings_name]
		# return(flask.jsonify(settings))
		CMDS = PullCmds(args)
		if settings['private_key_file'].endswith('.txt'):
			# first line
			# u/p/p
			upp = wc.read_file(settings['private_key_file']).split('\n')
			paramiko_args['password'] = upp[0]
			if len(upp) > 1: paramiko_args['become'] = upp[1]
		else: paramiko_args['key_fname'] = settings['private_key_file']
		if settings['vendor'] == 'gainspeed':
			blind = {'commands':['show config | match prompt'],'ip':args['hostname'],'username':settings['username'],'password':wc.read_file(settings['private_key_file']),'windowing':False,'ping':False,'quiet':False}
			prompt = wc.cleanLine(wc.PARA_CMD_LIST(**blind)[0])
			settings['prompt'] = '|'.join([ prompt[1].split(';')[0],  prompt[3].split(';')[0] ])
		paramiko_args['commands'] = CMDS
		paramiko_args['ip'] = args['hostname']
		paramiko_args['driver'] = settings['vendor']
		paramiko_args['username'] = settings['username']
		paramiko_args['ping'] = False
		paramiko_args['quiet'] = True
		if 'buffering' in settings.keys(): paramiko_args['buffering'] = settings['buffering']
		paramiko_args['settings_prompt'] = settings['prompt']
		# wc.jd(paramiko_args)
		try:
			raw = wc.PARA_CMD_LIST(**paramiko_args)
		except Exception as err:
			return(flask.jsonify({'err': str(err)}))
		for cmd in raw.keys():
			if cmd == "_": pass
			elif 'json' in wc.cleanLine(cmd): 
				# JUNIPER
				# wc.jd(raw[cmd].split('\r\n')[0:-2])
				raw[cmd] = '\n'.join(raw[cmd].split('\r\n')[0:-2])
				raw[cmd] = json.loads(raw[cmd])
			elif 'xml' in wc.cleanLine(cmd):
				raw[cmd] = '\n'.join(raw[cmd].split('\r\n')[0:-2])
				raw[cmd] = wc.xml_loads(raw[cmd])
			elif type(raw[cmd]) == dict: pass
			else: raw[cmd] = raw[cmd].split('\r\n')
		return(flask.jsonify(raw)); # {'command': 'output'}

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
	flask_AIEngine(); # /aie?hostname=10.88.240.26
	flask_downloader()
	flask_validate() # /validate
	flask_AIS(); # /ais
	flask_NewCall(); # /new_call
	flask_RunJenkinsPipeline()
	flask_qr(); # / qr
	flask_runtimelogger(); # /runner
	if 'port' in wc.argv_dict.keys():
		Mongo.MONGO.app.run(debug=True, host=flaskIP, port=int(wc.argv_dict['port']))
	else: Mongo.MONGO.app.run(debug=True, host=flaskIP)

