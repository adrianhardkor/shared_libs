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
		# page = '1'
		# while page is ''
		# url = url + '?offset={offset}&limit={limit}&filter={filter}' == MAX 200 then OFFSET
		url = url + '?limit=200'
		data = json.loads(wc.REST_GET(self.V + url, user=self.user, pword=self.pword, params=params))
		return(data)
	def GetTopologies(self):
		top = VELOCITY.REST_GET(self, '/topology/v12/topologies')['topologies']
		out = {}
		for t in top:
			out[t['id']] = t
		return(out)
	def GetInventory(self):
		top = VELOCITY.GetTopologies(self)
		out = {}
		data = VELOCITY.REST_GET(self, '/inventory/v13/devices', params={'includeProperties':True, 'includePortGroups': True})
		for device in data['devices']:
			out[device['id']] = {'name': device['name'], 'portGroups':[]}
			wc.pairprint(device['name'], out[device['id']])
			for prop in device['properties']:
				out[device['id']][prop['name']] = prop['value']
			wc.pairprint(device['id'], out[device['id']])
			for pg in device['portGroups']:
				if pg['id'] != None:
					pg['ports'] = {}
					# wc.pairprint(device['id'], device['name'] + '\t' + str(pg['id']))
					# wc.jd(VELOCITY.REST_GET(self, '/inventory/v13/device/%s/port_group/%s' % (str(device['id']), str(pg['id']))))
					pp = VELOCITY.REST_GET(self, '/inventory/v13/device/%s/port_group/%s' % (str(device['id']), str(pg['id'])))
					for p in pp['ports']:
						pg['ports'][p['name']] = {'id':p['id'],'linkChecked':time.ctime(p['linkChecked'])}
						if p['isLocked']:
							pg['ports'][p['name']]['lockUtilizationType'] = p['lockUtilizationType']
							pg['ports'][p['name']]['connectedPortParentName'] = p['connectedPortParentName']
							pg['ports'][p['name']]['connectedPortParentId'] = p['connectedPortParentId']
							pg['ports'][p['name']]['connectedPortName'] = p['connectedPortName']
							pg['ports'][p['name']]['connectedPortId'] = p['connectedPortId']
						pg['ports'][p['name']] = p
						# wc.pairprint(p['name'], pg['ports'][p['name']])
					out[device['id']]['portGroups'].append(pg)
		return(out)

V = VELOCITY(wc.argv_dict['IP'], wc.argv_dict['user'], wc.argv_dict['pass'])
wc.jd(V.GetInventory())
wc.jd(V.GetTopologies())
exit(0)

