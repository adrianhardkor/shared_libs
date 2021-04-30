#!/usr/bin/env python3
# Skinny class handler
import wcommon as wc
import os
import json

class MEDIC():
	def __init__(self, IP, email, pword):
		self.IP = IP
		self.email = email
		self.pword = pword
		headers= {'Authorization': 'Basic'}
		self.__name__ = 'MEDIC'
	def GetModemDetail(self, cmac):
		cmac = cmac.replace(':', '').replace('.','').lower()
		cmac = ':'.join([cmac[0:2],cmac[2:4],cmac[4:6],cmac[6:8],cmac[8:10],cmac[10:12]])
		args = {'macaddress': cmac}
		data = json.loads(wc.REST_POST('https://' + self.IP + '/api/v1/cablemodem/modemdetail', user=self.email, pword=self.pword, verify=False, args=args, convert_args=True))
		return(data)

C = MEDIC(IP=wc.argv_dict['IP'], email=wc.argv_dict['email'], pword=wc.argv_dict['pass'])
wc.jd(C.GetModemDetail(wc.argv_dict['cmac']))

