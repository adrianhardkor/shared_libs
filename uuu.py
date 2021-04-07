#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
import re
import soap
import deepdiff

for f in wc.exec2('ls ~/Modems').split('\n'):
	if f.endswith('.json') is False: continue
	print(f)
	data = wc.read_file('/home/adrian/Modems/' + f)
	data = json.loads(data)
#	wc.jd(data)

data = wc.read_file('e6k.verbose.log')
def e6kModemVerbose(lines):
	modems = {}
	for line in lines:
		cline = wc.cleanLine(line)
		if len(cline) < 2: continue
		elif cline[1] == 'CM':
			mac = cline[2].replace('.','').upper()
			modems[mac] = {'cmac': mac, 'downstream':{'stats':{}},'upstream':{'stats':{}}}
			modems[mac]['docsis'] = cline[4]
			ports1 = cline[0].split('-')
			modems[mac]['downstream']['port'] = ports1[0]
			modems[mac]['upstream']['port'] = ports1[1]
			modems[mac]['State'] = ' '.join(cline[5:7])
			modems[mac]['PrimSID'] = cline[7]
			modems[mac]['FiberNode'] = ' '.join(cline[9::])
		elif cline[0] == 'Cable-Mac=':
			modems[mac]['id'] = cline[1]
			modems[mac]['mCMsg'] = cline[4]
			modems[mac]['mDSsg'] = cline[6]
			modems[mac]['mUSsg'] = cline[8]
			remainder = wc.pairedList(cline[11:])
			for r in remainder.keys():
				modems[mac][r] = remainder[r]
		elif cline[0] == 'Timing':
			modems[mac]['Timing Offset'] = cline[1]
			modems[mac]['Rec Power'] = cline[4]
			if len(cline) > 6: modems[mac]['Proto-Throttle'] = cline[6]
			if len(cline) > 8: modems[mac][cline[7]] = cline[8]
			if len(cline) > 10: modems[mac][cline[9]] = cline[10]
			# 'dsRegFailedChan', '-', 'usRegFailedChan', '-']
		elif cline[0] == 'MODEM':
			modems[mac]['downstream']['capability'] = ' '.join(cline[1:3])
			modems[mac]['upstream']['capability'] = ' '.join(cline[3::])
		elif cline[0].startswith('OFDM='):
			modems[mac]['OFDM'] = cline[0]
			modems[mac]['OFDM ds-profile'] = ' '.join(cline[1::])
		elif cline[0] == 'Uptime=':
			for k in cline:
				if '=' in k:
					
					index = k.split('=')[0]
					modems[mac][index] = k.split('=')[1]
				else: modems[mac][index] = modems[mac][index] + ' ' + k
		elif cline[0] == 'LB' and cline[2] == 'LB':
			modems[mac]['LB Policy'] = cline[1]
			modems[mac]['LB Group'] = cline[3]
			modems[mac]['Filter-Group'] = cline[5::]
		elif cline[0].startswith('Privacy') or cline[0].startswith('em1x1Enable'):
			index = ''
			for cl in cline:
				if '=' in cl:
					if index != '': modems[mac][index] = value
					cl = cl.split('=')
					index = cl[0]
					value = cl[1]
				else: value = value + ' ' + cl
		elif cline[0] == 'MDF':
			index = ''
			for cl in cline:
				if '=' in cl:
					if index != '': modems[mac][index] = value
					cl = cl.split('=')
					index = 'MDF ' + cl[0]
					value = cl[1]
				else: value = value + ' ' + cl
		elif cline[0] in ['uB','dB','uC','dC', 'd']:
			ud = cline.pop(0)
			sfid = cline.pop(0)
			asfid = cline.pop(0)
			sid = cline.pop(0)
			state = cline.pop(0)
			if ud.startswith('u'): dir2 = 'upstream'
			else: dir2 = 'downstream'
			modems[mac][dir2]['stats'][sfid] = {'ud':ud,'asfid':asfid,'sid':sid,'state':state}
			if not wc.is_int(cline[0]): sched = cline.pop(0)
			else: sched = ''
			modems[mac][dir2]['stats'][sfid]['sched'] = sched
			modems[mac][dir2]['stats'][sfid]['Tmin'] = cline.pop(0)
			modems[mac][dir2]['stats'][sfid]['Tmax'] = cline.pop(0)
			modems[mac][dir2]['stats'][sfid]['Frames'] = cline.pop(0)
			modems[mac][dir2]['stats'][sfid]['Bytes'] = cline.pop(0)
			if wc.is_int(cline[0]):
					modems[mac][dir2]['stats'][sfid]['CRC'] = cline.pop(0)
					modems[mac][dir2]['stats'][sfid]['HCS'] = cline.pop(0)

		elif cline[0] == 'L2VPN':
			modems[mac]['L2VPN per CM'] = ' '.join(cline[3::])
		elif 'CPE' in cline[0]:
			TYPE = cline[0]; cline.pop(0)
			TYPE = wc.cleanLine(TYPE.replace('(',' ').replace(')',' '))
			if len(TYPE) == 2: TYPE = TYPE[1]
			elif len(TYPE) == 1: TYPE = TYPE[0]
			modems[mac][TYPE] = {}
			modems[mac][TYPE]['id'] = cline[0]; cline.pop(0)
			if cline[-2] == 'IP': cline[-1] = cline[-2] + cline[-1]; cline.pop(-2)
			modems[mac][TYPE]['IP'] = cline[-1].split('=')[-1]; cline.pop(-1)
			modems[mac][TYPE][cline[-1].split('=')[0]] = cline[-1].split('=')[-1]; cline.pop(-1)
			modems[mac][TYPE][cline[0].split(':')[0]] = [cline[-1].split(':')[-1]]; cline.pop(0)
			for remainder in cline:
				modems[mac][TYPE]['Filter-Group'].append(remainder)
		else:
			# print(line)
			pass
	return(modems)
out = e6kModemVerbose(data.split('\n'))
wc.jd(out)
