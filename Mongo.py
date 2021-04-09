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
# rdu_json = wc.argv_dict['rdu_json']
# flaskIP = wc.argv_dict['flaskIP']

def compareForPUT(old,new):
	compare = wc.compareDict(old,new)
	if compare != {} and compare != "{}":
		# print(compare)
		return(True)
	return(False)

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
		self.DocumentMethods = sorted(list(dir(self.M.Document)))
		self.DocumentMethods.append('objects')
		self.DocumentMethods.append('DoesNotExist')
		self.DocumentMethods.append('MultipleObjectsReturned')
		self.DocumentMethods.append('id')
		self.__name__ = 'MDB'
	def _TEMPLATE_CRITERIA(self, _TEMPLATE):
		raw = sorted(list(dir(_TEMPLATE)))
		clean = []
		for r in raw:
			if r not in self.DocumentMethods: clean.append(r)
		return(clean)
	def _PUT(self, _TEMPLATE, criteria_GET, criteria_SET):
		if criteria_GET == {}:
			# all elements push
			_TEMPLATE.objects.update(**criteria_SET)
			wc.pairprint('Mongo._PUT\tALL', criteria_SET)
			return()
		current = self._GET(_TEMPLATE, criteria=criteria_GET).first(); # per device

		# Compare Current vs. New = rebuild criteria_SET
		cSET = {}
		currentJSON = json.loads(current.to_json())
		for old in criteria_SET.keys():
			if old not in currentJSON:
				cSET[old] = criteria_SET[old]
			elif type(currentJSON[old]) == dict:
				if compareForPUT(currentJSON[old],criteria_SET[old]):  cSET[old] = criteria_SET[old]
			elif type(currentJSON[old]) == list:
				# NEEDS POSSIBLE EFFICENCY? PORTS?
				if wc.compareList(currentJSON[old],criteria_SET[old]) is False:
					cSET[old] = criteria_SET[old]
			elif currentJSON[old] != criteria_SET[old]:
				cSET[old] = criteria_SET[old]
#			if old in cSET and old == 'velocityARC':
#				wc.jd(currentJSON[old])
#				wc.jd(cSET[old])
#				print(old)
		# {'ports': [{'name': 'ae0'}]}

		#current = _TEMPLATE.objects(_id="....").first()
		#for port in current.ports:
		#    if port.text == "title":
		#        port.value = "placeholder for real update"
		#current.save()

		# _TEMPLATE.objects(_id="...", ports__name="findvalue").update(set__ports__S__value="updatevalue")
		# doc = MyModel.objects.find(<model-key> = <model-val>, <embedded-doc-key>__<embedded-doc-lookup-key> = <lookup-key-val>)
		# doc.update(set__<embedded-doc-key>__S__<embedded-doc-lookup-key> = <new-val>)
		if cSET != {}:
			current.update(**cSET)
			current.save()
			wc.pairprint('Mongo._PUT:  ' + str(criteria_GET), sorted(list(cSET.keys())))
	def _POST(self, _TEMPLATE, criteria_SET, name):
		_OBJECT = _TEMPLATE(**criteria_SET)
		_OBJECT.save()
		wc.pairprint('Mongo._POST', name)
	def _GET(self, _TEMPLATE, criteria={}):
		if criteria == {}: return(_TEMPLATE.objects())
		else: return(_TEMPLATE.objects(**criteria))
	def _GETJSON(self, _TEMPLATE, criteria={}):
		try:
			_obj = self._GET(_TEMPLATE, criteria=criteria)
			return(json.loads(_obj.to_json())); # returns type(dict)
		except Exception:
			return({})
	def _DELETE(self, _TEMPLATE, criteria={}, force=False):
		if criteria == {}: 
			if not force: wc.pairprint("Mongo._DELETE Cannot be for all objects", _TEMPLATE)
			else: 
				_TEMPLATE.objects().delete(); # ALL IN MONGO
				wc.pairprint("Mongo._DELETE", "Wipe Template")
		else: 
			_TEMPLATE.objects(**criteria).delete()
			wc.pairprint('Mongo._DELETE', criteria)
	def _UPDATE(self, _TEMPLATE, criteria_GET, criteria_SET):
		# CRITERIA_GET MUST BE UNIQUE
		# ONLY 1 DEVICE/PORT/ELEMENT SHOULD RESOND PER CALL
		current = self._GET(_TEMPLATE, criteria=criteria_GET)
		if len(current) == 1:
			# PUT
			self._PUT(_TEMPLATE, criteria_GET=criteria_GET, criteria_SET=criteria_SET)
		else:
			if len(current) != 0:
				# CLEANUP NEEDED (DELETE ALL IF MORE THAN ONE DUPLICATE CRITERIA_GET)
				self._DELETE(_TEMPLATE, criteria=criteria_GET)
				wc.pairprint('Mongo._DELETE', criteria_GET)
			self._POST(_TEMPLATE, criteria_SET, criteria_GET)
	def LoadModem(self, data):
		# DELETE OLD
		# IF MODEM.MONGO NOT IN MODEM.JSON-RDU: DELETE
		allRM = self._GET(rduModem)
		for rm in allRM:
			# if rm.cmac == '': print(flask.jsonify(rduModem.objects()))
			if str(rm.cmac) not in data.keys(): self._DELETE(rduModem, {'cmac':rm.cmac})
		# ADD NEW
		for cmac in data.keys():
			MODEM = soap.FormatRDU_Modem(cmac, data[cmac])
			MODEM['cmac'] = cmac; # json into object.index
			MODEM['timestamp'] = time.ctime(time.time())
			criteria = {}
			for crit in self._TEMPLATE_CRITERIA(rduModem):
				if crit not in MODEM.keys(): MODEM[crit] = ''
			# wc.jd(MODEM)
			self._UPDATE(rduModem, {'cmac':cmac}, MODEM)

