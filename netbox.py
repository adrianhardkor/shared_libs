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
		self.tenants = {}
	def REST_POST(self, url):
		if '?' in url: _CHAR = '&'
		else: _CHAR = '?'
		return(requests.post(self.IP + url, headers=self.headers, verify=False).json())
	def REST_GET(self, url):
		if '?' in url: _CHAR = '&'
		else: _CHAR = '?'
		return(requests.get(self.IP + url, headers=self.headers, verify=False).json())
	def ChangeIPAM(self, tenant_name, ip_cidr,name):
		# if name not in Inventory - Unverified
		data = {'address': ip_cidr, 'tenant': ,nametenant_name, 'dns_name':}		# if name not in Inventory - Unverified
		
{
  "address": "10.88.240.250/32",
  "tenant": 0,
  "status": "active"0
  "role": "management",
  "dns_name": "test1_unverified",
  "description": "test1_unverified"
}
	
	def GetIPAM(self, tenant_name):
		self.IPAM = self.REST_GET('/api/ipam/ip-addresses/?tenant=' + tenant_name)['results']
		wc.jd(self.IPAM)
	def GetInventory(self, tenant_name):
		self.INV = self.REST_GET('/api/dcim/devices/?tenant=' + tenant_name)['results']
		wc.jd(self.INV)
		

N = NETBOX(wc.env_dict['NETBOX'], wc.env_dict['NETBOX_USER'], wc.env_dict['NETBOX_TOKEN'])
# N.GetInventory('arc-lab')
N.GetIPAM('arc-lab')

