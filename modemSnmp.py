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
		if allmacs == {}: return({})
		found = ''
		try:
			found = allmacs[cmac]
		except IndexError:
			wc.jd(allmacs)
			wc.pairprint('CMAC Not Found', cmac)
		except KeyError:
			wc.jd(allmacs)
			wc.pairprint('CMAC Not Found', cmac)
		return(found)
	def FormatSNMPline(self, line):
		line = line.split('=')
		line[0] = wc.mcsplit(line[0].strip(), ['.',':'])
		line[1] = line[1].strip().split(':')
		line[1].pop(0)
		line[1] = ':'.join(line[1])
		if line[0][2] == 'ipNetToMediaPhysAddress':
			line[1] = ':'.join(wc.cleanLine(line[1]))
			line[1] = line[1] + ' ' + '.'.join(line[0][4::])
		return(line[0][2].strip(),line[0][3].strip(),line[1].strip())
	def GetModemPorts(self, ip):
		result = {'intfs':{}, 'chassis':{}}
		data = []
		MIBS = ['1.3.6.1.2.1.2.2.1', 'ifConnectorPresent', 'ifPromiscuousMode', 'ipNetToMediaPhysAddress']
		for MIB in MIBS:
			data.append(wc.exec2('snmpbulkwalk -r 2 -t 15 -m all -v2c -c %s %s %s' % (self.community, ip, MIB)))
		data = '\n'.join(data)
		for intf in wc.grep('ifDescr', data).split('\n'):
			mib,ifIndex,value = self.FormatSNMPline(intf)
			result['intfs'][ifIndex] = {}
		for intf in data.split('\n'):
			mib,ifIndex,value = self.FormatSNMPline(intf)
			# print(mib,ifIndex,value)
			# if mib in MIBS: print(mib,ifIndex,value)
			result['intfs'][ifIndex][mib] = value
		self.Modem = result
		return(result)

# M = MODEMSNMP(wc.env_dict['ARC_SNMP_COMM'])
# data = M.GetModemPorts(wc.argv_dict['ip'])
# wc.jd(data)
# M.ValidateModemIP(wc.argv_dict['ip'], wc.argv_dict['cmac'])





# print(json.dumps(Ports, indent=4))

# serial number = SNMPv2-SMI::mib-2.69.1.1.4.0 = STRING
# softwareFile = SNMPv2-SMI::mib-2.69.1.3.2.0 = STRING: 
# sysLocation
# ipAdEntNetMask
# ipNetToPhysicalRowStatus
# hrSystemDate