MONGO = MDB('localhost', 27017, 'admin')
# SCALE ALL FURTHER CLASSES/DOCUMENTS IN ORDER OF CALLS/REFERENCES

class rduModem(MONGO.M.Document):
	cmac = MONGO.M.StringField(required=True)
	access = MONGO.M.StringField()
	chaddr = MONGO.M.StringField()
	clientid = MONGO.M.StringField()
	clientidcreatedfrommacaddress = MONGO.M.StringField()
	cos = MONGO.M.StringField()
	detected = MONGO.M.StringField()
	deviceType = MONGO.M.StringField()
	domain = MONGO.M.StringField()
	dhcpmessagetype = MONGO.M.StringField()
	dhcpparameterrequestlist = MONGO.M.StringField()
	dhcpCriteria = MONGO.M.StringField()
	dhcpclassidentifier = MONGO.M.StringField()
	docsisVersion = MONGO.M.StringField()
	DIVISION = MONGO.M.StringField()
	e = MONGO.M.StringField()
	explanation = MONGO.M.StringField()
	giaddr = MONGO.M.StringField()
	hlen = MONGO.M.StringField()
	htype = MONGO.M.StringField()
	isBehindRequiredDevice = MONGO.M.StringField()
	isProvisioned = MONGO.M.StringField()
	isRegistered = MONGO.M.StringField()
	isInRequiredProvGroup = MONGO.M.StringField()
	provGroup = MONGO.M.StringField()
	isInRequiredPortGroup = MONGO.M.StringField()
	oidRevisionNumber = MONGO.M.StringField()
	mac = MONGO.M.StringField()
	node = MONGO.M.StringField()
	PACKAGE = MONGO.M.StringField()
	reason = MONGO.M.StringField()
	relayagentcircuitid = MONGO.M.StringField()
	relayagentremoteid = MONGO.M.StringField()
	relayagentinfo = MONGO.M.StringField()
	selected = MONGO.M.StringField()
	subscriberId = MONGO.M.StringField()
	vivendoropts = MONGO.M.StringField()
	vendorencapsulatedoptions = MONGO.M.StringField()
	timestamp = MONGO.M.StringField()
	dhcpv4 = MONGO.M.StringField()
	pass


class rduModemEmbed(MONGO.M.EmbeddedDocument):
	_id = MONGO.M.DictField()
	cmac = MONGO.M.StringField(required=True)
	access = MONGO.M.StringField()
	chaddr = MONGO.M.StringField()
	clientid = MONGO.M.StringField()
	clientidcreatedfrommacaddress = MONGO.M.StringField()
	cos = MONGO.M.StringField()
	detected = MONGO.M.StringField()
	deviceType = MONGO.M.StringField()
	domain = MONGO.M.StringField()
	dhcpmessagetype = MONGO.M.StringField()
	dhcpparameterrequestlist = MONGO.M.StringField()
	dhcpCriteria = MONGO.M.StringField()
	dhcpclassidentifier = MONGO.M.StringField()
	docsisVersion = MONGO.M.StringField()
	DIVISION = MONGO.M.StringField()
	e = MONGO.M.StringField()
	explanation = MONGO.M.StringField()
	giaddr = MONGO.M.StringField()
	hlen = MONGO.M.StringField()
	htype = MONGO.M.StringField()
	isBehindRequiredDevice = MONGO.M.StringField()
	isProvisioned = MONGO.M.StringField()
	isRegistered = MONGO.M.StringField()
	isInRequiredProvGroup = MONGO.M.StringField()
	provGroup = MONGO.M.StringField()
	isInRequiredPortGroup = MONGO.M.StringField()
	oidRevisionNumber = MONGO.M.StringField()
	mac = MONGO.M.StringField()
	node = MONGO.M.StringField()
	PACKAGE = MONGO.M.StringField()
	reason = MONGO.M.StringField()
	relayagentcircuitid = MONGO.M.StringField()
	relayagentremoteid = MONGO.M.StringField()
	relayagentinfo = MONGO.M.StringField()
	selected = MONGO.M.StringField()
	subscriberId = MONGO.M.StringField()
	vivendoropts = MONGO.M.StringField()
	vendorencapsulatedoptions = MONGO.M.StringField()
	timestamp = MONGO.M.StringField()
	dhcpv4 = MONGO.M.StringField()
	pass

