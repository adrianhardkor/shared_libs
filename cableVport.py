#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
import re
import soap
import deepdiff
import wgcp
import velocity

global sheet
# GOOGLE PUBLIC CLOUD
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SAMPLE_SPREADSHEET_ID = '1lChMjk1OMyZlEmX8TqUjHOwILoBSnCUpm4evrPvLork'
SAMPLE_RANGE_NAME = 'ARC_AutoCabling'
creds_path = '/opt/google/'
# build class
UNIT_ASSET = wgcp.GCP(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME, SCOPES, creds_path + 'runner.pickle', creds_path + 'credentials.json')
handle = UNIT_ASSET.Connect(); # connect to google
# CONVERT GSHEET AND SORT BY 'IP'
sheet = UNIT_ASSET.GET(handle)
sheet = UNIT_ASSET.CONVERT_JSON_BY_HEADER(sheet, '_automationId')
for k in list(sheet.keys()):
	if sorted(list(sheet[k].keys())) == ['Row', '_automationId']: del sheet[k]; continue
	# if sheet[k]['Device 1'] == 'N12U' and 'Device 2' not in sheet[k].keys(): pass
	# else: del sheet[k]
#    "Device 1": "N12U",
#    "Port 1": "S9P7",
#    "Row": 28,
#    "WireOnce Device": "lepton01",
#    "WireOnce Port1": "1.15",

# Connect to Velocity <class>
V = velocity.VELOCITY(wc.argv_dict['IP'], user=wc.argv_dict['user'], pword=wc.argv_dict['pass'])
V.GetInventory()
# CreateConnections
for row in sheet.keys():
	try:
		device = sheet[row]['Device 2']
		port = sheet[row]['Port 2']
	except KeyError:
		pass
	if 'WireOnce Device' in sheet[row].keys() and 'WireOnce Port1' in sheet[row].keys():
		if sheet[row]['WireOnce Device'] != '' and sheet[row]['WireOnce Port1'] != '':
			device = sheet[row]['WireOnce Device']
			port = sheet[row]['WireOnce Port1']
	# wc.pairprint(device + '  ' + port, sheet[row])
	V.CreateConnection(sheet[row]['Device 1'], sheet[row]['Port 1'], device, port)
	
exit(0)

