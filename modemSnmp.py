#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
import re

from pysnmp.hlapi import *
import sys


class MODEMSNMP():
	def __init__(self, community):
		self.community = community
		self.__name__ = 'MODEMSNMP'
		self.translations = {}
		self.ifTypes = {}
		self.Modem = {'intfs':{}, 'chassis':{}}
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
	def GetIfTypes(self):
		data = json.loads(wc.REST_GET('https://www.iana.org/assignments/ianaiftype-mib/ianaiftype-mib'))['response.body']
		for line in data.split('\n'):
			cline = wc.cleanLine(line)
			if cline == []: continue
			elif '(' in line and ')' in line:
				sLine = wc.mcsplit(line, ['(',')'])
				self.ifTypes[sLine[1]] = sLine[0].strip()
	def GetMibOID(self, oid):
		if oid in self.translations.keys(): pass
		else:
			mib = wc.exec2('snmptranslate ' + oid)
			self.translations[oid] = mib.split(':')[-1]
		return(self.translations[oid])
	def walk(self, host, mib):
		oid = wc.exec2('snmptranslate -On ' + mib)
		for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(SnmpEngine(), CommunityData(self.community), UdpTransportTarget((host, 161)), ContextData(), ObjectType(ObjectIdentity(oid)), lookupMib=True, lexicographicMode=False): 
			if errorIndication:
				print(errorIndication, file=sys.stderr)
				break
			elif errorStatus:
				print('%s at %s' % (errorStatus.prettyPrint(), errorIndex and varBinds[int(errorIndex) - 1][0] or '?'), file=sys.stderr)
				break
			else:
				for varBind in varBinds:
					varBind = wc.cleanLine(str(varBind))
					out_oid = varBind[0].split('.')
					value = ' '.join(varBind[2::])
					if mib == 'IP-MIB::ipNetToMediaPhysAddress':
						ifIndex = str(out_oid[-5])
						index = self.GetMibOID('.'.join(out_oid)).split('.')
						value = value + ' ' + '.'.join(index[2::])
						index = index[0]
					else:
						ifIndex = out_oid.pop(-1)
						index = self.GetMibOID('.'.join(out_oid))
					if index == 'ifPhysAddress' and value != '':
						value = value.split('x')[1]
						value = ':'.join([value[0:2],value[2:4],value[4:6],value[6:8],value[8:10],value[10:12]])
					elif index == 'ifType': value = ifTypes[value]
					if ifIndex not in self.Modem['intfs'].keys(): self.Modem['intfs'][ifIndex] = {}
					self.Modem['intfs'][ifIndex][index] = value
			return(self.Modem)
	def GetModemPorts(self, ip):
		MIBS = ['IF-MIB::ifTable', 'IF-MIB::ifConnectorPresent', 'IF-MIB::ifPromiscuousMode', 'IP-MIB::ipNetToMediaPhysAddress']
		for MIB in MIBS:
			self.walk(ip, MIB)
		return(self.Modem)

