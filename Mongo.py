#!/usr/bin/env python3
# encoding: utf-8
import sys, os
import flask
from flask_mongoengine import MongoEngine
import json
import wcommon as wc
import time
sys.path.insert(1,'./MongoClasses/')
import soap

# INPUTS
rdu_json = wc.argv_dict['rdu_json']
# flaskIP = wc.argv_dict['flaskIP']

class MDB():
	def __init__(self, MongoIP, MongoPort, MongoName):
		self.MongoIP = MongoIP
		self.MongoPort = MongoPort
		self.MongoName = MongoName
		self.app = flask.Flask(__name__)
		self.app.config['MONGODB_SETTINGS'] = {
			'db': self.MongoName,
			'host': self.MongoIP,
			'port': self.MongoPort,
			'connect': True
		}
		self.M = MongoEngine()
		self.M.init_app(self.app)
		self.__name__ = 'MDB'
	def GetMongoModems(self,myFilter=''):
		return(flask.jsonify(rduModem.objects()))
	def LoadModem(self, data):
		for cmac in data.keys():
			MODEM = soap.FormatRDU_Modem(cmac, data[cmac])
			for unset in list(dir(rduModem)):
				if unset not in MODEM.keys(): MODEM[unset] = ''
			current = rduModem.objects(cmac=cmac)
			wc.pairprint(cmac,len(current))
			if len(current) == 1: cmacM = current[0]; # found existing
			else:
				if len(current) != 0: 
					rduModem.objects(cmac=cmac).delete(); # more than 1, delete all!
				cmacM = rduModem(cmac=cmac,
					access=MODEM['access'],
					chaddr=MODEM['chaddr'],
					clientId=MODEM['clientId'],
					clientIdCreated=MODEM['clientIdCreated'],
					cos=MODEM['cos'],
					deviceType=MODEM['deviceType'],
					domain=MODEM['domain'],
					dhcpMessageType=MODEM['dhcpMessageType'],
					dhcpParamRequestList=MODEM['dhcpParamRequestList'],
					dhcpCriteria=MODEM['dhcpCriteria'],
					DIVISION=MODEM['DIVISION'],
					explanation=MODEM['explanation'],
					giaddr=MODEM['giaddr'],
					hlen=MODEM['hlen'],
					htype=MODEM['htype'],
					isBehindRequiredDevice=MODEM['isBehindRequiredDevice'],
					isProvisioned=MODEM['isProvisioned'],
					isRegistered=MODEM['isRegistered'],
					isInRequiredPortGroup=MODEM['isInRequiredPortGroup'],
					oidRevNum=MODEM['oidRevNum'],
					PACKAGE=MODEM['PACKAGE'],
					provGroup=MODEM['provGroup'],
					reason=MODEM['reason'],
					relayAgentCircuitId=MODEM['relayAgentCircuitId'],
					relayAgentRemoteId=MODEM['relayAgentRemoteId'],
					relayAgentInfo=MODEM['relayAgentInfo'],
					subscriberId=MODEM['subscriberId'],
					viVendorOpts=MODEM['viVendorOpts'],
					vendorEncapsulatedOptions=MODEM['vendorEncapsulatedOptions'],
					timestamp=MODEM['timestamp'])
				cmacM.save()

MONGO = MDB('localhost', 27017, 'admin')

class rduModem(MONGO.M.Document):
	cmac = MONGO.M.StringField(required=True)
	access = MONGO.M.StringField()
	chaddr = MONGO.M.StringField()
	clientId = MONGO.M.StringField()
	clientIdCreated = MONGO.M.StringField()
	cos = MONGO.M.StringField()
	deviceType = MONGO.M.StringField()
	domain = MONGO.M.StringField()
	dhcpMessageType = MONGO.M.StringField()
	dhcpParamRequestList = MONGO.M.StringField()
	dhcpCriteria = MONGO.M.StringField()
	DIVISION = MONGO.M.StringField()
	explanation = MONGO.M.StringField()
	giaddr = MONGO.M.StringField()
	hlen = MONGO.M.StringField()
	htype = MONGO.M.StringField()
	isBehindRequiredDevice = MONGO.M.StringField()
	isProvisioned = MONGO.M.StringField()
	isRegistered = MONGO.M.StringField()
	isInRequiredPortGroup = MONGO.M.StringField()
	oidRevNum = MONGO.M.StringField()
	PACKAGE = MONGO.M.StringField()
	provGroup = MONGO.M.StringField()
	reason = MONGO.M.StringField()
	relayAgentCircuitId = MONGO.M.StringField()
	relayAgentRemoteId = MONGO.M.StringField()
	relayAgentInfo = MONGO.M.StringField()
	subscriberId = MONGO.M.StringField()
	viVendorOpts = MONGO.M.StringField()
	vendorEncapsulatedOptions = MONGO.M.StringField()
	timestamp = MONGO.M.StringField()
	pass

# MONGO.LoadModem(json.loads(wc.read_file(rdu_json)))



#rdu = json.loads(wc.read_file(rdu_json))
#for cmac in rdu.keys():
#	RDU = FormatRDU_Modem(cmac, rdu[cmac]) 
#	# if CMAC doesnt exist, create
#	if list(rduModem.objects(cmac=cmac)) == []:
#		cmacM = rduModem(cmac=cmac, deviceType=RDU['deviceType'],timestamp=str(time.time()))
#		cmacM.save()
# 	rduModem.objects(cmac=cmac).delete()

#def flask_RDU():
#	@app.route('/rdu', methods=['GET'])
#	def all():
#		return(flask.jsonify(rduModem.objects()))
#
## FLASK WEB-API
#def flask_default():
#	@app.route('/', methods=['GET'])
#	def home():
#		return "<h1>DFEAULT</h1><p>Got default, but is working</p>"

