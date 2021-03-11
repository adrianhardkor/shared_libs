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
	def GetModemPorts(self, ip):
		result = {}
		for mib in ['ifDescr', 'ifSpeed', 'ifAdminStatus', 'ifOperStatus', 'ifPhysAddress']:
			data = wc.exec2('snmpwalk -v2c -c %s -m all %s %s' % (self.community, ip, mib))
			for d in data.split('\n'):
				d = wc.mcsplit(d, ':=')
				ifIndex = d[2].strip().split('.')[-1]
				Value = d[-1]
				if ifIndex not in result.keys(): result[ifIndex] = {}
				if mib == 'ifPhysAddress': result[ifIndex][mib] = ''.join(d[-6::]).upper().strip()
				else: result[ifIndex][mib] = d[-1]
		data = wc.exec2('snmpwalk -v2c -c %s -m all %s %s' % (self.community, ip, 'ipNetToMediaPhysAddress'))
		for d in data.split('\n'):
			d = d.split('=')
			value =  wc.cleanLine(d[-1])[-1]
			d = d[0].split('.')
			snmpjunk = d.pop(0)
			intf = d.pop(0)
			if 'ipNetToMediaPhysAddress' not in result[intf].keys():
				result[intf]['ipNetToMediaPhysAddress'] = {}
			result[intf]['ipNetToMediaPhysAddress'][value] = '.'.join(d).strip()
		return(result)

M = MODEMSNMP(wc.argv_dict['comm'])
Ports = M.GetModemPorts(wc.argv_dict['ip'])
print(json.dumps(Ports, indent=4))

