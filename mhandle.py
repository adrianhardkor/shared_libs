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
		self.payload = {}
	def GetRun(self, myID):
		data = json.loads(wc.REST_GET(self.url + '/runner?runId=' + str(myID)))
		return(data)
	def UpdateRun(self, myID, preamble, data, ForceUpdate=False):
		potential = {}
		if self.payload == {} or ForceUpdate == True:
			# diff call-class will re-init self.payload
			potential = self.GetRun(myID)
			if myID in potential.keys():
				self.payload[myID] = potential[myID]
				wc.pairprint('[INFO] update:' + str(ForceUpdate) + str(myID), str(potential.keys()))
				# wc.jd(self.payload[myID])
		if myID not in self.payload.keys():
			# NEW POST
			self.payload[myID] = {'stdout_lines': [str(time.ctime(time.time())), str(potential), 'ForceUpdate:' + str(ForceUpdate), str(preamble) + str(data)]}
			self.payload[myID]['runId'] = myID
			data = json.loads(wc.REST_POST(self.url + '/runner?runId=' + str(myID), verify=False, args=self.payload[myID], convert_args=True))
		else:
			# APPEND
			# Updater works if providing an additional str(log) or list(of logs)
			if type(data) == str:
				if 'stdout_lines' not in self.payload[myID].keys(): wc.jd(self.payload[myID])
				self.payload[myID]['stdout_lines'].append(str(preamble) + str(data))
			elif type(data) == list:
				for d in data:
					self.payload[myID]['stdout_lines'].append(str(preamble) + str(d))
			data = json.loads(wc.REST_PUT(self.url + '/runner?runId=' + str(myID), verify=False, args=self.payload[myID], convert_args=True))
		return(data)
	def PutRun(self, myID, payload):
		current = self.GetRun(myID)
		payload['runId'] = myID
		if current == {}:
			data = json.loads(wc.REST_POST(self.url + '/runner?runId=' + str(myID), verify=False, args=payload, convert_args=True))
		else:
			data = json.loads(wc.REST_PUT(self.url + '/runner?runId=' + str(myID), verify=False, args=payload, convert_args=True))
		return(data)
	def _LOGGER(self, data, timestamp=True, ForceUpdate=False):
		global who
		global runId
		try:
			self.who = who
			self.runId = runId
		except Exception:
			pass
		if timestamp: preamble = '[%s @ %s] ' % (self.who, str(time.ctime(time.time())).split(' ')[-2])
		else: preamble = ''
		self.UpdateRun(self.runId, preamble, data, ForceUpdate=ForceUpdate)
	def _UPLOAD(self, fname):
		data = wc.REST_UPLOAD(self.url + '/upload', fname)
		return(data)

# MH = mHANDLE(flaskIP='10.88.48.21', flaskPort='5000')
# wc.jd(dir(MH))
# wc.jd(MH._UPLOAD('adrian.csv'))

