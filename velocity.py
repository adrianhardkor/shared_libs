#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
# wc.jenkins_header(); # load inputs from Jenkinsfile
# wc.jd(wc.wcheader)
import time

class VELOCITY():
	def __init__(self, IP, user, pword):
		self.user = user
		self.pword = pword
		self.V = 'https://%s/velocity/api' % str(IP)	
		self.__name__ = 'VELOCITY'
	def REST_GET(self, url, params={}):
		# print('\t' + self.V + url)
		return(json.loads(wc.REST_GET(self.V + url, user=self.user, pword=self.pword, params=params)))
	def GetInventory(self):
		out = {}
		data = VELOCITY.REST_GET(self, '/inventory/v13/devices', params={'includeProperties':True, 'includePortGroups': True})
		for device in data['devices']:
			wc.pairprint(device['id'], device['name'])
			out[device['id']] = {'name': device['name'], 'portGroups':[]}
			for prop in device['properties']:
				out[device['id']][prop['name']] = prop['value']
			for pg in device['portGroups']:
				if pg['id'] != None:
					out[device['id']]['portGroups'].append(pg)
					# wc.pairprint(device['id'], device['name'] + '\t' + str(pg['id']))
					# wc.jd(VELOCITY.REST_GET(self, '/inventory/v13/device/%s/port_group/%s' % (str(device['id']), str(pg['id']))))
					for p in VELOCITY.REST_GET(self, '/inventory/v13/device/%s/port_group/%s' % (str(device['id']), str(pg['id'])))['ports']:
						o = ['  ', p['name'], p['id'], time.ctime(p['linkChecked'])]
						if p['isLocked']:
							o.append(p['lockUtilizationType'])
							o.append(p['connectedPortParentName'])
							o.append(p['connectedPortParentId'])
							o.append(p['connectedPortName'])
							o.append(p['connectedPortId'])
						wc.listprint('  ', o)
		return(out)
		# wc.jd(data)

V = VELOCITY(wc.argv_dict['IP'], wc.argv_dict['user'], wc.argv_dict['pass'])
V.GetInventory()
# wc.jd(V.REST_GET('/inventory/v13/devices'))
exit(0)
