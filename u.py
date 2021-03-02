#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
import re

# import velocity
# V = velocity.VELOCITY('10.88.48.31', 'akrygows', wc.argv_dict['p'])
# INV = V.GetInventory(); # device ipAddress
# wc.jd(INV)

# /velocity/api/inventory/v13/template/{templateId}/sessions/{sessionId}?merge= <NO/INVENTORY/FULL>
# /ito/executions/v1/agents


data = json.loads(wc.read_file('/Users/adrian/Desktop/comm.json'))
for d in data.keys():
	if type(data[d]) != dict: continue
	for dd in data[d].keys():
		wc.pairprint(d,dd)
