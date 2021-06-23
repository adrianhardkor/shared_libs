#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
import re
import lepton

LEP = lepton.LEPTON(wc.argv_dict['IP'], wc.argv_dict['user'], wc.argv_dict['pass'])
status = LEP.GetStatus()

def GetLports(status, speed):
	results = {}
	for p in status['ports'].keys():
			if speed not in status['ports'][p]['Speed']: continue; # match speed
			if 'NUL' in status['ports'][p]['PhyLink']: continue; # cabled interfaces only
			results[p] = {'Speed':wc.lunique(status['ports'][p]['Speed']), 'PhyLink': status['ports'][p]['PhyLink']}
	return(results)
# wc.jd(status['ports']['1.64'])

special = wc.read_yaml('./special.yml')
# for lcType in special.keys():

wc.jd(LEP.MapPorts('unmap', '1.61', '1.64'))
wc.jd(LEP.MapPorts('map', '1.62', '1.64')); exit(0)

for speed in [10.3125]:
	lports = GetLports(status,speed)
	for lport in lports.keys():
		portTimer = wc.timer_index_start()
		print(lport, special[speed]['woPort'])
		mapping = LEP.MapPorts('map', lport, special[speed]['woPort'])['response.body']
		if 'Error' in mapping.keys(): wc.pairprint(lport, mapping); continue;
		# status = LEP.GetStatus()
		# wc.pairprint('MAPPED', {lport: status['ports'][lport]['MAP']})
		wc.pairprint('MAPPED', mapping)
		PTX = json.loads(wc.REST_GET('http://10.88.48.21:5000/aie?settings=juniper_junos&hostname=%s&cmd1=show_lldp_neighbor_|_match_%s' % (special[speed]['device'],special[speed]['port'])))
		if '1show lldp neighbor | match et-6/0/23' in PTX.keys(): wc.jd(PTX['1show lldp neighbor | match et-6/0/23'])
		else: wc.jd(PTX)
		wc.pairprint('UNMAPPED', LEP.MapPorts('unmap', lport, special[speed]['woPort']))
		print('leptonPort ' + lport + ' took ' + str(wc.timer_index_since(portTimer)) + '\n\n')
# wc.jd(GetLports(status,10.3125))
# wc.jd(special)

