#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
import re
import jinja2

class mHANDLE():
	def __init__(self, flaskIP, flaskPort):
		self.flaskIP = flaskIP
		self.flaskPort = flaskPort
		self.url = 'http://%s:%s' % (self.flaskIP, self.flaskPort)
		self.__name__ = 'mHANDLE'
	def GetRun(self, myID):
		data = json.loads(wc.REST_GET(self.url + '/vAgent?runId=' + str(myID)))
		return(data)
	def PutRun(self, myID, payload):
		current = self.GetRun(myID)
		if current == {}:
			data = json.loads(wc.REST_POST(self.url + '/vAgent?runId=' + str(myID), verify=False, args=payload, convert_args=True))
		else:
			data = json.loads(wc.REST_PUT(self.url + '/vAgent?runId=' + str(myID)))
		return(data)
	def delDevice(self, cmac):
		data = runner(self.PATH, 'delDevice', 'http://%s:9100/cp-ws-prov/provService' % self.PWS, args={'sessionId':self.sessionId, 'cmac':cmac})
		# wc.jd(data)
		return(data)




import Mongo
try:
	Mongo.TryDeleteDocuments(Mongo.vAgent)
except Exception as err:
	wc.pairprint('err',err)

MH = mHANDLE(flaskIP='10.88.48.21', flaskPort='5000')
wc.jd(MH.GetRun('docsisSched_25'))
wc.jd(MH.PutRun('docsisSched_25', {'stdout_lines': ["1","2","a","A",'_']}))
wc.jd(MH.GetRun('docsisSched_25'))