class velTopologyReservation(MONGO.M.EmbeddedDocument):
	topologyId = MONGO.M.StringField()
	topologyName = MONGO.M.StringField()
	descriptionTopology = MONGO.M.StringField()
	creatorId = MONGO.M.StringField(); # top built by
	name = MONGO.M.StringField()
	reservationId = MONGO.M.StringField()
	ownerId = MONGO.M.StringField(); # reserved by
	start = MONGO.M.StringField()
	end = MONGO.M.StringField()	
	pass

class velPort(MONGO.M.EmbeddedDocument):
	name = MONGO.M.StringField()
	pgName = MONGO.M.StringField(); # name
	pgId = MONGO.M.StringField()
	uuid = MONGO.M.StringField()
	templateName = MONGO.M.StringField()
	description = MONGO.M.StringField()
	isLocked = MONGO.M.StringField()
	# isOnline = MONGO.M.StringField()
	connections = MONGO.M.StringField(); # uuid? V is p2p so String
	activeRes = MONGO.M.ListField(MONGO.M.EmbeddedDocumentField(velTopologyReservation, dbref=True))
	pass

class velDevice(MONGO.M.EmbeddedDocument):
	name = MONGO.M.StringField()
	uuid = MONGO.M.StringField()
	templateName = MONGO.M.StringField()
	ipAddress = MONGO.M.StringField()
	Hostname = MONGO.M.StringField(); # V uses for DNS instead of IP
	Make = MONGO.M.StringField()
	Model = MONGO.M.StringField(); # used for V.abstract
	tags = MONGO.M.ListField(); # list
	isOnline = MONGO.M.BooleanField(); # ping/status
	isLocked = MONGO.M.BooleanField()
	driver = MONGO.M.StringField(); # pull from template
	connections = MONGO.M.StringField(); # uuid? V is p2p so String
	activeRes = MONGO.M.ListField(MONGO.M.EmbeddedDocumentField(velTopologyReservation, dbref=True))
	pass

# ansible host/group vars?

class RFPort(MONGO.M.EmbeddedDocument):
	name = MONGO.M.StringField()
	node = MONGO.M.StringField()
	direction = MONGO.M.StringField()
	cable_mac = MONGO.M.StringField()
	docsis_mode = MONGO.M.StringField()
	supervision = MONGO.M.StringField()
	channel_width = MONGO.M.StringField()
	modulation_profile = MONGO.M.StringField()
	modulation = MONGO.M.StringField()
	ingress_cancellation = MONGO.M.StringField()
	interleave_depth = MONGO.M.StringField()
	ds_profile = MONGO.M.DictField()
	bonding_group = MONGO.M.DictField()
	_templateName = MONGO.M.StringField()
	description = MONGO.M.StringField()
	pass

class ModemPort(MONGO.M.EmbeddedDocument):
	_connections = MONGO.M.StringField(); # connections/modems not in V 
	ifSpeed = MONGO.M.StringField()
	ifLastChange = MONGO.M.StringField()
	ifInUnknownProtos = MONGO.M.StringField()
	ifOutOctets = MONGO.M.StringField()
	ifOutErrors = MONGO.M.StringField()
	ifPhysAddress = MONGO.M.StringField()
	ifInOctets = MONGO.M.StringField()
	ifOperStatus = MONGO.M.StringField()
	ifMtu = MONGO.M.StringField()
	ifDescr = MONGO.M.StringField()
	ifInDiscards = MONGO.M.StringField()
	ifType = MONGO.M.StringField()
	name = MONGO.M.StringField()
	ipNetToMediaPhysAddress = MONGO.M.StringField()
	ifInErrors = MONGO.M.StringField()
	ifAdminStatus = MONGO.M.StringField()
	ifInUcastPkts = MONGO.M.StringField()
	ifOutDiscards = MONGO.M.StringField()
	ifOutUcastPkts = MONGO.M.StringField()
	ifIndex = MONGO.M.StringField()
	ifPromiscuousMode = MONGO.M.StringField()
	ifConnectorPresent = MONGO.M.StringField()
	portGroup = MONGO.M.StringField()
	ifOutNUcastPkts = MONGO.M.StringField()
	ifInNUcastPkts = MONGO.M.StringField()
	ifSpecific = MONGO.M.StringField()
	ifOutQLen = MONGO.M.StringField()
	pass

