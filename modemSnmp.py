#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
import re


from easysnmp import Session

class MODEMSNMP():
	def __init__(self, community):
		self.community = community
		self.__name__ = 'MODEMSNMP'
	def ValidateModemIP(self, ip, cmac):
		cmac = cmac.replace(':','').upper().strip()
		allmacs = {}
		for intf in self.Modem['intfs'].keys():
			if 'ifPhysAddress' not in self.Modem['intfs'][intf].keys(): continue
			if self.Modem['intfs'][intf]['ifPhysAddress'].replace(':','').upper() == cmac and \
			self.Modem['intfs'][intf]['ipNetToMediaPhysAddress'] != '':
				self.Modem['intfs'][intf]['portGroup'] = 'cmac'
			elif 'erouter' in self.Modem['intfs'][intf]['ifDescr'].lower() and \
			self.Modem['intfs'][intf]['ipNetToMediaPhysAddress'] != '':
				self.Modem['intfs'][intf]['portGroup'] = 'ertr'
			elif self.Modem['intfs'][intf]['ifType'].startswith('ipForward'):
				self.Modem['intfs'][intf]['portGroup'] = 'logical'
			elif self.Modem['intfs'][intf]['ifType'].startswith('ethernetCsmacd'):
				self.Modem['intfs'][intf]['portGroup'] = 'ethernet'
			elif self.Modem['intfs'][intf]['ifType'].startswith('ieee80211') and 'sub' in self.Modem['intfs'][intf]['ifDescr']:
				self.Modem['intfs'][intf]['portGroup'] = 'logical'
			elif 'packetcable' in self.Modem['intfs'][intf]['ifDescr'].lower():
				self.Modem['intfs'][intf]['portGroup'] = 'PacketCable'
			else: self.Modem['intfs'][intf]['portGroup'] = self.Modem['intfs'][intf]['ifType']
	def FormatSNMPline(self, line):
		line = line.split('=')
		line[0] = wc.mcsplit(line[0].strip(), ['.',':'])
		if len(line) < 2: wc.pairprint('broken?', line)
		line[1] = line[1].strip().split(':')
		line[1].pop(0)
		line[1] = str(':'.join(line[1]))
		if line[0][2] == 'ipNetToMediaPhysAddress':
			line[1] = ':'.join(wc.cleanLine(line[1]))
			line[1] = line[1] + ' ' + '.'.join(line[0][4::])
		elif line[0][2] == 'ifPhysAddress':
			value = []
			for v in str(line[1]).split(':'):
				for vv in v:
					if wc.str_int_split(vv) == (' ',''): value.append('0')
					else: value.append(vv)
			line[1] = ''.join(value).upper()
		return(line[0][2].strip(),line[0][3].strip(),line[1].strip())
	def isAscii(self, value):
		ascii2 = True
		for v in str(value):
			if 0 <= ord(v) <= 127: pass
			else: ascii2 = False
		return(ascii2)
	def GetModemPorts(self, ip):
		timer = wc.timer_index_start()
		result = {'intfs':{}, 'chassis':{}}
		if wc.is_pingable(ip) is False:
			wc.pairprint(ip, 'is not pingable cant use snmp')
			self.Modem = result
			return({})
		session = Session(hostname=ip, community=self.community, version=2)
		MIBS = ['ifDescr', 'ifPhysAddress', 'ifTable', 'ifConnectorPresent', 'ifPromiscuousMode', 'ipNetToMediaPhysAddress']
		for MIB in MIBS:
			data = session.walk(MIB)
			for d in data:
				if self.isAscii(d.value):  value = d.value
				else: value = ':'.join('{:02x}'.format(ord(x)) for x in d.value)
				if MIB == 'ipNetToMediaPhysAddress':
					d.oid_index = str(d.oid_index).split('.')
					ifIndex = str(d.oid_index.pop(0))
					index = MIB
					value = value + ' ' + '.'.join(d.oid_index)

				else:
					ifIndex = str(d.oid_index)
					index = str(d.oid)
				if ifIndex not in result['intfs'].keys(): result['intfs'][ifIndex] = {'portGroup':'', 'ipNetToMediaPhysAddress':'', 'ifDescr':'','ifType':''}
				result['intfs'][ifIndex][index] = value
		self.Modem = result
		wc.pairprint('[INFO] GetModemPorts.class.py took', wc.timer_index_since(timer))
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

