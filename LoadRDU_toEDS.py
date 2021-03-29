#!/usr/bin/env python3
# encoding: utf-8
import flask
from flask_mongoengine import MongoEngine
import json
import wcommon as wc
import time

rdu_json = wc.argv_dict['rdu_json']
flaskIP = wc.argv_dict['flaskIP']

app = flask.Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'db': 'admin',
    'host': 'localhost',
    'port': 27017,
    'connect': True
}
M = MongoEngine(); # starts Mongo
M.init_app(app)

def wonky_bac_pairedlist(myl):
        result = {}
        for i in range(0, len(myl), 2):
                index = str(myl[i]).strip()
                value = str(myl[i + 1])
                result[index] = value
                if index == 'dhcp-parameter-request-list':
                        ii = int(i) + 1
                        for myll in myl[ii::]:
                                if myll.startswith(' '):
                                        break
                                ii = ii + 1
                        result[index] = ' '.join(myl[i:ii])
                        remainder = wonky_bac_pairedlist(myl[ii:])
                        for r in remainder:
                                result[r] = remainder[r]
                        return(result)
        return(result)

def FormatRDU_Modem(cmac, bac):
	result = {}
	if bac == {}: return(result)
	result['deviceType'] = bac['cptype:deviceType']
	if 'cptype:dhcpCriteria' in bac.keys(): result['dhcpCritera'] = bac['cptype:dhcpCriteria']
	else: result['dhcpCritera'] = ''
	if 'cptype:discoveredData' in bac.keys():
		properties = bac['cptype:discoveredData']['cptype:dhcpv4RequestData']['cptype:entry']
	elif 'cptype:properties' in bac.keys():
		properties = bac['cptype:properties']['cptype:entry']
	else: wc.jd(bac)
	for unformat in properties:
		if ',' not in unformat['cptype:value']: result[unformat['cptype:name']] = unformat['cptype:value']
		else:
			for each in unformat['cptype:value'].split(','):
				result[each[0]] = each[-1]
	for unformat2 in bac['cptype:properties']['cptype:entry']:
		if '/' in unformat2['cptype:name']: index = unformat2['cptype:name'].split('/')[-1]
		else: index = unformat2['cptype:name']
		if str(unformat2['cptype:value']) != '[]': result[index] = unformat2['cptype:value']
		if unformat2['cptype:name'] == '/discoveredData/raw/dhcpv4':
			pairedlist = wc.mcsplit(unformat2['cptype:value'], ',=')
			pairedlist.pop(0)
			pairedlist[0] = pairedlist[0].strip('{')
			pairedlist[-1] = pairedlist[0].strip('}')
			mydict = wonky_bac_pairedlist(pairedlist)
			for key in mydict.keys():
				result[key] = mydict[key]
	return(result)


# TEMPLATE CLASSES
class rduModem(M.Document):
	cmac = M.StringField(required=True)
	access = M.StringField()
	chaddr = M.StringField()
	clientId = M.StringField()
	clientIdCreated = M.StringField()
	cos = M.StringField()
	deviceType = M.StringField()
	domain = M.StringField()
	dhcpMessageType = M.StringField()
	dhcpParamRequestList = M.StringField()
	dhcpCriteria = M.StringField()
	DIVISION = M.StringField()
	explanation = M.StringField()
	giaddr = M.StringField()
	hlen = M.StringField()
	htype = M.StringField()
	isBehindRequiredDevice = M.StringField()
	isProvisioned = M.StringField()
	isRegistered = M.StringField()
	isInRequiredPortGroup = M.StringField()
	oidRevNum = M.StringField()
	PACKAGE = M.StringField()
	provGroup = M.StringField()
	reason = M.StringField()
	relayAgentCircuitId = M.StringField()
	relayAgentRemoteId = M.StringField()
	relayAgentInfo = M.StringField()
	subscriberId = M.StringField()
	viVendorOpts = M.StringField()
	vendorEncapsulatedOptions = M.StringField()
	timestamp = M.StringField()
	pass


#rdu = json.loads(wc.read_file(rdu_json))
#for cmac in rdu.keys():
#	RDU = FormatRDU_Modem(cmac, rdu[cmac]) 
#	# if CMAC doesnt exist, create
#	if list(rduModem.objects(cmac=cmac)) == []:
#		cmacM = rduModem(cmac=cmac, deviceType=RDU['deviceType'],timestamp=str(time.time()))
#		cmacM.save()
# 	Food.objects(type="snacks").delete()
Food.objects(type="snacks").delete()

def flask_RDU():
        @app.route('/rdu', methods=['GET'])
        def all():
                return(flask.jsonify(rduModem.objects()))

# FLASK WEB-API
def flask_default():
        @app.route('/', methods=['GET'])
        def home():
                return "<h1>DFEAULT</h1><p>Got default, but is working</p>"

if  __name__ == "__main__":
        flask_default()
        flask_RDU()
        app.run( debug=True, host=flaskIP)

