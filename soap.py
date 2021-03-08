#!/usr/bin/env python
import time
import os
import sys
import wcommon as wc
import json
import re
from suds.client import Client

class SOAP():
	def __init__(self, IP, rduHost, user, pword):
		self.user = user
		self.pword = pword
		self.IP = IP
		self.client = Client('http://%s:9100/cp-ws-prov/provService?wsdl' % IP)
		print('http://%s:9100/cp-ws-prov/provService?wsdl' % IP)
		raw_login = self.client.service.createSession(username=self.user, password=self.pword, rduHost=rduHost, rduPort='49187')
		print('\n\n')
		print(raw_login)
		# , username=self.user, password=self.pword, rduHost=self.IP, rduPort='49187'
		self.__name__ = 'SOAP'
	def GET_MODEMS(self, macAddressPattern = '*'):
		# DeviceSearchByDeviceIdPatternType
		d = {'macAddressPattern': macAddressPattern}
		result = self.client.service.DeviceSearchByDeviceIdPatGternType(**d)
		print(result)

S = SOAP(wc.argv_dict['PWS'], wc.argv_dict['RDU'], wc.argv_dict['user'], wc.argv_dict['pass'])
S.GET_MODEMS()

