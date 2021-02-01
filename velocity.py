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
				return(INV[r['topologyName']])
	def GetScripts(self):
		for script in VELOCITY.REST_GET(self, '/ito/repository/v1/scripts')['content']:
			wc.jd(script)
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
			out[t['name']] = t
			if t['id'] in activeRes.keys():
				out[t['name']]['activeRes'] = activeRes[t['id']]
				for resource in VELOCITY.REST_GET(self, '/velocity/api/topology/v12/topology/%s/resources' % t['id'])['items']:
					if resource['parentName'] == None:
						out[t['name']]['resources'][resource['name']] = resource
					else:
						out[t['name']]['resources'][resource['parentName'] + '||' + resource['name']] = resource

				out[t['name']]['activeRes']['creatorId'] = users[out[t['name']]['activeRes']['creatorId']]['display']
				out[t['name']]['activeRes']['ownerId'] = users[out[t['name']]['activeRes']['ownerId']]['display']
			out[t['name']]['creatorId'] = users[out[t['name']]['creatorId']]['display']
			out[t['name']]['lastModifierId'] = users[out[t['name']]['lastModifierId']]['display']
		return(out)
	def ApplyReservationTopology(top, out, pg, ports, p, device):
		ports[p['name']]['lockUtilizationType'] = p['lockUtilizationType']
		ports[p['name']]['connectedPortParentName'] = p['connectedPortParentName']
		ports[p['name']]['connectedPortParentId'] = p['connectedPortParentId']
		ports[p['name']]['connectedPortName'] = p['connectedPortName']
		ports[p['name']]['connectedPortId'] = p['connectedPortId']
		for t in top.keys():
			# t = topology_name
			for resource in top[t]['resources'].keys():
				# resource = 'name'
				activeRes = {
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
				if device['name'] == resource:
					# Reserved Device
					out[device['name']]['activeRes'] = activeRes
				elif '||'.join([device['name'], p['name']]) == resource:
					# Reserved Port on Device
					ports[p['name']]['activeRes'] = activeRes
				# wc.jd(p)
				if p['connectedPortParentName'] in out.keys():
					# bi-directional mapping for devices
					out[p['connectedPortParentName']]['activeRes'] = activeRes
					if p['connectedPortName'] in out[p['connectedPortParentName']]['ports'].keys():
						# reserved device and port exists
						out[p['connectedPortParentName']]['ports'][p['connectedPortName']]['activeRes'] = activeRes
		return(out,ports)
	def GetInventory(self):
		out = {}
		top = VELOCITY.GetTopologies(self)
		data = VELOCITY.REST_GET(self, '/velocity/api/inventory/v13/devices', params={'includeProperties':True, 'includePortGroups': True})
		for device in data['devices']:
			if device['id'] not in out.keys():
				out[device['name']] = {'ports': {}}
			out[device['name']]['id'] = device['id']
			for prop in device['properties']:
				out[device['name']][prop['name']] = prop['value']
			for pg in device['portGroups']:
				if pg['id'] != None:
					ports = {}
					# wc.pairprint(device['id'], device['name'] + '\t' + str(pg['id']))
					pp = VELOCITY.REST_GET(self, '/velocity/api/inventory/v13/device/%s/port_group/%s' % (str(device['id']), str(pg['id'])), params={'includeProperties':True})
					for p in pp['ports']:
						# wc.pairprint(device['name'], p['name'] + '\t' + p['templateId'])
						# template = VELOCITY.REST_GET(self, '/velocity/api/inventory/v13/template/%s/ports' % p['templateId'])
						# wc.jd(template)
						ports[p['name']] = {'pgName': pg['name'], 'pgId': pg['id'], 'id':p['id'],'linkChecked':time.ctime(p['linkChecked'])}
						for PortProp in p['properties']:
							ports[p['name']][PortProp['name']] = PortProp['value']
						if p['isLocked']:
							out,ports = VELOCITY.ApplyReservationTopology(top, out, pg, ports, p, device)
						# wc.pairprint(p['name'], pg['ports'][p['name']])
					out[device['name']]['ports'] = ports
		return(out)

V = VELOCITY(wc.argv_dict['IP'], user=wc.argv_dict['user'], pword=wc.argv_dict['pass'])
# V.GetScripts()
# V.GetAgentReservation('cecf3f52-fc19-4d3c-9e58-7bf8c5975290')
INV = V.GetInventory(); # device ipAddress
wc.jd(INV)
# wc.jd(V.GetTopologies())
# https://10.88.48.31/velocity/inventory/resources/14a1dc9b-3347-4396-bb38-eb4ede1a30c4/ports/6ae2b408-7b9f-42d3-800d-a3cb23d7d70e/properties

# page 51-52 on 8.3.0 api ref -- create port (DRIVER)
# 59 to edit: body {'properties': [{'definitionId':prop_uuid,'value':value}]}

  "properties": [
    {
      "availableValues": null,
      "definitionId": "b395be08-5628-4f68-b069-42d6cf7ec466",
      "description": "System port number. Example: 1.1.1",
      "groupName": "System Identification",
      "isRequired": true,
      "name": "portNumber",
      "type": "TEXT",
      "value": "1/7"
    },
    {
      "availableValues": null,
      "definitionId": "f828c9cd-e6db-4f93-b147-386dccd95e98",
      "description": "Unit of Measure:  Mbps",
      "groupName": "System Identification",
      "isRequired": false,
      "name": "Port Speed",
      "type": "INTEGER",
      "value": "100000"
    },
    {
      "availableValues": null,
      "definitionId": "52b1cb81-9a4b-44aa-83d2-3320fb10d12c",
      "description": "Example: Ethernet, Fast Ethernet, Copper..., etc",
      "groupName": "System Identification",
      "isRequired": false,
      "name": "Port Type",
      "type": "TEXT",
      "value": "Ethernet"
    }
  ],


