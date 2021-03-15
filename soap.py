#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
import re
import jinja2

def runner(PATH, method, PWS_URL, args={}):
	# does file exist?
	if args != {}:
		# args is index/value search_repalce
		handler = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath=PATH))
		original = [method, '.xml']
		if 'next' in args.keys(): original.insert(1, 'Next')
		handlerFile = handler.get_template(''.join(original))
		updatedTemplate = handlerFile.render(args)
		fname = [PATH, method, '.rendered.xml']
		if 'next' in args.keys(): fname.insert(2, 'Next')
		fname = ''.join(fname)
		wc.rmf(PATH + method + '.rendered.xml')
		# wc.jd(wc.xml_loads2(handlerFile.render(args)))
		wc.post_fname(handlerFile.render(args), fname)

	command = 'curl --header "Content-Type: text/xml;charset=UTF-8" --header "SOAPAction: %s" --data @%s %s' % (method, fname, PWS_URL)
	session_xml = wc.exec2(command).split('\r\n')
	wc.rmf(fname)
	if len(session_xml) == 1: awk = 0
	else: awk = -2
	session_xml = session_xml[awk]
	return(wc.xml_loads2(session_xml))

class BACSOAP():
	def __init__(self, PWS, RDU, username, password, PATH):
		self.PWS = PWS
		self.RDU = RDU
		self.username = username
		self.password = password
		self.PATH = PATH
		raw = runner(self.PATH, 'createSession', 'http://%s:9100/cp-ws-prov/provService' % self.PWS, args={'username':self.username, 'password':self.password, 'rduHost':self.RDU, 'rduPort':'49187'})
		self.sessionId = raw['soap:Envelope']['soap:Body']['ns2:createSessionResponse']['ns2:context']['cptype:sessionId']
		wc.pairprint('sessionId',self.sessionId)
		self.__name__ = 'BACSOAP'
	def delDevice(self, cmac):
		data = runner(self.PATH, 'delDevice', 'http://%s:9100/cp-ws-prov/provService' % self.PWS, args={'sessionId':self.sessionId, 'cmac':cmac})
		wc.pairprint(cmac, data)
	def DeviceSearchByDeviceIdPatternType(self, macAddressPattern='*'):
		fname = '.'.join(['/opt/RDU', self.RDU, 'json'])
		data = runner(self.PATH, 'DeviceSearchByDeviceIdPatternType', 'http://%s:9100/cp-ws-prov/provService' % self.PWS, args={'sessionId':self.sessionId, 'macAddressPattern':macAddressPattern})
		result = {}
		if 'ns2:searchResponse' not in data['soap:Envelope']['soap:Body'].keys():
			wc.jd(data['soap:Envelope']['soap:Body'])
		for modem in data['soap:Envelope']['soap:Body']['ns2:searchResponse']['ns2:results']['cptype:item']:
			result[modem['cptype:deviceIds']['cptype:macAddress']] = modem
		while 'cptype:next' in data['soap:Envelope']['soap:Body']['ns2:searchResponse']['ns2:results'].keys():
			start = data['soap:Envelope']['soap:Body']['ns2:searchResponse']['ns2:results']['cptype:next']['cptype:start']
			data = runner(self.PATH, 'DeviceSearchByDeviceIdPatternType', 'http://%s:9100/cp-ws-prov/provService' % self.PWS, args={'sessionId':self.sessionId, 'macAddressPattern':macAddressPattern, 'next':start})
			if 'cptype:item' not in data['soap:Envelope']['soap:Body']['ns2:searchResponse']['ns2:results'].keys():
				wc.jd(data['soap:Envelope']['soap:Body']['ns2:searchResponse']['ns2:results'])
				break
			for modem in data['soap:Envelope']['soap:Body']['ns2:searchResponse']['ns2:results']['cptype:item']:
				result[modem['cptype:deviceIds']['cptype:macAddress']] = modem
			wc.pairprint('\n\n\n\nMODEMCOUNT\t' + start, len(result.keys()))
		wc.rmf(fname)
		wc.post_fname(json.dumps(result), fname)
		wc.pairprint('export took', wc.fullRuntime())
		return(result)
	def closeSession(self):
            wc.jd(self.PATH, runner('closeSession', 'http://%s:9100/cp-ws-prov/provService' % self.PWS, args={'sessionId':self.sessionId, 'username':self.username, 'password':self.password, 'rduHost':self.RDU, 'rduPort':'49187'}))

# BAC = BACSOAP(PWS=wc.argv_dict['PWS'], RDU=wc.argv_dict['RDU'], username=wc.argv_dict['username'], password=wc.argv_dict['password'])
# if 'mac' in wc.argv_dict.keys():
#     BAC.DeviceSearchByDeviceIdPatternType(macAddressPattern=wc.argv_dict['mac']); # 1,6,00:00:ca:de:7f:f4
# else:
#     BAC.DeviceSearchByDeviceIdPatternType()
# BAC.closeSession()

