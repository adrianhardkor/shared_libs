#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
import re
import skinny
import cablemedic

S = skinny.SKINNY('skinnyapi.arc.ninjaneers.net')
CM = cablemedic.MEDIC('10.88.48.232', 'cablemedic@wowinc.com', 'CuredBonwiff')

PATH = '/var/lib/jenkins/Modems'
for ip in wc.exec2('ls ' + PATH).split('\n'):
	if ip.startswith('10') is False: continue
	ip1 = '.'.join(ip.split('.')[0:4])
	# wc.pairprint(ip1, sorted(list(S.GetSQC(ip1).keys())))
	cmac = json.loads(wc.read_file(PATH + '/' + ip))
	for index in cmac['intfs'].keys():
		if cmac['intfs'][index]['ifDescr'] == 'RF MAC Interface':
			medic = CM.GetModemDetail(cmac['intfs'][index]['ifPhysAddress'])
			wc.pairprint(ip1, medic['response.status_code'])
