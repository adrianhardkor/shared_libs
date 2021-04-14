#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
import re
import jinja2
import time

class mHANDLE():
	def __init__(self, flaskIP, flaskPort):
		self.flaskIP = flaskIP
		self.flaskPort = flaskPort
		self.url = 'http://%s:%s' % (self.flaskIP, self.flaskPort)
		self.__name__ = 'mHANDLE'
	def GetRun(self, myID):
		data = json.loads(wc.REST_GET(self.url + '/runner?runId=' + str(myID)))
		return(data)
	def UpdateRun(self, myID, data):
		payload = self.GetRun(myID)
		if payload == {}:
			payload = {'stdout_lines': [data]}
			payload['runId'] = myID
			data = json.loads(wc.REST_POST(self.url + '/runner?runId=' + str(myID), verify=False, args=payload, convert_args=True))
		else:
			payload[myID]['runId'] = myID
			payload[myID]['stdout_lines'].append(data)
			data = json.loads(wc.REST_PUT(self.url + '/runner?runId=' + str(myID), verify=False, args=payload[myID], convert_args=True))
		return(data)
	def PutRun(self, myID, payload):
		current = self.GetRun(myID)
		payload['runId'] = myID
		if current == {}:
			data = json.loads(wc.REST_POST(self.url + '/runner?runId=' + str(myID), verify=False, args=payload, convert_args=True))
		else:
			data = json.loads(wc.REST_PUT(self.url + '/runner?runId=' + str(myID), verify=False, args=payload, convert_args=True))
		return(data)

MH = mHANDLE(flaskIP='10.88.48.21', flaskPort='5000')
# wc.pairprint('before', MH.GetRun('docsisSched_25'))
# wc.pairprint('update1', MH.UpdateRun('docsisSched_25', {'stdout_lines': ["1","2","a","A",'_']}))
wc.pairprint('update2', MH.UpdateRun('docsisSched_25', time.ctime(time.time())))

