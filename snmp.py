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
			for d in data.split('\n'):
				print(d)
				d = wc.mcsplit(d, ':=')
				ifIndex = d[2].strip().split('.')[-1]
				Value = d[-1]
				if ifIndex not in result['intfs'].keys(): result['intfs'][ifIndex] = {}
				if mib == 'ifPhysAddress': result['intfs'][ifIndex][mib] = ''.join(d[-6::]).replace(':','').upper().strip()
				else: result['intfs'][ifIndex][mib] = d[-1].strip()
		data = wc.exec2('snmpwalk -v2c -c %s -m all %s %s' % (self.community, ip, 'ipNetToMediaPhysAddress'))
		for d in data.split('\n'):
			d = d.split('=')
			value =  wc.cleanLine(d[-1])[-1]
			d = d[0].split('.')
			snmpjunk = d.pop(0)
			intf = d.pop(0)
			if 'ipNetToMediaPhysAddress' not in result['intfs'][intf].keys():
				result['intfs'][intf]['ipNetToMediaPhysAddress'] = {}
			result['intfs'][intf]['ipNetToMediaPhysAddress'][value.replace(':','').upper()] = '.'.join(d).strip()
		data = wc.exec2('snmpwalk -v2c -c %s -m all %s %s' % (self.community, ip, 'SNMPv2-SMI::mib-2.69.1'))
		result['chassis']['serialNumber'] = wc.grep('69.1.1.4.0', data).split(':')[-1]
		result['chassis']['softwareFile'] = wc.grep('69.1.3.2.0', data).split(':')[-1]
		self.Modem = result
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

