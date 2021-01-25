#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
# wc.jenkins_header(); # load inputs from Jenkinsfile
# wc.jd(wc.wcheader)
import time

class VELOCITY():
	def __init__(self, IP, user='', pword='', token=''):
		self.__name__ = 'VELOCITY'
		self.V = 'https://' + str(IP)
		if user != '' and pword != '':
			self.user = user
			self.pword = pword
			self.TOKEN = json.loads(wc.REST_GET(self.V + '/velocity/api/auth/v2/token', user=self.user, pword=self.pword))['token']
		elif token != '':
			self.TOKEN = token
		else:
			print('Failed: VELOCITY No U/P or TOKEN provided!')
			exit(5)
	def REST_GET(self, url, params={}):
		# print('\t' + self.V + url)
		# page = '1'
		# while page is ''
		# url = url + '?offset={offset}&limit={limit}&filter={filter}' == MAX 200 then OFFSET
		url = url + '?limit=200'
		headers = {"X-Auth-Token": self.TOKEN}
		headers['Content-Type'] = headers['Accept'] = 'application/json'
		# print(headers)
		data = json.loads(wc.REST_GET(self.V + url, headers=headers, params=params))
		return(data)
	def GetAgentReservation(self, resvId):
		# if has resvId then already reserved
		# if has topId then script requires reservation PUT/POST?
		INV = VELOCITY.GetTopologies(self)
		for r in VELOCITY.REST_GET(self, '/velocity/api/reservation/v16/reservations', params={'filter': 'status::ACTIVE'})['items']:
			if r['id'] == resvId:
				return(INV[r['topologyId']])
	def GetScripts(self):
		for script in VELOCITY.REST_GET(self, '/ito/repository/v1/scripts')['content']:
			if not script['driver']:
				wc.pairprint(script['fullPath'], script['guid'])
	def GetUsers(self):
		# /velocity/api/user/v9/profiles
		out = {}
		for p in VELOCITY.REST_GET(self, '/velocity/api/user/v9/profiles')['profiles']:
			out[p['id']] = p
			out[p['id']]['display'] = "%s (%s)" % (p['name'], p['login'])
		return(out)
	def GetTopologies(self):
		out = {}
		top = VELOCITY.REST_GET(self, '/velocity/api/topology/v12/topologies')['topologies']
		res = VELOCITY.REST_GET(self, '/velocity/api/reservation/v16/reservations', params={'filter': 'status::ACTIVE'})['items']
		users = VELOCITY.GetUsers(self)
		activeRes = {}
		for r in res:
			# topology-oriented, for both active and non
			r['start'] = time.ctime(r['start'])
			r['end'] = time.ctime(r['end'])
			activeRes[r['topologyId']] = r
		for t in top:
			t['resources'] = {}
			t['activeRes'] = {}
			out[t['id']] = t
			if t['id'] in activeRes.keys():
				out[t['id']]['activeRes'] = activeRes[t['id']]
				for resource in VELOCITY.REST_GET(self, '/velocity/api/topology/v12/topology/%s/resources' % t['id'])['items']:
					out[t['id']]['resources'][resource['id']] = resource

				out[t['id']]['activeRes']['creatorId'] = users[out[t['id']]['activeRes']['creatorId']]['display']
				out[t['id']]['activeRes']['ownerId'] = users[out[t['id']]['activeRes']['ownerId']]['display']
			out[t['id']]['creatorId'] = users[out[t['id']]['creatorId']]['display']
			out[t['id']]['lastModifierId'] = users[out[t['id']]['lastModifierId']]['display']
		return(out)
	def ApplyReservationTopology(top, out, pg, p):
		pg['ports'][p['name']]['lockUtilizationType'] = p['lockUtilizationType']
		pg['ports'][p['name']]['connectedPortParentName'] = p['connectedPortParentName']
		pg['ports'][p['name']]['connectedPortParentId'] = p['connectedPortParentId']
		pg['ports'][p['name']]['connectedPortName'] = p['connectedPortName']
		pg['ports'][p['name']]['connectedPortId'] = p['connectedPortId']
		for t in top.keys():
			for resource in top[t]['resources'].keys():
				if p['id'] == top[t]['resources'][resource]['inventoryResourceId']:
					# IF device !OR! port ID exists in RESOURCES of ACTIVE-RES TOPOLOGIES
					pg['ports'][p['name']]['activeRes'] = {
						'name': top[t]['activeRes']['name'],
						'id': top[t]['activeRes']['id'],
						'start': top[t]['activeRes']['start'],
						'end': top[t]['activeRes']['end'],
						'topologyId': top[t]['activeRes']['topologyId'],
						'topologyName': top[t]['activeRes']['topologyName'],
						'ownerId': top[t]['activeRes']['ownerId'],
						'description': top[t]['activeRes']['description'],
						'creatorId': top[t]['creatorId'],
						'descriptionTopology': top[t]['description']
					}
					# Cross-Ref for any wire-once ports (velocity doesnt include wire-once as reservation-resources by default)
#					if p['connectorPortParentId'] in out.keys():
#						out[p['connectedPortId']]['activeRes'] = pg['ports'][p['name']]['activeRes']
#					else:
#						pass
					
		return(out,pg)
	def GetInventory(self):
		out = {}
		top = VELOCITY.GetTopologies(self)
		data = VELOCITY.REST_GET(self, '/velocity/api/inventory/v13/devices', params={'includeProperties':True, 'includePortGroups': True})
		for device in data['devices']:
			if device['id'] not in out.keys():
				out[device['id']] = {'portGroups':[]}
			out[device['id']]['name'] = device['name']
			for prop in device['properties']:
				out[device['id']][prop['name']] = prop['value']
			wc.pairprint(device['name'], out[device['id']])
			for pg in device['portGroups']:
				if pg['id'] != None:
					pg['ports'] = {}
					# wc.pairprint(device['id'], device['name'] + '\t' + str(pg['id']))
					# wc.jd(VELOCITY.REST_GET(self, '/inventory/v13/device/%s/port_group/%s' % (str(device['id']), str(pg['id']))))
					pp = VELOCITY.REST_GET(self, '/velocity/api/inventory/v13/device/%s/port_group/%s' % (str(device['id']), str(pg['id'])))
					for p in pp['ports']:
						pg['ports'][p['name']] = {'id':p['id'],'linkChecked':time.ctime(p['linkChecked'])}
						if p['isLocked']:
							out,pg = VELOCITY.ApplyReservationTopology(top, out, pg, p)
						# pg['ports'][p['name']] = p
						# wc.pairprint(p['name'], pg['ports'][p['name']])
					out[device['id']]['portGroups'].append(pg)
		return(out)

# V = VELOCITY(wc.argv_dict['IP'], user=wc.argv_dict['user'], pword=wc.argv_dict['pass'])
# V.GetScripts()
# V.GetAgentReservation('cecf3f52-fc19-4d3c-9e58-7bf8c5975290')
# wc.jd(V.GetInventory())
# wc.jd(V.GetTopologies())