class Port(MONGO.M.EmbeddedDocument):
	name = MONGO.M.StringField()
	description = MONGO.M.StringField()
	status = MONGO.M.StringField()	
	vlans = MONGO.M.ListField()
	unit = MONGO.M.ListField()
	duplex = MONGO.M.StringField()
	speed = MONGO.M.StringField()
	ipv4 = MONGO.M.StringField()
	ipv6 = MONGO.M.StringField()	
	familys = MONGO.M.ListField()
	MAC = MONGO.M.StringField()
	PortType = MONGO.M.StringField()
	mtu = MONGO.M.StringField()
	qos = MONGO.M.StringField()
	velocityARC = MONGO.M.EmbeddedDocumentField(velPort, dbref=True)
	_uplinkPort = MONGO.M.StringField()
	ifIndex = MONGO.M.FloatField()
	_templateName = MONGO.M.StringField()
	ifPromiscuousMode = MONGO.M.StringField()
	ifConnectorPresent = MONGO.M.StringField()
	arp = MONGO.M.StringField()
	pass

class e6k_traffic(MONGO.M.EmbeddedDocument):
	ud = MONGO.M.StringField()
	max_burst = MONGO.M.StringField()
	max_sustained_rate = MONGO.M.StringField()
	min_reserved_rate = MONGO.M.StringField()
	sched = MONGO.M.StringField()
	sfid = MONGO.M.StringField()
	sid = MONGO.M.StringField()
	state = MONGO.M.StringField()
	throughput_bps = MONGO.M.StringField()
	tp = MONGO.M.StringField()
	Tmax = MONGO.M.StringField()
	Tmin = MONGO.M.StringField()
	capability = MONGO.M.StringField()
	pass

class Modem(MONGO.M.Document):
	name = MONGO.M.StringField(); # ansible inventory name
	device_name = MONGO.M.StringField(); # name on device
	Make = MONGO.M.StringField()
	Model = MONGO.M.StringField()
	ipAddress = MONGO.M.StringField()
	sn = MONGO.M.StringField()
	protocols = MONGO.M.ListField()
	SAID = MONGO.M.StringField()
	State = MONGO.M.StringField()
	_cmts = MONGO.M.StringField()
	_cmts_port_ds = MONGO.M.StringField()
	_cmts_port_us = MONGO.M.StringField()
	Bootr = MONGO.M.StringField()
	sw_rev = MONGO.M.StringField()
	ofdm = MONGO.M.StringField()
	DOCSIS = MONGO.M.StringField()
	description = MONGO.M.StringField()
	rx_power = MONGO.M.StringField()
	tx_power = MONGO.M.StringField()
	_sg = MONGO.M.StringField()
	type = MONGO.M.StringField()
	hw_rev = MONGO.M.StringField()
	cfg = MONGO.M.StringField()
	# traffic = MONGO.M.DictField(MONGO.M.DictField())
	traffic = MONGO.M.ListField(MONGO.M.EmbeddedDocumentField(e6k_traffic, dbref=True))
	rdu_bac = MONGO.M.EmbeddedDocumentField(rduModemEmbed, dbref=True)
	isReserved = MONGO.M.StringField()
	# ansible_net_system = MONGO.M.ListField()
	# ansible_inventories = MONGO.M.DictField()
	# ansible_host_vars = MONGO.M.DictField()
	# ansible_ready = MONGO.M.DictField()
	# ansible host/group vars?
	ports = MONGO.M.ListField(MONGO.M.EmbeddedDocumentField(ModemPort, dbref=True))
	# modems not in V;  # velocityARC = MONGO.M.EmbeddedDocumentField(velDevice, dbref=True)
	IPAM = MONGO.M.DictField(); # {'10.88.48.0/23':fxp0}
	# NCS = MONGO.M.EmbeddedDocumentField(mNCS, dbref=True); # rack-loc?
	timestamp = MONGO.M.StringField()
	_templateName = MONGO.M.StringField()
	ERTR = MONGO.M.DictField()
	MTA = MONGO.M.DictField()
	node = MONGO.M.StringField()
	lb = MONGO.M.DictField()
	pass


