#! /usr/bin/env python3
import wcommon as wc
import os
import json
from requests import Session
import hmac
import hashlib


class NCS():
	def __init__(self, host, key, secret_hmac):
		self.host = host
		self.key = key
		self.secret_hmac = secret_hmac
		self.url = 'https://' + self.host + '/json.pl'
		self.headers = {'HMAC': self.secret_hmac, 'KEY': self.key}
	def make_digest(self, message, key):
		key	 = bytes(key, 'UTF-8')
		message = bytes(message, 'UTF-8')
		digester = hmac.new(key, message, hashlib.sha1)
		return(digester.hexdigest())
	def REST_POST(self, endpoint, args={}):
		s = Session()
		base_api_url = self.url + endpoint
		json_payload = json.dumps(args)
		hmac_key = self.secret_hmac
		digest = self.make_digest(self.url + endpoint, hmac_key)
		self.headers['HMAC'] = digest
		wc.jd(self.headers)
		data = s.post(self.url + endpoint, headers=self.headers, json=json_payload)
		return(data.json())
	def GetInventory(self, site_location_id):
		data = self.REST_POST('/multiplexers/list', args={'criteria':{'site_location_id':{'operator':'=','data':str(site_location_id)}}})
		return(data)

key = '3b4fc64446838561fdef78d18f6e963f'
myhmac = 'b4814b0cfbd19f032d3c61e282cbfa6f'
N = NCS('wow-sandbox.n-c-s.net', key=key, secret_hmac=myhmac)
wc.jd(N.GetInventory('61325'))


##!/usr/bin/python3
#from requests import Session
#import hmac
#import hashlib
#import json
#def make_digest(message, key):
#	key	 = bytes(key, 'UTF-8')
#	message = bytes(message, 'UTF-8')
#	digester = hmac.new(key, message, hashlib.sha1)
#	sig = digester.hexdigest()
#	return sig
#s = Session()
#base_api_url = "https://portal-sandbox.genband.com:443/api/rest/3.42/"
#json_payload = "{}"
#hmac_key = 'key-goes-here'
#digest = make_digest(json_payload, hmac_key)
#headers = {
#		'X-Group-ID'	: 'group-id',
#		'X-User-ID'	 : 'user-id',
#		'X-User-Token'  : 'token-here',
#		'X-Hmac'		 : digest
#}
#url = base_api_url + "path/to/method"
#ret = s.get(url, headers=headers, json={})

