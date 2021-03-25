#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
import re
import skinny
import cablemedic
import velocity

V = velocity.VELOCITY(wc.argv_dict['IP'], wc.argv_dict['user'], wc.argv_dict['pass'])
inv = V.GetInventory()
for d in inv.keys():
	if inv[d]['templateName'] == 'Modem':
		if inv[d]['explanation']['value'] == 'Because the device is not registered':
			print('   '.join([d,inv[d]['explanation']['value'],inv[d]['Model']['value'],inv[d]['ipAddress']['value'], inv[d]['CMTS_hostname']['value']]))