class SG(MONGO.M.Document):
	name = MONGO.M.StringField()
	ports = MONGO.M.ListField(MONGO.M.EmbeddedDocumentField(velPort, dbref=True))
	modems = MONGO.M.ListField(MONGO.M.DictField())
	timestamp = MONGO.M.StringField()
	cmts = MONGO.M.StringField()
	velocityARC = MONGO.M.EmbeddedDocumentField(velDevice, dbref=True)
	_templateName = MONGO.M.StringField()
	pass

class Router(MONGO.M.Document):
	name = MONGO.M.StringField(); # ansible inventory name
	device_name = MONGO.M.StringField(); # name on device
	vendor = MONGO.M.StringField()
	model = MONGO.M.StringField()
	ipAddress = MONGO.M.StringField()
	sn = MONGO.M.StringField()
	protocols = MONGO.M.ListField()
	ansible_net_system = MONGO.M.ListField()
	ansible_inventories = MONGO.M.DictField()
	ansible_host_vars = MONGO.M.DictField()
	ansible_ready = MONGO.M.DictField()
	# ansible host/group vars?
	ports = MONGO.M.ListField(MONGO.M.EmbeddedDocumentField(Port, dbref=True))
	velocityARC = MONGO.M.EmbeddedDocumentField(velDevice, dbref=True)
	IPAM = MONGO.M.DictField(); # {'10.88.48.0/23':fxp0}
	# NCS = MONGO.M.EmbeddedDocumentField(mNCS, dbref=True); # rack-loc?
	timestamp = MONGO.M.StringField()
	_templateName = MONGO.M.StringField()
	pass

class Server(MONGO.M.Document):
	name = MONGO.M.StringField(); # ansible inventory name
	device_name = MONGO.M.StringField(); # name on device
	vendor = MONGO.M.StringField()
	model = MONGO.M.StringField()
	ipAddress = MONGO.M.StringField()
	sn = MONGO.M.StringField()
	protocols = MONGO.M.ListField()
	ansible_net_system = MONGO.M.ListField()
	ansible_inventories = MONGO.M.DictField()
	ansible_host_vars = MONGO.M.DictField()
	ansible_ready = MONGO.M.DictField()
	# ansible host/group vars?
	ports = MONGO.M.ListField(MONGO.M.EmbeddedDocumentField(Port, dbref=True))
	velocityARC = MONGO.M.EmbeddedDocumentField(velDevice, dbref=True)
	IPAM = MONGO.M.DictField(); # {'10.88.48.0/23':fxp0}
	# NCS = MONGO.M.EmbeddedDocumentField(mNCS, dbref=True); # rack-loc?
	timestamp = MONGO.M.StringField()
	_templateName = MONGO.M.StringField()
	pass

class CMTS(MONGO.M.Document):
	name = MONGO.M.StringField(); # ansible inventory name
	device_name = MONGO.M.StringField(); # name on device
	vendor = MONGO.M.StringField()
	model = MONGO.M.StringField()
	ipAddress = MONGO.M.StringField()
	sn = MONGO.M.StringField()
	protocols = MONGO.M.ListField()
	ansible_net_system = MONGO.M.ListField()
	ansible_inventories = MONGO.M.DictField()
	ansible_host_vars = MONGO.M.DictField()
	ansible_ready = MONGO.M.DictField()
	# ansible host/group vars?
	ports = MONGO.M.ListField(MONGO.M.EmbeddedDocumentField(Port, dbref=True))
	portsRF = MONGO.M.ListField(MONGO.M.EmbeddedDocumentField(RFPort, dbref=True))
	velocityARC = MONGO.M.EmbeddedDocumentField(velDevice, dbref=True)
	IPAM = MONGO.M.DictField(); # {'10.88.48.0/23':fxp0}
	# NCS = MONGO.M.EmbeddedDocumentField(mNCS, dbref=True); # rack-loc?
	timestamp = MONGO.M.StringField()
	_templateName = MONGO.M.StringField()
	pass

# MONGO._DELETE(Router, criteria={}, force=True)
# MONGO._DELETE(CMTS, criteria={}, force=True)
# MONGO._DELETE(Server, criteria={}, force=True)
# MONGO._DELETE(SG, criteria={}, force=True)

def TryDeleteDocuments(obj):
	try:
		MONGO._DELETE(obj, criteria={}, force=True)
	except Exception:
		pass
# MONGO.LoadModem(json.loads(wc.read_file(os.environ['rdu_json'])))

