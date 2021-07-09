#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
import re
import jinja2

# PATH is for soapTemplates
# PATH2 is for json export

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
	def __init__(self, PWS, RDU, username, password, PATH, PATH2):
		self.PWS = PWS
		self.RDU = RDU
		self.username = username
		self.password = password
		self.PATH = PATH
		self.PATH2 = PATH2
		raw = runner(self.PATH, 'createSession', 'http://%s:9100/cp-ws-prov/provService' % self.PWS, args={'username':self.username, 'password':self.password, 'rduHost':self.RDU, 'rduPort':'49187'})
		self.sessionId = raw['soap:Envelope']['soap:Body']['ns2:createSessionResponse']['ns2:context']['cptype:sessionId']
		wc.pairprint('sessionId',self.sessionId)
		self.__name__ = 'BACSOAP'
	def delDevice(self, cmac):
		data = runner(self.PATH, 'delDevice', 'http://%s:9100/cp-ws-prov/provService' % self.PWS, args={'sessionId':self.sessionId, 'cmac':cmac})
		# wc.jd(data)
		return(data)
	def DeviceSearchByDeviceIdPatternType(self, macAddressPattern='*'):
		fname = '.'.join([self.PATH2 + '/RDU', self.RDU, 'json'])
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
		wc.pairprint('DEL: ' + fname, str(wc.rmf(fname)))
		wc.post_fname(json.dumps(result), fname)
		wc.pairprint(fname, wc.exec2(' ls -l ' + fname))
		wc.pairprint('export took', wc.fullRuntime())
		return(result)
	def closeSession(self):
	    wc.jd(self.PATH, runner('closeSession', 'http://%s:9100/cp-ws-prov/provService' % self.PWS, args={'sessionId':self.sessionId, 'username':self.username, 'password':self.password, 'rduHost':self.RDU, 'rduPort':'49187'}))

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
	if 'cptype:dhcpCriteria' in bac.keys(): result['dhcpCriteria'] = bac['cptype:dhcpCriteria']
	else: result['dhcpCriteria'] = ''
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
	# cleanup
	bad = ['(',')',' ','{']
	for kk in list(result.keys()):
		if kk in bad: del result[kk]
		elif wc.is_int(kk): del result[kk]
		elif '/' in kk: del result[kk]
		else: result[kk.replace('-','')] = result.pop(kk)
		if kk in result.keys():
			result[kk.strip('/')] = result.pop(kk)
	if 'detected' in result.keys():
		result['detected'] = result['detected']['@xsi:nil']
#	if 'mac' in result.keys():
#		if 'cmac' in result.keys():
#			if result['cmac'] == '': result['cmac'] = result.pop('mac')
#		else: result['cmac'] = result.pop('mac')
	return(json.loads(json.dumps(result, sort_keys=True)))




#BAC = BACSOAP(PWS=wc.argv_dict['PWS'], RDU=wc.argv_dict['RDU'], username=wc.argv_dict['username'], password=wc.argv_dict['password'])
#if 'mac' in wc.argv_dict.keys():
#    BAC.DeviceSearchByDeviceIdPatternType(macAddressPattern=wc.argv_dict['mac']); # 1,6,00:00:ca:de:7f:f4
#else:
#    BAC.DeviceSearchByDeviceIdPatternType()
#BAC.closeSession()

