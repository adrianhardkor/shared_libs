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
		self.ianaiftype = json.loads(wc.REST_GET('https://www.iana.org/assignments/ianaiftype-mib/ianaiftype-mib'))
		if 'response.body' in self.ianaiftype.keys(): self.ianaiftype = self.ianaiftype['response.body']
		else: wc.jd(self.ianaiftype)
	def ValidateModemIP(self, ip, cmac):
		cmac = cmac.replace(':','').upper().strip()
		allmacs = {}
		for intf in self.Modem['intfs'].keys():
			for default in ['ipNetToMediaPhysAddress']:
				if default not in self.Modem['intfs'][intf].keys(): self.Modem['intfs'][intf][default] = ''
			if 'ifPhysAddress' not in self.Modem['intfs'][intf].keys(): continue
			if self.Modem['intfs'][intf]['ifPhysAddress'] == '': continue
			if self.Modem['intfs'][intf]['ifPhysAddress'].replace(':','').upper() == cmac and \
			self.Modem['intfs'][intf]['ipNetToMediaPhysAddress'] != '':
				self.Modem['intfs'][intf]['portGroup'] = 'cmac'
			elif 'erouter' in self.Modem['intfs'][intf]['ifDescr'].lower() and \
			self.Modem['intfs'][intf]['ipNetToMediaPhysAddress'] != '':
				self.Modem['intfs'][intf]['portGroup'] = 'ertr'
			elif self.Modem['intfs'][intf]['ifType'].startswith('ipForward'):
				self.Modem['intfs'][intf]['portGroup'] = 'logical'
			elif self.Modem['intfs'][intf]['ifType'].startswith('pptp'):
				self.Modem['intfs'][intf]['portGroup'] = 'ethernet'
			elif self.Modem['intfs'][intf]['ifType'].startswith('ieee80211') and 'sub' in self.Modem['intfs'][intf]['ifDescr']:
				self.Modem['intfs'][intf]['portGroup'] = 'logical'
			elif 'packetcable' in self.Modem['intfs'][intf]['ifDescr'].lower():
				self.Modem['intfs'][intf]['portGroup'] = 'PacketCable'
			else: self.Modem['intfs'][intf]['portGroup'] = self.Modem['intfs'][intf]['ifType']
	def GetIfTypes(self):
		for line in self.ianaiftype.split('\n'):
			cline = wc.cleanLine(line)
			if cline == []: continue
			elif '(' in line and ')' in line:
				sLine = wc.mcsplit(line, ['(',')'])
				self.ifTypes[sLine[1]] = sLine[0].strip()
	def GetMibOID(self, oid):
		if oid in self.translations.keys(): pass
		else:
			mib = wc.exec2('snmptranslate ' + oid)
			# wc.pairprint('trans ' + oid, mib)
			self.translations[oid] = mib.split(':')[-1]
		return(self.translations[oid])
	def bulkwalkSystem(self, host, mib):
		data = wc.exec2('snmpbulkwalk -v2c -c ' + wc.env_dict['ARC_SNMP_COMM'] + ' '.join(['',host,mib]))
		for varBind in data.split('\n'):
			# print('\t' + str(varBind))
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
				# index = self.GetMibOID('.'.join(out_oid))
				index = mib.split(':')[-1]
			if index == 'ifPhysAddress' and value != '':
				if 'x' in value:
					value = value.split('x')[1]
					value = ':'.join([value[0:2],value[2:4],value[4:6],value[6:8],value[8:10],value[10:12]])
			elif index == 'ifType' and wc.is_int(value): value = self.ifTypes[value]
			if ifIndex not in self.Modem['intfs'].keys(): self.Modem['intfs'][ifIndex] = {}
			self.Modem['intfs'][ifIndex][index] = value
	def bulkwalk(self, host, mib):
		# wc.pairprint(host,mib)
		# oid = wc.exec2('snmptranslate -On ' + mib)
		for (errorIndication, errorStatus, errorIndex, varBinds) in bulkCmd(SnmpEngine(),
			CommunityData(self.community),
			UdpTransportTarget((host,161)),
			ContextData(),
			0, 2,
			ObjectType(ObjectIdentity(mib.split(':')[0], mib.split(':')[-1]))):
			wc.pairprint(mib.split(':')[0], mib.split(':')[-1])
			for varBind in varBinds:
				print('\t' + str(varBind))
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
					# index = self.GetMibOID('.'.join(out_oid))
					index = mib.split(':')[-1]
				if index == 'ifPhysAddress' and value != '':
					if 'x' in value:
						value = value.split('x')[1]
						value = ':'.join([value[0:2],value[2:4],value[4:6],value[6:8],value[8:10],value[10:12]])
				elif index == 'ifType': value = self.ifTypes[value]
				if ifIndex not in self.Modem['intfs'].keys(): self.Modem['intfs'][ifIndex] = {}
				self.Modem['intfs'][ifIndex][index] = value
	def walk(self, host, mib):
		oid = wc.exec2('snmptranslate -On ' + mib)
		wc.pairprint('trans1 ' + mib, oid)
		for (errorIndication, errorStatus, errorIndex, varBinds) in bulkCmd(SnmpEngine(), 
			CommunityData(self.community), 
			UdpTransportTarget((host, 161)), 
			ContextData(), 
			ObjectType(ObjectIdentity(oid)), 
			lookupMib=True,
			maxRepetitions=3,
			lexicographicMode=False): 
			if errorIndication:
				print(errorIndication, file=sys.stderr)
				break
			elif errorStatus:
				print('%s at %s' % (errorStatus.prettyPrint(), errorIndex and varBinds[int(errorIndex) - 1][0] or '?'), file=sys.stderr)
				break
			else:
				for varBind in varBinds:
					print(varBind)
					varBind = wc.cleanLine(str(varBind))
					out_oid = varBind[0].split('.')
					value = ' '.join(varBind[2::])
					if mib == 'IP-MIB::ipNetToMediaPhysAddress':
						if len(out_oid) <= 5: print(out_oid)
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
					elif index == 'ifType': value = self.ifTypes[value]
					if ifIndex not in self.Modem['intfs'].keys(): self.Modem['intfs'][ifIndex] = {}
					self.Modem['intfs'][ifIndex][index] = value
		return(self.Modem)
	def GetModemPorts(self, ip):
		# wc.pairprint('[INFO] ' + ip, 'start')
		timer = wc.timer_index_start()
		if not wc.is_pingable(ip): wc.pairprint(ip, 'not_pingable'); return(self.Modem)
		self.GetIfTypes()
		MIBS = ['IF-MIB::ifDescr', 'IF-MIB::ifAdminStatus', 'IF-MIB::ifOperStatus', 'IF-MIB::ifMtu', 'IF-MIB::ifType', 'IF-MIB::ifPhysAddress', 'IF-MIB::ifSpeed', 'IF-MIB::ifConnectorPresent', 'IF-MIB::ifPromiscuousMode', 'IP-MIB::ipNetToMediaPhysAddress']
		print('\t' + ip + ':  ', end='')
		for MIB in MIBS:
			timer2 = wc.timer_index_start()
			free = '\t' + str(wc.exec2('free -m').split('\n'))
			self.bulkwalkSystem(ip, MIB)
			free = ''
			print(MIB + '   ', end='', flush=True); # nonewline
			# wc.pairprint(ip, MIB + free)
			# wc.pairprint(MIB, wc.timer_index_since(timer2))
		# wc.pairprint('[INFO] modemSnmp.PySnmp for ' + ip, wc.timer_index_since(timer))
		print('Done!')
		return(self.Modem)

# M = MODEMSNMP(wc.env_dict['ARC_SNMP_COMM'])
# out = M.GetModemPorts('10.88.16.2')
# wc.jd(out)

