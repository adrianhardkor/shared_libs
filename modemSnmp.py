#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
import re

class MODEMSNMP():
	def __init__(self, community):
		self.community = community
		self.__name__ = 'MODEMSNMP'
	def ValidateModemIP(self, ip, cmac):
		cmac = cmac.replace(':','').upper().strip()
		allmacs = {}
		for intf in self.Modem['intfs'].keys():
			allmacs[self.Modem['intfs'][intf]['ifPhysAddress']] = self.Modem['intfs'][intf]['ifDescr']
		wc.pairprint('CMAC Found', allmacs[cmac])
		return(allmacs[cmac])
	def GetModemPorts(self, ip):
		result = {'intfs':{}, 'chassis':{}}
		for mib in ['ifDescr', 'ifPromiscuousMode', 'ifConnectorPresent', 'ifType', 'ifMtu', 'ifSpeed', 'ifAdminStatus', 'ifOperStatus', 'ifPhysAddress']:
			data = wc.exec2('snmpwalk -v2c -c %s -m all %s %s' % (self.community, ip, mib))
			# wc.pairprint('snmpwalk -v2c -c %s -m all %s %s' % (self.community, ip, mib), data)
			for d in data.split('\n'):
				d = wc.mcsplit(d, ':=')
				try:
					ifIndex = d[2].strip().split('.')[-1]
				except IndexError:
					wc.pairprint('IndexError', d)
					raise
				Value = d[-1]
				if mib == 'ifConnectorPresent' and Value == '0': Value = 'false(2)'
				if mib == 'ifConnectorPresent' and Value == '1': Value = 'true(1)'
				if mib == 'ifDescr': Value = ':'.join(d[4::])
				if ifIndex not in result['intfs'].keys(): result['intfs'][ifIndex] = {}
				if mib == 'ifPhysAddress':
					new = []
					for element in d[-6::]:
						element = element.strip()
						if len(element) == 1: new.append('0' + element)
						else: new.append(element)
					result['intfs'][ifIndex][mib] = ''.join(new).upper()
				else: result['intfs'][ifIndex][mib] = Value.strip()
		data = wc.exec2('snmpwalk -v2c -c %s -m all %s %s' % (self.community, ip, 'ipNetToMediaPhysAddress'))
		for d in data.split('\n'):
			d = d.split('=')
			value =  wc.cleanLine(d[-1])
			d = d[0].split('.')
			snmpjunk = d.pop(0)
			intf = d.pop(0)
			if 'ipNetToMediaPhysAddress' not in result['intfs'][intf].keys():
				result['intfs'][intf]['ipNetToMediaPhysAddress'] = {}
			value.pop(0)
			result['intfs'][intf]['ipNetToMediaPhysAddress'][' '.join(value)] = '.'.join(d).strip()
		data = wc.exec2('snmpwalk -v2c -c %s -m all %s %s' % (self.community, ip, 'SNMPv2-SMI::mib-2.69.1'))
		result['chassis']['serialNumber'] = wc.grep('69.1.1.4.0', data).split(':')[-1]
		result['chassis']['softwareFile'] = wc.grep('69.1.3.2.0', data).split(':')[-1]
		self.Modem = result
		# wc.jd(result)
		return(result)

# M = MODEMSNMP(wc.argv_dict['comm'])
# wc.jd(M.GetModemPorts(wc.argv_dict['ip']))
# M.ValidateModemIP(wc.argv_dict['ip'], wc.argv_dict['cmac'])





# print(json.dumps(Ports, indent=4))

# serial number = SNMPv2-SMI::mib-2.69.1.1.4.0 = STRING
# softwareFile = SNMPv2-SMI::mib-2.69.1.3.2.0 = STRING: 
# sysLocation
# ipAdEntNetMask
# ipNetToPhysicalRowStatus
# hrSystemDate

