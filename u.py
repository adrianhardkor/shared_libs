#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
import re

from pysnmp.hlapi import *
import sys

def GetIfTypes():
	data = json.loads(wc.REST_GET('https://www.iana.org/assignments/ianaiftype-mib/ianaiftype-mib'))['response.body']
	global ifTypes
	ifTypes = {}
	for line in data.split('\n'):
		cline = wc.cleanLine(line)
		if cline == []: continue
		elif '(' in line and ')' in line:
			sLine = wc.mcsplit(line, ['(',')'])
			ifTypes[sLine[1]] = sLine[0].strip()
GetIfTypes()

global translations
translations = {}

def GetMibOID(oid):
	global translations
	if oid in translations.keys(): pass
	else:
		mib = wc.exec2('snmptranslate ' + oid)
		translations[oid] = mib.split(':')[-1]
	return(translations[oid])

def walk(host, mib):
    global ifTypes
    oid = wc.exec2('snmptranslate -On ' + mib)
    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) in nextCmd(SnmpEngine(),
                              CommunityData('W0WForeCM@!'),
                              UdpTransportTarget((host, 161)),
                              ContextData(),
                              ObjectType(ObjectIdentity(oid)),
                              lookupMib=True,
                              lexicographicMode=False):

        if errorIndication:
            print(errorIndication, file=sys.stderr)
            break

        elif errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(),
                                errorIndex and varBinds[int(errorIndex) - 1][0] or '?'), file=sys.stderr)
            break

        else:
#            print(json.dumps(varBinds, indent=2))
            for varBind in varBinds:
                 varBind = wc.cleanLine(str(varBind))
                 out_oid = varBind[0].split('.')
                 value = ' '.join(varBind[2::])
                 if mib == 'IP-MIB::ipNetToMediaPhysAddress':
                     ifIndex = str(out_oid[-5])
                     index = GetMibOID('.'.join(out_oid)).split('.')
                     value = value + ' ' + '.'.join(index[2::])
                     index = index[0]
                 else:
                     ifIndex = out_oid.pop(-1)
                     index = GetMibOID('.'.join(out_oid))
                 if index == 'ifPhysAddress' and value != '':
                     value = value.split('x')[1]
                     value = ':'.join([value[0:2],value[2:4],value[4:6],value[6:8],value[8:10],value[10:12]])
                 elif index == 'ifType': value = ifTypes[value]
                 print('\t'.join([index, ifIndex, value]))

MIBS = ['IF-MIB::ifTable', 'IF-MIB::ifConnectorPresent', 'IF-MIB::ifPromiscuousMode', 'IP-MIB::ipNetToMediaPhysAddress']
# MIBS = ['IF-MIB::ifConnectorPresent', 'IF-MIB::ifPromiscuousMode', 'IP-MIB::ipNetToMediaPhysAddress']
for MIB in MIBS:
	# walk('10.88.26.9', MIB)
	walk('10.88.16.10', MIB)

	pass
wc.pairprint('PySnmp took', wc.fullRuntime())

