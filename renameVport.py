#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
import re
import soap
import deepdiff

import velocity

V = velocity.VELOCITY(wc.argv_dict['IP'], user=wc.argv_dict['user'], pword=wc.argv_dict['pass'])
V.GetInventory()
for port in V.INV[wc.argv_dict['device']]['ports'].keys():
	if wc.is_int(port[0]):
		sPort = port.split('/')
		try:
			V.UpdatePort(wc.argv_dict['device'], 'S' + port[0], port, 'name', 'S' + sPort[0] + 'P' + sPort[1])
			V.UpdatePort(wc.argv_dict['device'], 'S' + port[0], port, 'portNumber', 'S' + sPort[0] + 'P' + sPort[1])
		except Exception:
			pass
# V.UpdatePort(wc.argv_dict['old'][0], 'S1', wc.argv_dict['old'][1], 'name', wc.argv_dict['new'])
# V.UpdatePort(wc.argv_dict['old'][0], 'S1', wc.argv_dict['old'][1], 'portNumber', wc.argv_dict['new'])
