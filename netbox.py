#!/usr/bin/env python3
import time
import os
import sys
import wcommon as wc
import json
import re
import requests



class NETBOX():
	def __init__(self, IP, user, token):
		self.user = user
		self.token = token
		self.headers = {  
			'Content-Type': 'application/json',
			'Accept': 'application/json',
			'Authorization': 'Token ' + str(self.token)
		} 
		self.IP = 'https://' + IP
		self.__name__ = 'NETBOX'
	def REST_GET(self, url):
		if '?' in url: _CHAR = '&'
		else: _CHAR = '?'
		return(requests.get(self.IP + url, headers=self.headers, verify=False).json())
	def GetInventory(self, tenant_name):
		self.INV = self.REST_GET('/api/dcim/devices/?tenant=' + tenant_name)['results']
		wc.jd(self.INV)

N = NETBOX(wc.env_dict['NETBOX'], wc.argv_dict['user'], wc.argv_dict['pass'])
N.GetInventory('arc-lab')

