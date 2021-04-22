#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
import re
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
	def UpdateRun(self, myID, preamble, data):
		payload = self.GetRun(myID)
		if payload == {}:
			payload = {'stdout_lines': [time.ctime(time.time()), preamble + data]}
			payload['runId'] = myID
			data = json.loads(wc.REST_POST(self.url + '/runner?runId=' + str(myID), verify=False, args=payload, convert_args=True))
		else:
			payload[myID]['runId'] = myID
			# Updater works if providing an additional str(log) or list(of logs)
			if type(data) == str: payload[myID]['stdout_lines'].append(preamble + data)
			elif type(data) == list:
				for d in data:
					payload[myID]['stdout_lines'].append(preamble + str(d))
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
	def _LOGGER(self, data, timestamp=True):
		global who
		global runId
		try:
			self.who = who
			self.runId = runId
		except Exception:
			pass
		if timestamp: preamble = '[%s @ %s] ' % (self.who, str(time.ctime(time.time())).split(' ')[-2])
		else: preamble = ''
		self.UpdateRun(self.runId, preamble, data)
	def _UPLOAD(self, fname):
		data = wc.REST_UPLOAD(self.url + '/upload', fname)
		return(data)

# MH = mHANDLE(flaskIP='10.88.48.21', flaskPort='5001')
# wc.jd(MH._UPLOAD('adrian.log'))

